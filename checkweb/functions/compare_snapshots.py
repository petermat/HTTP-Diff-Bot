from checkweb.models import *
from django.contrib.auth.models import User
from django.utils import timezone
from difflib import SequenceMatcher
from django.core.mail import send_mail
from django.conf import settings
import os

#3rt party
from prettytable import PrettyTable
from bs4 import BeautifulSoup

import django
django.setup()

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

class Comparator:
    '''
    inp: snapshot object
    out: compared values, if crossing tresholds then alert
    '''

    def __init__(self, snapshot_obj):
        self.snapshot_obj = snapshot_obj

        # load previous snapshot, if not found terminate
        self.prev_snapshot = Snapshot.objects\
            .filter(access_url=self.snapshot_obj.access_url)\
            .exclude(id=self.snapshot_obj.id)\
            .order_by('id').last()

        if self.prev_snapshot and os.path.exists(self.prev_snapshot.html_dump.path):
            # calculate diff as summary and for treshold purposes

            m = SequenceMatcher(None, open(self.prev_snapshot.html_dump.path).read(), open(self.snapshot_obj.html_dump.path).read())
            self.diff_content_int = round(100 - (m.ratio() * 100), 2)
            logger.debug("\t[Comparator] DEBUG: Content diff is {}%".format(self.diff_content_int))

            # returns difference between fields:
            # resolved_ip,http_status_first,http_status_last, redirected_url
            # return {resolved_ip:{'current':111, 'previous': 112}}
            out_dict=dict()
            if self.snapshot_obj.resolved_ip != self.prev_snapshot.resolved_ip:
                out_dict['resolved_ip'] = {'current':self.snapshot_obj.resolved_ip,
                                      'previous': self.prev_snapshot.resolved_ip}

            if self.snapshot_obj.http_status_first != self.prev_snapshot.http_status_first:
                out_dict['http_status_first'] = {'current':self.snapshot_obj.http_status_first,
                                      'previous': self.prev_snapshot.http_status_first}

            if self.snapshot_obj.http_status_last != self.prev_snapshot.http_status_last:
                out_dict['http_status_last'] = {'current':self.snapshot_obj.http_status_last,
                                      'previous': self.prev_snapshot.http_status_last}

            if self.snapshot_obj.redirected_url != self.prev_snapshot.redirected_url:
                out_dict['redirected_url'] = {'current':self.snapshot_obj.redirected_url,
                                      'previous': self.prev_snapshot.redirected_url}
            self.diff_meta_dict =  out_dict
            logger.debug("\t[Comparator] DEBUG: Meta diff amount: {}, compating snapshots {} vs {}".format(len(self.diff_meta_dict),
                                self.prev_snapshot.id, self.snapshot_obj.id))

        else:
            self.diff_content_int = 0
            self.diff_meta_dict = dict()

    # main function - front-end
    def generate_diff_file(self):
        import subprocess

        if not self.prev_snapshot:
            logger.warning("[Comparator] ERROR: Previous snapshot not found, comparison skipped")
            return 0

        p1 = self.prev_snapshot.html_dump.path.lstrip('/')
        #os.path.join(settings.BASE_DIR ,self.prev_snapshot.html_dump.path)
        p2 = self.snapshot_obj.html_dump.path.lstrip('/')
        #os.path.join(settings.BASE_DIR, self.snapshot_obj.html_dump.path)
        out = subprocess.Popen(['/usr/local/bin/htmldiff', self.prev_snapshot.html_dump.path.lstrip('/'),
                                self.snapshot_obj.html_dump.path.lstrip('/')],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)


        stdout, stderr = out.communicate()
        logger.debug('DEBUG: Frontend:HTMLDiff comparing shapshots {} and {}'.format(
            self.prev_snapshot.id,
            self.snapshot_obj.id
        ))
        soup = BeautifulSoup(stdout.decode('utf-8'),features="html.parser")
        head_tag = soup.find('h1')
        #head_tag.name = 'h2'
        if head_tag:
            head_tag.string = 'Alert on changes: {}'.format(self.snapshot_obj.access_url)

        return soup.prettify()



    # not for direct use
    def generate_alert_object(self,alert_on_content_change=False, alert_on_meta_change=False):
        message_verbose,message_short = "",None

        metachange_html=None
        if alert_on_meta_change:
            x = PrettyTable()
            x.field_names = ["Changed field", "Previous value", "Current Value"]
            for part_dict in self.diff_meta_dict.items():
                x.add_row([part_dict[0], part_dict[1].get('previous'),part_dict[1].get('current')])
            metachange_html = x.get_html_string()

        if alert_on_content_change and alert_on_meta_change:
            # multi alert
            message_short = "Change in content of ({}% from {}) and metadata: {}".format(
                self.diff_content_int, self.snapshot_obj.html_dump_size_readable(),str(self.diff_meta_dict))
            message_verbose = metachange_html + self.generate_diff_file()
        else:
            if alert_on_content_change:
                # sinle alert - change of content
                message_short = "Change in content - {}% from total lenght {}".format(self.diff_content_int,self.snapshot_obj.html_dump_size_readable())
                message_verbose = self.generate_diff_file()

            if alert_on_meta_change:
                # single alert - change of meta
                message_short= "Change in metadata: {}".format(str(self.diff_meta_dict))
                message_verbose = metachange_html

        alert_obj = Alert(snapshot_current=self.snapshot_obj,
                          snapshot_previous=self.prev_snapshot,
                          message_short=message_short,
                          message_verbose=message_verbose,
                          watchurl=self.snapshot_obj.watchurl,)
        alert_obj.save()

        if alert_obj:
            logger.info("\t[Comparator] DEBUG: Alert {} from Snapshot {} saved. message_short: {}".format(
                alert_obj.id,self.snapshot_obj.id,message_short))

            if self.snapshot_obj.watchurl.active_email_alert:

                send_mail(subject="Domain Monitor Alert ["+self.snapshot_obj.access_url+']: '+message_short,# Subject here'
                          message='message is in html not plain, something wrong',
                          html_message=message_verbose,#self.generate_diff_file(),#Here is the message
                          from_email=getattr(settings,'DEFAULT_FROM_EMAIL', None), # From
                          recipient_list=[value['email'] for value in User.objects.filter(is_staff=True, is_active=True).values('email')],
                          fail_silently=not settings.DEBUG)


    # main function - backend
    def compare_and_alert(self):

        alert_on_content_change = False
        if self.diff_content_int > self.snapshot_obj.watchurl.treshold_change_percent:
            logger.info("\t[Comparator] DEBUG: Alerting on content change triggered ({}>{})".format(self.diff_content_int,
                                                                                              self.snapshot_obj.watchurl.treshold_change_percent))
            alert_on_content_change = True

        alert_on_meta_change = False
        if len(self.diff_meta_dict) > 0:
            logger.info("\t[Comparator] DEBUG: Alert on metadata triggered")
            alert_on_meta_change = True


        if alert_on_content_change or alert_on_meta_change:
            self.generate_alert_object(alert_on_content_change=alert_on_content_change, alert_on_meta_change=alert_on_meta_change)


