from django.conf import settings
from django.db import models

import pytz


TIMEZONE_CHOICES = tuple(zip(pytz.all_timezones, pytz.all_timezones))


class TimeZoneField(models.CharField):
    
    __metaclass__ = models.SubfieldBase
    
    def __init__(self, *args, **kwargs):
        defaults = {
            "max_length": 100,
            "default": settings.TIME_ZONE,
            "choices": TIMEZONE_CHOICES
        }
        defaults.update(kwargs)
        return super(TimeZoneField, self).__init__(*args, **defaults)
