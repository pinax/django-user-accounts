# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_auto_20170416_1821'),
    ]

    operations = [
        migrations.AddField(
            model_name='signupcode',
            name='username',
            field=models.CharField(default=None, max_length=30, null=True, blank=True),
        ),
    ]
