.. _usage:

=====
Usage
=====

This document covers the usage of django-user-accounts. It assumes you've
read :ref:`installation`.

Using email address for authentication
======================================

django-user-accounts allows you to use email addresses for authentication
instead of usernames. You still have the option to continue using usernames
or get rid of them entirely.

To enable email authentication do the following:

1. check your settings for the following values::
   
       ACCOUNT_EMAIL_UNIQUE = True
       ACCOUNT_EMAIL_CONFIRMATION_REQUIRED = True
   
   .. note::
   
       If you need to change the value of ``ACCOUNT_EMAIL_UNIQUE`` make sure your
       database schema is modified to support a unique email column in
       ``account_emailaddress``.
   
   ``ACCOUNT_EMAIL_CONFIRMATION_REQUIRED`` is optional, but highly
   recommended to be ``True``.

2. define your own ``LoginView`` in your project::
   
       import account.forms
       import account.views
       
       
       class LoginView(account.views.LoginView):
           
           form_class = account.views.LoginEmailForm

3. ensure ``"account.auth_backends.EmailAuthenticationBackend"`` is in ``AUTHENTICATION_BACKENDS``

If you want to get rid of username you'll need to do some extra work:

1. define your own ``SignupForm`` and ``SignupView`` in your project::
   
       # forms.py
       
       import account.forms
       
       
       class SignupForm(account.forms.SignupForm):
           
           def __init__(self, *args, **kwargs):
               super(SignupForm, self).__init__(*args, **kwargs)
               del self.fields["username"]
       
       # views.py
       
       import account.views
       
       
       class SignupView(account.views.SignupView):
           
           form_class = myproject.forms.SignupForm
           
           def generate_username(self, form):
               # do something to generate a unique username (required by the
               # Django User model, unfortunately)
               username = "<magic>"
               return username

2. many places will rely on a username for a User instance.
   django-user-accounts provides a mechanism to add a level of indirection
   when representing the user in the user interface. Keep in mind not
   everything you include in your project will do what you expect when
   removing usernames entirely.
   
   Set ``ACCOUNT_USER_DISPLAY`` in settings to a callable suitable for your
   site::
   
       ACCOUNT_USER_DISPLAY = lambda user: user.email
   
   Your Python code can use ``user_display`` to handle user representation::
   
       from account.utils import user_display
       user_display(user)
   
   Your templates can use ``{% user_display request.user %}``::
   
       {% load account_tags %}
       {% user_display request.user %}
