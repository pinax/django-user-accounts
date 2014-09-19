====================
django-user-accounts
====================

*user accounts for Django*

.. image:: https://img.shields.io/travis/pinax/django-user-accounts.svg
    :target: https://travis-ci.org/pinax/django-user-accounts

.. image:: https://img.shields.io/coveralls/pinax/django-user-accounts.svg
    :target: https://coveralls.io/r/pinax/django-user-accounts

.. image:: https://img.shields.io/pypi/dm/django-user-accounts.svg
    :target:  https://pypi.python.org/pypi/django-user-accounts/

.. image:: https://img.shields.io/pypi/v/django-user-accounts.svg
    :target:  https://pypi.python.org/pypi/django-user-accounts/

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target:  https://pypi.python.org/pypi/django-user-accounts/


Provides a Django project with a very extensible infrastructure for dealing
with user accounts.

Features
========

* Functionality for:

  - Log in (email or username authentication)
  - Sign up
  - Email confirmation
  - Signup tokens for private betas
  - Password reset
  - Account management (update account settings and change password)
  - Account deletion

* Extensible class-based views and hooksets
* Custom ``User`` model support

Requirements
============

* Django 1.4, 1.6 or 1.7
* Python 2.6, 2.7, 3.3 or 3.4
* django-appconf (included in ``install_requires``)
* pytz (included in ``install_requires``)

Keep in mind that the Python version support will also depend on what is
supported by Django. For example, if you need to use Python 2.6 you can't use
Django 1.7+.

Documentation
=============

See http://django-user-accounts.readthedocs.org/

Contributing
============

We accept contributions for everyone! See the ``CONTRIBUTING.md`` file for more
information about how to contribute.
