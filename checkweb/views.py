from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.utils import timezone
from django.contrib.auth.decorators import login_required


from django.db.models.functions import TruncDay

import pytz
from checkweb.models import *
from checkweb.functions.compare_snapshots import Comparator

from random import choice, randint
from string import ascii_lowercase

# Create your views here.
def index(request):
    html = "<html><body>It is now %s.</body></html>" % timezone.now()

    return HttpResponse(html)


def dashboard(request):
    template = loader.get_template('dashboard.html')

    monitored_urls = WatchUrl.objects.filter(active_monitor=True).count()
    active_disabled_urls = int(monitored_urls / WatchUrl.objects.all().count()*100)
    last24h = timezone.datetime.now() - timezone.timedelta(days=1)
    last7d = timezone.datetime.now() - timezone.timedelta(days=7)
    snapshots_24_7 = [Snapshot.objects.filter(created__gte=last24h,watchurl__active_monitor=True ).count(),
                   Snapshot.objects.filter(created__gte=last7d,watchurl__active_monitor=True ).count()]
    alerts_24_7 = [Alert.objects.filter(created__gte=last24h,watchurl__active_monitor=True).count(),
                   Alert.objects.filter(created__gte=last7d,watchurl__active_monitor=True).count()]


    group_dict = dict()
    #for watch_obj in WatchUrl.objects.filter(active_monitor=True).values('id','domain'):
    #    group_dict[watch_obj.get('id')] = str(watch_obj.get('domain')or "")\
    #        .replace("//","+:;+").replace("/","/<br>").replace("?","?<br>").replace("&","&<br>").replace("+:;+","//")

    url_backlog = []
    group_list  = [] # this list keep order, similar dict used in code for lookup
    for watch_obj in Snapshot.objects.filter(watchurl__active_monitor=True).order_by('watchurl').values('id','access_url'):
        if watch_obj.get('access_url') not in url_backlog:
            url_backlog.append(watch_obj.get('access_url'))
            group_dict[watch_obj.get('id')] = str(watch_obj.get('access_url') or "")
            group_list.append([watch_obj.get('id'),str(watch_obj.get('access_url') or "")])



    event_graph_dctlst = []
    id_counter = 0
    for snaps_event in Snapshot.objects.filter(watchurl__active_monitor=True).order_by("-created"):
        event_graph_dctlst.append({'id':id_counter,
                                   'group':list(group_dict.keys())[list(group_dict.values()).index(snaps_event.access_url)],
                                   'content':'{} ({})'.format(snaps_event.http_status_last,
                                                                            snaps_event.html_dump_size_readable()),
                                   'start': snaps_event.created.astimezone(tz=pytz.timezone('Europe/Amsterdam')).strftime("%Y-%m-%d %H:%M:%S"),
                                   'type': 'box'
                                   })
        id_counter += 1

    for alert_event in Alert.objects.filter(watchurl__active_monitor=True).order_by("-created"):
        if " content " in alert_event.message_short:
            content_variable = '<a href=/checkweb/content_diff?id={} target="_blank"><font color="red">Alert: {}</font></a>'.format(alert_event.id, alert_event.message_short.replace("'",""))
        else:
            content_variable = '<font color="red">Alert: {}</font>'.format(alert_event.message_short.replace("'",""))

        #utc_to_local_dt = timezone.datetime.utcfrom(alert_event.created)
        event_graph_dctlst.append({'id':id_counter,
                                   'group':list(group_dict.keys())[list(group_dict.values()).index(alert_event.snapshot_current.access_url)],
                                   'content':content_variable,
                                   'start': alert_event.created.astimezone(tz=pytz.timezone('Europe/Amsterdam')).strftime("%Y-%m-%d %H:%M:%S"),
                                   'type': 'point'
                                   })
        id_counter += 1



    context = {'monitored_urls': monitored_urls,
            'active_disabled_urls':active_disabled_urls,
            'snapshots_24_7':snapshots_24_7,
            'alerts_24_7':alerts_24_7,
            'event_graph_dctlst':event_graph_dctlst,
            'group_list':group_list,
            'alerts_qs':Alert.objects.filter(watchurl__active_monitor=True,created__gte=last7d ).order_by("-created")}

    return HttpResponse(template.render(context, request))

def list_of_alerts():
    # alert
    return None

### detail views ###

@login_required(login_url="/admin/login/")
def htmldiffview(request):
    comparator_obj = Comparator(snapshot_obj=Snapshot.objects.get(id=request.GET.get('id')))
    retrieved_fromDiff = comparator_obj.generate_diff_file()

    context = {'main':retrieved_fromDiff}

    template = loader.get_template('show_diff.html')
    return HttpResponse(template.render(context, request))

@login_required(login_url="/admin/login/")
def test_reply(request):
    template = loader.get_template('test_reply.html')

    if request.GET.get('content'):
        context = {
            'text1': ''.join(choice(ascii_lowercase) for x in range(randint(100, 501))),
            'text2': ''.join(choice(ascii_lowercase) for x in range(randint(100, 501))),
        }
    else:
        context = {
            'text1': None,
            'text2': None,
        }

    if request.GET.get('status'):
        return HttpResponse(template.render(context, request),status=randint(100, 501))
    else:
        return HttpResponse(template.render(context, request))


