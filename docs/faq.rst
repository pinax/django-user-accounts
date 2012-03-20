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
