from django.core.management.base import BaseCommand

from checkweb.models import *
from django.utils import timezone
from django.conf import settings
import os


class Command(BaseCommand):
    help = """Create test URLs with configs"""

    #def add_arguments(self, parser):
    #    parser.add_argument(
    #        "-d",
    #        "--delete",
    #        help="Wipe out existing content before generating new.",
    #        action="store_true")

    def handle(self, *args, **options):

        #if options.get('delete'):
            # pass

        print("INFO: Hopper Starting...")

        WatchUrl.objects.create(
            description='simple static page only',
            domain='http://heartbleed.com/',
            active_monitor = False,
            active_discover_urls = False,
            active_tor_proxy = False,
        )
        print("DEBUG: testwatch1 created")

        WatchUrl.objects.create(
            description='Basic HTTP Auth - Unauthorized',
            domain='http://246.s.hostens.cloud/',
            active_monitor = False,
            active_discover_urls = False,
            active_tor_proxy = False,
        )
        print("DEBUG: testwatch2 created")

        WatchUrl.objects.create(
            description='Redirect to 443',
            domain='http://larsjung.de/h5ai/',
            active_monitor = False,
            active_discover_urls = False,
            active_tor_proxy = False,
        )
        print("DEBUG: testwatch3 created")

        WatchUrl.objects.create(
            description='Redirect subpage',
            domain='http://www.h2database.com',
            active_monitor = False,
            active_discover_urls = False,
            active_tor_proxy = False,
        )
        print("DEBUG: testwatch4 created")

        WatchUrl.objects.create(
            description='changing only content',
            domain='http://127.0.0.1:8000/checkweb/test_reply?content=true',
            active_monitor = False,
            active_discover_urls = False,
            active_tor_proxy = False,
        )
        print("DEBUG: test_reply1 created")

        WatchUrl.objects.create(
            description='changing only status code',
            domain='http://127.0.0.1:8000/checkweb/test_reply?status=true',
            active_monitor = False,
            active_discover_urls = False,
            active_tor_proxy = False,
        )
        print("DEBUG: test_reply1 created")

        WatchUrl.objects.create(
            description='changing both status code and content',
            domain='http://127.0.0.1:8000/checkweb/test_reply?status=true&content=true',
            active_monitor = False,
            active_discover_urls = False,
            active_tor_proxy = False,
        )
        print("DEBUG: test_reply1 created")


        print("INFO: Hopper DONE")

