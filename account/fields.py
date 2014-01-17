from __future__ import unicode_literals

from django.db import models
from django.utils import six

from account.conf import settings

HAS_SOUTH = True
try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    HAS_SOUTH = False


class TimeZoneField(six.with_metaclass(models.SubfieldBase, models.CharField)):

    def __init__(self, *args, **kwargs):
        defaults = {
            "max_length": 100,
            "default": "",
            "choices": settings.ACCOUNT_TIMEZONES,
            "blank": True,
        }
        defaults.update(kwargs)
        return super(TimeZoneField, self).__init__(*args, **defaults)


if HAS_SOUTH:
    add_introspection_rules([], ["^account\.fields\.TimeZoneField"])
