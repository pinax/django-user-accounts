.. _templates:

============
Templates
============
This document covers the implementation of django-user-accounts within django templates. The pinax-theme-bootstrap-account package provides a good starting point to build off of. 
Note, this document assumes you have read the installation docs.

Template Files
===============

By default, django-user-accounts expects the following templates. If you don't use ``pinax-theme-bootstrap-account``, then you will have to create these templates yourself. 
You can also customize the names and locations of the templates by customizing the views.

Login/Registration/Signup Templates:
**************************************
``account/login.html`` 

``account/logout.html``

``account/signup.html``

``account/signup_closed.html``


Email Confirmation Templates:
*****************************

``account/email_confirm.html`` 

``account/email_confirmation_sent.html``

``account/email_confirmed.html`` 



Password Management:
********************

``account/password_change.html``

``account/password_reset.html``

``account/password_reset_sent.html``

``account/password_reset_token.html``

``account/password_reset_token_fail.html``

Account Settings:
*****************

``account/settings.html``


Template Tags
===============

To use the built in template tags you must first load them within the templates:

``{{ load account_tags }}``

To display the current logged-in user:

``{% user_display request.user %}``
