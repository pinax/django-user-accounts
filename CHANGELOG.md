# Change Log

BI indicates a backward incompatible change. Take caution when upgrading to a
version with these. Your code will need to be updated to continue working.

## 3.1.0

* #205 - Bug fix on checking email against email not signup code
* #225 - Fix case sensitivity mismatch on email addresses
* #233 - Fix link to languages in docs
* #247 - Update Spanish translations
* #273 - Update German translations
* #135 - Update Russian translations
* #242 - Fix callbacks/hooks for account deletion
* #251 (#249) - Allow overriding the password reset token url
* #280 - Raise improper config error if signup view can't login
* #348 (#337) - Make https the default protocol
* #351 (#332) - Reduction in queries
* #360 (#210) - Updates to docs
* #361 (#141) - Added ability to override clean passwords
* #362 - Updated CI to use Pinax Actions
* Updates to packaging
* Dropped Python 3.5 and Django 3.1 from test matrix
* Added Python 3.10 to test matrix


## 3.0.3

* Fix deprecated urls
* Update template context processors docs
* Fix deprecrated argument in signals
* Update decorators for Django 3
* Fix issue with lazy string
* Drop deprecated `force_text()`

## 3.0.2

* Drop Django 2.0 and Python 2,7, 3.4, and 3.5 support
* Add Django 2.1, 2.2 and 3.0, and Python 3.7 and 3.8 support
* Update packaging configs

## 2.0.3

 * fixed breaking change in 2.0.2 where context did not have uidb36 and token
 * improved documentation

## 2.0.2

 * fixed potentional security issue with leaking password reset tokens through HTTP Referer header
 * added `never_cache`, `csrf_protect` and `sensitive_post_parameters` to appropriate views

## 2.0.1

@@@ todo

## 2.0.0

 * BI: moved account deletion callbacks to hooksets
 * BI: dropped Django 1.7 support
 * BI: dropped Python 3.2 support
 * BI: removed deprecated `ACCOUNT_USE_AUTH_AUTHENTICATE` setting with behavior matching its `True` value
 * added Django 1.10 support
 * added Turkish translations
 * fixed migration with language codes to dynamically set
 * added password expiration
 * added password stripping by default
 * added `ACCOUNT_EMAIL_CONFIRMATION_AUTO_LOGIN` feature (default is `False`)

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
