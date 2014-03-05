.. _faq:

===
FAQ
===

This document is a collection of frequently asked questions about
django-user-accounts.

What is the difference between django-user-accounts and django.contrib.auth?
============================================================================

django-user-accounts is designed to supplement ``django.contrib.auth``. This
app provides improved views for log in, password reset, log out and adds
sign up functionality. We try not to duplicate code when Django provides a
good implementation. For example, we did not re-implement password reset, but
simply provide an improved view which calls into the secure Django password
reset code. ``django.contrib.auth`` is still providing many of supporting
elements such as ``User`` model, default authentication backends, helper
functions and authorization.

django-user-accounts takes your Django project from having simple log in,
log out and password reset to a full blown account management system that you
will end up building anyways.

Why can email addresses get out of sync?
========================================

django-user-accounts stores email addresses in two locations. The default
``User`` model contains an ``email`` field and django-user-accounts provides an
``EmailAddress`` model. This latter is provided to support multiple email
addresses per user.

If you use a custom user model you can prevent the double storage. This is
because you can choose not to do any email address storage.

If you don't use a custom user model then make sure you take extra precaution.
When editing email addresses either in the shell or admin make sure you update
in both places. Only the primary email address is stored on the ``User`` model.

Why does auto-login after sign up not log my user in?
=====================================================

If you are using Django 1.6+ and ``django.contrib.auth.backends.ModelBackend``
does not exist in your ``AUTHENTICATION_BACKENDS`` then you will experience an
issue where users are not logged in after sign up (when
``ACCOUNT_EMAIL_CONFIRMATION_REQUIRED`` is ``False``.)

This has been fixed, but the default behavior is buggy (for this use case) to
maintain backward compatibility. In a future version of django-user-accounts
the default behavior will not be buggy.

To fix, simply set::

    ACCOUNT_USE_AUTH_AUTHENTICATE = True

in your Django settings. This will cause the ``login_user`` method of
``SignupView`` to use proper backend authentication to determine the correct
authentication backend for the user. You will need to make sure that
``SignupView.identifier_field`` is set to represent the correct field on the
sign up form to use as the username for credentials. By default the ``username``
field is used (to be consistent with the default username authentication used
for log in.)

If you have a custom need for user credentials passed to the authentication
backends, you may override the behavior using the hookset
``get_user_credentials``.
