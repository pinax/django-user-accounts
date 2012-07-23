from django.db import models

from account.conf import settings


class TimeZoneField(models.CharField):
    
    __metaclass__ = models.SubfieldBase
    
    def __init__(self, *args, **kwargs):
        defaults = {
            "max_length": 100,
            "default": None,
            "choices": settings.ACCOUNT_TIMEZONES,
            "null": True,
            "blank": True,
        }
        defaults.update(kwargs)
        return super(TimeZoneField, self).__init__(*args, **defaults)
