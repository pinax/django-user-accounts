# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-08 10:14
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_passwordexpiry_passwordhistory'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='passwordhistory',
            options={'verbose_name': 'password history', 'verbose_name_plural': 'password histories'},
        ),
    ]
