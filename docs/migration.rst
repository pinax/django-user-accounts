.. _migration:

====================
Migration from Pinax
====================

django-user-accounts is based on ``pinax.apps.account`` combining some of
the supporting apps. django-email-confirmation, ``pinax.apps.signup_codes``
and bits of django-timezones have been merged to create django-user-accounts.

This document will outline the changes needed to migrate from Pinax to using
this app in your Django project. If you are new to django-user-accounts then
this guide will not be useful to you.

Database changes
================

Due to combining apps the table layout when converting from Pinax has changed.
We've also taken the opportunity to update the schema to take advantage of
much saner defaults. Here is SQL (tested on PostgreSQL only) to convert from
Pinax to django-user-accounts::

    ALTER TABLE "emailconfirmation_emailaddress" RENAME TO "account_emailaddress";
    ALTER TABLE "emailconfirmation_emailconfirmation" RENAME TO "account_emailconfirmation";
    ALTER TABLE "signup_codes_signupcode" RENAME TO "account_signupcode";
    ALTER TABLE "signup_codes_signupcoderesult" RENAME TO "account_signupcoderesult";
    DROP TABLE "account_passwordreset";
    -- @@@ more ...

URL changes
===========

No changes have been made to URLs. As long as django-user-account is mounted
at ``/account/`` everything should be backwards compatible.

View changes
============

All views have been converted to class-based views. This is a big departure
from the traditional function-based, but has the benefit of being much more
flexible.

@@@ todo: table of changes

General changes
===============

django-user-accounts requires Django 1.4. This means we can take advantage of
many of the new features offered by Django. This app implements all of the
best practices of Django 1.4. If there is something missing you should let us
know!
