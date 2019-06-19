from django.core.management.base import BaseCommand
from checkweb.models import *
from django.utils import timezone
from django.conf import settings
from django.utils.text import slugify
import io, os, json
from socket import gethostbyname, gaierror, setdefaulttimeout
from random import choice
import ipaddress

# non-internals party
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from urllib3.exceptions import NewConnectionError, MaxRetryError

import tldextract


import django
django.setup()



def random_headers():
    desktop_agents = [
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0']
    return {'User-Agent': choice(desktop_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}


class Harvester:
    '''
    input: WathURL object
    output: list of snapshot_obj
    '''


    def __init__(self, watchUrl_obj):
        #self.urls_obj_qs = WatchUrl.objects.filter(active_monitor=True)
        self.watchUrl_obj = watchUrl_obj

        #def get_target_urls(self):
        print("\n[Harvester] INFO: Starting with: {0}; Description:'{1}'".format(self.watchUrl_obj.domain, self.watchUrl_obj.description))

        # return all combination of URLs
        if self.watchUrl_obj.active_discover_urls:
            # todo discover URLs and create snapshot for every one of them
            base_domain = self.watchUrl_obj.domain.replace('http://','').replace('https://','').lstrip('www.')


            self.targeturls_list =  ['http://' + base_domain,'https://' + base_domain,
                    'http://www.' + base_domain,'https://www.' + base_domain]
            print("\t[Harvester] DEBUG: URL Discovery ACTIVE. Target list={}".format(str(self.targeturls_list)))

        # URL discovery is off, domain will be used directly as URL
        else:
            print("\t[Harvester] DEBUG: URL Discovery disabled, progressing with only following URL: {0}".format(self.watchUrl_obj.domain))
            self.targeturls_list = [self.watchUrl_obj.domain,]

    def return_targets(self):
        return self.targeturls_list

    def process_url(self):
        session = requests.session()
        if self.watchUrl_obj.active_tor_proxy:
            session.proxies = {'http': 'socks5://127.0.0.1:9050',
                               'https': 'socks5://127.0.0.1:9050'}

        my_ipaddr, my_location = None, None
        try:
            my_ipaddr = session.get('https://api.ipify.org').text
            assert ipaddress.ip_address(my_ipaddr)
            location_json = json.loads(requests.get("http://extreme-ip-lookup.com/json/{}".format(my_ipaddr)).text)
            my_location = location_json.get('country') + ", " + location_json.get('city')
            print("\t[Harvester] DEBUG: My IP: {}, localized at '{}'".format(my_ipaddr, my_location))
        except Exception as Er:
            print("\t[Harvester] ERROR: My IP address resolution failed, reason:{}".format(Er))

        retun_objects=[]
        for url_suggested in self.targeturls_list:
            slug_name = slugify(url_suggested.lstrip("https").lstrip("http"))

            # resolve domain name to IP (including subdomain)
            urlex_obj = tldextract.extract(url_suggested)
            try:
                resolved_ip = gethostbyname('.'.join([urlex_obj.subdomain,urlex_obj.domain,urlex_obj.suffix]).strip('.'))
                print("\t[Harvester] DEBUG: IP Address resolved to {0} for: {1}".format(resolved_ip,url_suggested))

            except gaierror:
                resolved_ip = None
                print("[Harvester]  * WARNING: IP Address not resolved for: {}".format(url_suggested))

            if resolved_ip:
                try:
                    response = session.get(url_suggested, allow_redirects=True, verify=False, headers=random_headers())
                except Exception as Er:# (ConnectionError,TimeoutError,NewConnectionError,MaxRetryError):
                    print("[Harvester]  *** ERROR: ConnectionError to {} per '{}'".format(url_suggested, Er))
                    http_status_last = None
                    html_content = None
                    http_status_first = None
                    redirected_url = None
                else:
                    if response.history:
                        http_status_first = response.history[0].status_code
                        redirected_url = response.url

                        print("\t[Harvester] DEBUG: Redirections followed for: {}".format(url_suggested))
                    else:
                        http_status_first,redirected_url = None, None
                        print("\t[Harvester] DEBUG: No redirection followed for {}".format(url_suggested))

                    http_status_last = response.status_code
                    html_content = response.text
            else:
                http_status_first, http_status_last, redirected_url, html_content = None, None, None, None



            # save snapshot metadata
            snapshot_obj=Snapshot(watchurl=self.watchUrl_obj,my_ipaddr=my_ipaddr,my_location=my_location,
                     access_url=url_suggested,
                     resolved_ip=resolved_ip,
                     http_status_first=http_status_first,
                     http_status_last=http_status_last,
                     redirected_url=redirected_url,
                     html_content=html_content,
                     html_dump_size=len(str(html_content or "")),
                     )
            # save shapshot dump
            snapshot_obj.html_dump.save(
                    os.path.join(
                        slug_name,
                        timezone.now().strftime("%Y-%m-%d-%H-%M-%S")+".txt"),
                    io.StringIO(html_content)
                    )
            print("\t[Harvester] DEBUG: Values saved for {}\n".format(url_suggested))
            retun_objects.append(snapshot_obj)
        return retun_objects
