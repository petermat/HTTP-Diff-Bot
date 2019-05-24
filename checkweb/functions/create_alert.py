from checkweb.models import *
from django.utils import timezone

import django
django.setup()


class AlertMaster:
    '''
    inp: snapshot object
    out: compared values, if crossing tresholds then alert
    '''

    def __init__(self, snapshot_obj):
        pass