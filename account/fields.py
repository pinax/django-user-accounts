from __future__ import unicode_literals

import django

from django.db import models
from django.utils import six

from account.conf import settings


if django.VERSION < (1, 8):
    base = six.with_metaclass(models.SubfieldBase, models.CharField)
else:
    base = models.CharField


class TimeZoneField(base):

    def __init__(self, *args, **kwargs):
        defaults = {
            "max_length": 100,
            "default": "",
            "choices": settings.ACCOUNT_TIMEZONES,
            "blank": True,
        }
        defaults.update(kwargs)
        return super(TimeZoneField, self).__init__(*args, **defaults)
