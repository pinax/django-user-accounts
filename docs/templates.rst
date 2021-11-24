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


Login/Registration/Signup Templates
-----------------------------------

**account/login.html**

The template with the form to authenticate the user. The template has the
following context:

``form``
    The login form.

``redirect_field_name``
    The name of the hidden field that will hold the url where to redirect the
user after login.

``redirect_field_value``
    The actual url where the user will be redirected after login.

**account/logout.html**

The default template shown after the user has been logged out.

**account/signup.html**

The template with the form to registrate a new user. The template has the
following context:

``form``
    The form used to create the new user.

``redirect_field_name``
    The name of the hidden field that will hold the url where to redirect the
user after signing up.

``redirect_field_value``
    The actual url where the user will be redirected after signing up.

**account/signup_closed.html**

A template to inform the user that creating new users is not allowed (mainly
because ``settings.ACCOUNT_OPEN_SIGNUP`` is ``False``).

Email Confirmation Templates
----------------------------

**account/email_confirm.html**

A template to confirm an email address. The template has the following context:

``email``
    The email address where the activation link has been sent.

``confirmation``
    The EmailConfirmation instance to be confirmed.

**account/email_confirmation_sent.html**

The template shown after a new user has been created. It should tell the user
that an activation link has been sent to his email address. The template has
the following context:

``email``
    The email address where the activation link has been sent.

``success_url``
    A url where the user can be redirected from this page. For example to
show a link to go back.

**account/email_confirmed.html**

A template shown after an email address has been confirmed. The template
context is the same as in email_confirm.html.

``email``
    The email address that has been confirmed.

Password Management Templates
-----------------------------

**account/password_change.html**

The template that shows the form to change the user's password, when the user
is authenticated. The template has the following context:

``form``
    The form to change the password.

**account/password_reset.html**

A template with a form to type an email address to reset a user's password.
The template has the following context:

``form``
    The form to reset the password.

**account/password_reset_sent.html**

A template to inform the user that his password has been reset and that he
should receive an email with a link to create a new password. The template has
the following context:

``form``
    An instance of ``PasswordResetForm``. Usually the fields of this form
must be hidden.

``resend``
    If ``True`` it means that the reset link has been resent to the user.

**account/password_reset_token.html**

The template that shows the form to change the user's password. The user should
have come here following the link received to reset his password. The template
has the following context:

``form``
    The form to set the new password.

**account/password_reset_token_fail.html**

A template to inform the user that he is not allowed to change the password,
because the authentication token is wrong. The template has the following
context:

``url``
    The url to request a new reset token.

Account Settings
----------------

**account/settings.html**

A template with a form where the user may change his email address, time zone
and preferred language. The template has the following context:

``form``
    The form to change the settings.

Emails (actual emails themselves)
---------------------------------

**account/email/email_confirmation_subject.txt**

The subject line of the email that will be sent to the new user to validate the
email address. It will be rendered as a single line. The template has the
following context:

``email_address``
    The actual email address where the activation message will be sent.

``user``
    The new user object.

``activate_url``
    The complete url for account activation, including protocol and domain.

``current_site``
    The domain name of the site.

``key``
    The confirmation key.

**account/email/email_confirmation_message.txt**

The body of the activation email. It has the same context as the subject
template (see above).

**account/email/invite_user.txt**

The body of the invitation sent to somebody to join the site. The template has
the following context:

``signup_code``
    An instance of account.models.SignupCode.

``current_site``
    The instance of django.contrib.sites.models.Site that identifies the site.

``signup_url``
    The link used to use the invitation and create a new account.

**account/email/invite_user_subject.txt**

The subject line of the invitation sent to somebody to join the site. The
template has the same context as in invite_user.txt.

**account/email/password_change.txt**

The body of the email used to inform the user that his password has been
changed. The template has the following context:

``user``
    The user whom the password belongs to.

``protocol``
    The application protocol (usually http or https) being used in the site.

``current_site``
    The instance of django.contrib.sites.models.Site that identifies the site.

**account/email/password_change_subject.txt**

The subject line of the email used to inform the user that his password has
been changed. The context is the same as in password_change.txt.

**account/email/password_reset.txt**

The body of the email with a link to reset a user's password. The template has
the following context:


``user``
    The user whom the password belongs to.

``current_site``
    The instance of django.contrib.sites.models.Site that identifies the site.

``password_reset_url``
    The link that the user needs to follow to set a new password.

**account/email/password_reset_subject.txt**

The subject line of the email with a link to reset a user's password. The
context is the same as in password_reset.txt.

Template Tags
=============

To use the built in template tags you must first load them within the templates:

.. code-block:: jinja

    {% load account_tags %}

To display the current logged-in user:

.. code-block:: jinja

    {% user_display request.user %}
