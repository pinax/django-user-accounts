.. _templates:

=========
Templates
=========

This document covers the implementation of django-user-accounts within Django
templates. The `pinax-theme-bootstrap`_ package provides a good `starting point`_
to build from. Note, this document assumes you have read the installation docs.

.. _pinax-theme-bootstrap: https://github.com/pinax/pinax-theme-bootstrap
.. _starting point: https://github.com/pinax/pinax-theme-bootstrap/tree/master/pinax_theme_bootstrap/templates/account

Template Files
===============

By default, django-user-accounts expects the following templates. If you
don't use ``pinax-theme-bootstrap``, then you will have to create these
templates yourself.


Login/Registration/Signup Templates::

    account/login.html
    account/logout.html
    account/signup.html
    account/signup_closed.html

Email Confirmation Templates::

    account/email_confirm.html
    account/email_confirmation_sent.html
    account/email_confirmed.html

Password Management Templates::

    account/password_change.html
    account/password_reset.html
    account/password_reset_sent.html
    account/password_reset_token.html
    account/password_reset_token_fail.html

Account Settings::

    account/settings.html

Emails (actual emails themselves)::

    account/email/email_confirmation_message.txt
    account/email/email_confirmation_subject.txt
    account/email/invite_user.txt
    account/email/invite_user_subject.txt
    account/email/password_change.txt
    account/email/password_change_subject.txt
    account/email/password_reset.txt
    account/email/password_reset_subject.txt

Template Tags
=============

To use the built in template tags you must first load them within the templates:

.. code-block:: jinja

    {% load account_tags %}

To display the current logged-in user:

.. code-block:: jinja

    {% user_display request.user %}
