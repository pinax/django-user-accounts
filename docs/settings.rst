.. _settings:

========
Settings
========

``ACCOUNT_OPEN_SIGNUP``
=======================

Default: ``True``

If ``True``, creation of new accounts is allowed. When the signup view is
called, the template ``account/signup.html`` will be displayed, usually
showing a form to collect the new user data.

If ``False``, creation of new accounts is disabled. When the signup view is
called, the template ``account/signup_closed.html`` will be displayed.

``ACCOUNT_LOGIN_URL``
=====================

Default: ``"account_login"``

The name of the urlconf that calls the login view.

``ACCOUNT_SIGNUP_REDIRECT_URL``
===============================

Default: ``"/"``

The url where the user will be redirected after a successful signup.

``ACCOUNT_LOGIN_REDIRECT_URL``
==============================

Default: ``"/"``

The url where the user will be redirected after a successful authentication,
unless the ``next`` parameter is defined in the request.

``ACCOUNT_LOGOUT_REDIRECT_URL``
===============================

Default: ``"/"``

The url where the user will be redirected after logging out.

``ACCOUNT_PASSWORD_CHANGE_REDIRECT_URL``
========================================

Default: ``"account_password"``

The url where the user will be redirected after changing his password.

``ACCOUNT_PASSWORD_RESET_REDIRECT_URL``
=======================================

Default: ``"account_login"``

The url where the user will be redirected after resetting his password.

``ACCOUNT_REMEMBER_ME_EXPIRY``
==============================

Default: ``60 * 60 * 24 * 365 * 10``

The number of seconds that the user will remain authenticated after he logs in
the site.

``ACCOUNT_USER_DISPLAY``
========================

Default: ``lambda user: user.username``

The function that will be called by the template tag user_display.

``ACCOUNT_CREATE_ON_SAVE``
==========================

Default: ``True``

If ``True``, an account instance will be created when a new user is created.

``ACCOUNT_EMAIL_UNIQUE``
========================

Default: ``True``

If ``False``, more than one user can have the same email address.

``ACCOUNT_EMAIL_CONFIRMATION_REQUIRED``
=======================================

Default: ``False``

If ``True``, new user accounts will be created as inactive. The user must use
the activation link to activate his account.

``ACCOUNT_EMAIL_CONFIRMATION_EMAIL``
====================================

Default: ``True``

If ``True``, an email confirmation message will be sent to the user when they
make a new account.

``ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS``
==========================================

Default: ``3``

After this time, the email confirmation link will not be longer valid.

``ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL``
=====================================================

Default: ``"account_login"``

A urlconf name where the user will be redirected after confirming an email
address, if he is not authenticated.

``ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL``
=========================================================

Default: ``None``

A urlconf name where the user will be redirected after confirming an email
address, if he is authenticated. If not set, this url will be the one defined
in ``ACCOUNT_LOGIN_REDIRECT_URL``.

``ACCOUNT_EMAIL_CONFIRMATION_URL``
==================================

Default: ``"account_confirm_email"``

A urlconf name that will be used to confirm the user email (usually from the
email message they received).

``ACCOUNT_SETTINGS_REDIRECT_URL``
=================================

Default: ``"account_settings"``

The url where the user will be redirected after updating their account settings.

``ACCOUNT_NOTIFY_ON_PASSWORD_CHANGE``
=====================================

Default: ``True``

If ``True``, an notification email will be sent whenever a user changes their
password.

``ACCOUNT_DELETION_MARK_CALLBACK``
==================================

Default: ``"account.callbacks.account_delete_mark"``

This function will be called just after a user asks for account deletion.

``ACCOUNT_DELETION_EXPUNGE_CALLBACK``
=====================================

Default: ``"account.callbacks.account_delete_expunge"``

The function that will be called to expunge accounts.

``ACCOUNT_DELETION_EXPUNGE_HOURS``
==================================

Default: ``48``

The minimum time in hours since a user asks for account deletion until their
account is deleted.

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

A list of time zones available for the user to set as their current time zone.

``ACCOUNT_LANGUAGES``
=====================

A tuple of languages available for the user to set as their preferred language.

See full list in: https://github.com/pinax/django-user-accounts/blob/master/account/languages.py

``ACCOUNT_USE_AUTH_AUTHENTICATE``
=================================

Default: ``False``

If ``True``, ``django.contrib.auth.authenticate`` will be used to authenticate
the user.

.. note::
    According to the comments in the code, this setting is deprecated and,
    in the future, ``django.contrib.auth.authenticate`` will be the preferred
    method.
