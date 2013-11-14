.. _settings:

========
Settings
========

``ACCOUNT_HOOKSET``
===================

This setting allows you define your own hooks for specific functionality that
django-user-accounts exposes. Point this to a class using a string and you can
override the following methods:

* ``send_invitation_email(to, ctx)``
* ``send_confirmation_email(to, ctx)``
* ``send_password_change_email(to, ctx)``
* ``send_password_reset_email(to, ctx)``
