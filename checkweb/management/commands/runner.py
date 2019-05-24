from django.core.management.base import BaseCommand

from checkweb.models import *
from django.utils import timezone
from django.conf import settings
import os

from checkweb.functions.get_snapshots import Harvester
from checkweb.functions.compare_snapshots import Comparator

class Command(BaseCommand):
    help = """Runs thru all monitored domains"""

    #def add_arguments(self, parser):
    #    parser.add_argument(
    #        "-d",
    #        "--delete",
    #        help="Wipe out existing content before generating new.",
    #        action="store_true")

    def handle(self, *args, **options):

        #if options.get('delete'):
            # pass

        print("INFO: Runner Starting...")

        if WatchUrl.objects.filter(active_monitor=True).count() >0:
            for watch_url_obj in WatchUrl.objects.filter(active_monitor=True):
                harvested_obj = Harvester(watch_url_obj)
                retun_objects = harvested_obj.process_url()

                for retun_object in retun_objects:
                    comparator_obj = Comparator(retun_object)
                    comparator_obj.compare_and_alert()
            print("INFO: Runner DONE")
        else:
            print("WARNING: No WatchURL candidates, nothing to precess. Check WatchURL table")



