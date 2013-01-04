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
much saner defaults. Here is SQL to convert from Pinax to django-user-accounts.

PostgreSQL
----------

::

    ALTER TABLE "signup_codes_signupcode" RENAME TO "account_signupcode";
    ALTER TABLE "signup_codes_signupcoderesult" RENAME TO "account_signupcoderesult";
    ALTER TABLE "emailconfirmation_emailaddress" RENAME TO "account_emailaddress";
    ALTER TABLE "emailconfirmation_emailconfirmation" RENAME TO "account_emailconfirmation";
    DROP TABLE "account_passwordreset";
    ALTER TABLE "account_signupcode" ALTER COLUMN "code" TYPE varchar(64);
    ALTER TABLE "account_signupcode" ADD CONSTRAINT "account_signupcode_code_key" UNIQUE ("code");
    ALTER TABLE "account_emailconfirmation" RENAME COLUMN "confirmation_key" TO "key";
    ALTER TABLE "account_emailconfirmation" ALTER COLUMN "key" TYPE varchar(64);
    ALTER TABLE account_emailconfirmation ADD COLUMN created timestamp with time zone;
    UPDATE account_emailconfirmation SET created = sent;
    ALTER TABLE account_emailconfirmation ALTER COLUMN created SET NOT NULL;
    ALTER TABLE account_emailconfirmation ALTER COLUMN sent DROP NOT NULL;

If ``ACCOUNT_EMAIL_UNIQUE`` is set to ``True`` (the default value) you need::

    ALTER TABLE "account_emailaddress" ADD CONSTRAINT "account_emailaddress_email_key" UNIQUE ("email");
    ALTER TABLE "account_emailaddress" DROP CONSTRAINT "emailconfirmation_emailaddress_user_id_email_key";

MySQL
-----

::

    RENAME TABLE  `emailconfirmation_emailaddress` TO  `account_emailaddress` ;
    RENAME TABLE  `emailconfirmation_emailconfirmation` TO  `account_emailconfirmation` ;
    DROP TABLE account_passwordreset;
    ALTER TABLE  `account_emailconfirmation` CHANGE  `confirmation_key`  `key` VARCHAR(64) NOT NULL;
    ALTER TABLE `account_emailconfirmation` ADD UNIQUE (`key`);
    ALTER TABLE account_emailconfirmation ADD COLUMN created datetime NOT NULL;
    UPDATE account_emailconfirmation SET created = sent;
    ALTER TABLE  `account_emailconfirmation` CHANGE  `sent`  `sent` DATETIME NULL;

If ``ACCOUNT_EMAIL_UNIQUE`` is set to ``True`` (the default value) you need::

    ALTER TABLE  `account_emailaddress` ADD UNIQUE (`email`);
    ALTER TABLE account_emailaddress DROP INDEX user_id;

If you have installed ``pinax.apps.signup_codes``::

    RENAME TABLE  `signup_codes_signupcode` TO  `account_signupcode` ;
    RENAME TABLE  `signup_codes_signupcoderesult` TO  `account_signupcoderesult` ;


URL changes
===========

Here is a list of all URLs provided by django-user-accounts and how they map
from Pinax. This assumes ``account.urls`` is mounted at ``/account/`` as it
was in Pinax.

======================================  ====================================
Pinax                                   django-user-accounts
======================================  ====================================
``/account/login/``                     ``/account/login/``
``/account/signup/``                    ``/account/signup/``
``/account/confirm_email/``             ``/account/confirm_email/``
``/account/password_change/``           ``/account/password/`` [1]_
``/account/password_reset/``            ``/account/password/reset/``
``/account/password_reset_done/``       *removed*
``/account/password_reset_key/<key>/``  ``/account/password/reset/<token>/``
======================================  ====================================

.. [1] When user is anonymous and requests a GET the user is redirected to
   ``/account/password/reset/``.

View changes
============

All views have been converted to class-based views. This is a big departure
from the traditional function-based, but has the benefit of being much more
flexible.

@@@ todo: table of changes

Settings changes
================

We have cleaned up settings and set saner defaults used by
django-user-accounts.

===========================================  ===============================
Pinax                                        django-user-accounts
===========================================  ===============================
``ACCOUNT_OPEN_SIGNUP = True``               ``ACCOUNT_OPEN_SIGNUP = True``
``ACCOUNT_UNIQUE_EMAIL = False``             ``ACCOUNT_EMAIL_UNIQUE = True``
``EMAIL_CONFIRMATION_UNIQUE_EMAIL = False``  *removed*
===========================================  ===============================

General changes
===============

django-user-accounts requires Django 1.4. This means we can take advantage of
many of the new features offered by Django. This app implements all of the
best practices of Django 1.4. If there is something missing you should let us
know!
