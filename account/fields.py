from django.db import models

from account.conf import settings


class TimeZoneField(models.CharField):
    
    __metaclass__ = models.SubfieldBase
    
    def __init__(self, *args, **kwargs):
        defaults = {
            "max_length": 100,
            "default": settings.TIME_ZONE,
            "choices": settings.ACCOUNT_TIMEZONE_CHOICES
        }
        defaults.update(kwargs)
        return super(TimeZoneField, self).__init__(*args, **defaults)
