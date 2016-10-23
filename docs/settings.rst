.. _settings:

========
Settings
========

``ACCOUNT_OPEN_SIGNUP``
=======================

Default: ``True``

``ACCOUNT_LOGIN_URL``
=====================

Default: ``"account_login"``

``ACCOUNT_SIGNUP_REDIRECT_URL``
===============================

Default: ``"/"``

``ACCOUNT_LOGIN_REDIRECT_URL``
==============================

Default: ``"/"``

``ACCOUNT_LOGOUT_REDIRECT_URL``
===============================

Default: ``"/"``


``ACCOUNT_PASSWORD_CHANGE_REDIRECT_URL``
========================================

Default: ``"account_password"``

``ACCOUNT_PASSWORD_RESET_REDIRECT_URL``
=======================================

Default: ``"account_login"``

``ACCOUNT_PASSWORD_EXPIRY``
=======================================

Default: ``0``

``ACCOUNT_PASSWORD_USE_HISTORY``
=======================================

Default: ``False``

``ACCOUNT_REMEMBER_ME_EXPIRY``
==============================

Default: ``60 * 60 * 24 * 365 * 10``

``ACCOUNT_USER_DISPLAY``
========================

Default: ``lambda user: user.username``

``ACCOUNT_CREATE_ON_SAVE``
==========================

Default: ``True``

``ACCOUNT_EMAIL_UNIQUE``
========================

Default: ``True``

``ACCOUNT_EMAIL_CONFIRMATION_REQUIRED``
=======================================

Default: ``False``

``ACCOUNT_EMAIL_CONFIRMATION_EMAIL``
====================================

Default: ``True``

``ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS``
==========================================

Default: ``3``

``ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL``
=====================================================

Default: ``"account_login"``

``ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL``
=========================================================

Default: ``None``

``ACCOUNT_EMAIL_CONFIRMATION_URL``
==================================

Default: ``"account_confirm_email"``

``ACCOUNT_SETTINGS_REDIRECT_URL``
=================================

Default: ``"account_settings"``

``ACCOUNT_NOTIFY_ON_PASSWORD_CHANGE``
=====================================

Default: ``True``

``ACCOUNT_DELETION_MARK_CALLBACK``
==================================

Default: ``"account.callbacks.account_delete_mark"``

``ACCOUNT_DELETION_EXPUNGE_CALLBACK``
=====================================

Default: ``"account.callbacks.account_delete_expunge"``

``ACCOUNT_DELETION_EXPUNGE_HOURS``
==================================

Default: ``48``

``ACCOUNT_HOOKSET``
===================

Default: ``"account.hooks.AccountDefaultHookSet"``

This setting allows you define your own hooks for specific functionality that
django-user-accounts exposes. Point this to a class using a string and you can
override the following methods:

* ``send_invitation_email(to, ctx)``
* ``send_confirmation_email(to, ctx)``
* ``send_password_change_email(to, ctx)``
* ``send_password_reset_email(to, ctx)``

``ACCOUNT_TIMEZONES``
=====================

Default: ``list(zip(pytz.all_timezones, pytz.all_timezones))``

``ACCOUNT_LANGUAGES``
=====================

See full list in: https://github.com/pinax/django-user-accounts/blob/master/account/language_list.py
