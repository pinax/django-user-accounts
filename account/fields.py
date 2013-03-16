from django.db import models

from account.conf import settings


class TimeZoneField(models.CharField):
    
    __metaclass__ = models.SubfieldBase
    
    def __init__(self, *args, **kwargs):
        default_tz = 'UTC'
        if settings.TIME_ZONE:
            default_tz = settings.TIME_ZONE
        defaults = {
            "max_length": 100,
            "default": default_tz,
            "choices": settings.ACCOUNT_TIMEZONES,
            "blank": True,
        }
        defaults.update(kwargs)
        return super(TimeZoneField, self).__init__(*args, **defaults)
