# ChangeLog

BI indicates a backward incompatible change. Take caution when upgrading to a
version with these. Your code will need to be updated to continue working.

## 2.0.0

 * BI: account deletion callbacks moved to hooksets
 * BI: dropped Django 1.7 support
 * BI: removed deprecated `ACCOUNT_USE_AUTH_AUTHENTICATE` setting with behavior matching its `True` value 
 * added Turkish translations
 * fixed migration with language codes to dynamically set

## 1.3.0

 * added Python 3.5 and Django 1.9 compatibility
 * added Japanese translations
 * added model kwarg to SignupView.create_user enabling sign up for complex user hierarchies

## 1.2.0

 * added {% urlnext %} template tag

## 1.1.0

 * added Django 1.8 support
 * dropped Django 1.4, 1.6 and Python 2.6 support
 * improved test coverage
 * fixed edge case bugs in sign up codes
 * added Django migrations
 * added email notification on password change
