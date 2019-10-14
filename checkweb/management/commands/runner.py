from django.core.management.base import BaseCommand

from checkweb.models import *
from django.utils import timezone
from django.conf import settings
import os

from checkweb.functions.get_snapshots import Harvester
from checkweb.functions.compare_snapshots import Comparator

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

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

        logger.info("INFO: Runner Starting...")


        # cleaning
        time_threshold = timezone.now() - timezone.timedelta(days=14)

        try:
            logger.info("CleanUp! {} old alerts deleted".format(
                Alert.objects.filter(created__gte=time_threshold).count()))
            Alert.objects.filter(created__lt=time_threshold).delete()
        except Exception as Err:
            logger.error("Cleaning script on Alerts failed. Err: {}".format(Err))

        try:
            logger.info("CleanUp! {} old Snapshots deleted".format(
                Snapshot.objects.filter(created__gte=time_threshold).count()))
            Snapshot.objects.filter(created__lt=time_threshold).delete()
        except Exception as Err:
            logger.error("Cleaning script on Snapshots failed. Error:{}".format(Err))



        if WatchUrl.objects.filter(active_monitor=True).count() >0:
            for watch_url_obj in WatchUrl.objects.filter(active_monitor=True):
                harvested_obj = Harvester(watch_url_obj)
                retun_objects = harvested_obj.process_url()

                for retun_object in retun_objects:
                    comparator_obj = Comparator(retun_object)
                    comparator_obj.compare_and_alert()
            logger.info("INFO: Runner DONE")
        else:
            logger.warning("WARNING: No WatchURL candidates, nothing to precess. Check WatchURL table")



