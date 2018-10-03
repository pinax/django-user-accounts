.. _usage:

=====
Usage
=====

This document covers the usage of django-user-accounts. It assumes you've
read :ref:`installation`.

django-user-accounts has very good default behavior when handling user
accounts. It has been designed to be customizable in many aspects. By default
this app will:

* enable username authentication
* provide default views and forms for sign up, log in, password reset and
  account management
* handle log out with POST
* require unique email addresses globally
* require email verification for performing password resets

The rest of this document will cover how you can tweak the default behavior
of django-user-accounts.

Limiting access to views
========================

To limit view access to logged in users, normally you would use the Django decorator ``django.contrib.auth.decorators.login_required``.  Instead you should use ``account.decorators.login_required``.


Customizing the sign up process
===============================

In many cases you need to tweak the sign up process to do some domain specific
tasks. Perhaps you need to update a profile for the new user or something else.
The built-in ``SignupView`` has hooks to enable just about any sort of
customization during sign up. Here's an example of a custom ``SignupView``
defined in your project::

    import account.views


    class SignupView(account.views.SignupView):

        def after_signup(self, form):
            self.update_profile(form)
            super(SignupView, self).after_signup(form)

        def update_profile(self, form):
            profile = self.created_user.profile  # replace with your reverse one-to-one profile attribute
            profile.some_attr = "some value"
            profile.save()


This example assumes you had a receiver hooked up to the `post_save` signal for
the sender, `User` like so::

    from django.dispatch import receiver
    from django.db.models.signals import post_save

    from django.contrib.auth.models import User

    from mysite.profiles.models import UserProfile


    @receiver(post_save, sender=User)
    def handle_user_save(sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(user=instance)


You can define your own form class to add fields to the sign up process::

    # forms.py

    from django import forms
    from django.forms.extras.widgets import SelectDateWidget

    import account.forms


    class SignupForm(account.forms.SignupForm):

        birthdate = forms.DateField(widget=SelectDateWidget(years=range(1910, 1991)))

    # views.py

    import account.views

    import myproject.forms


    class SignupView(account.views.SignupView):

       form_class = myproject.forms.SignupForm

       def after_signup(self, form):
           self.create_profile(form)
           super(SignupView, self).after_signup(form)

       def create_profile(self, form):
           profile = self.created_user.profile  # replace with your reverse one-to-one profile attribute
           profile.birthdate = form.cleaned_data["birthdate"]
           profile.save()

To hook this up for your project you need to override the URL for sign up::

    from django.conf.urls import patterns, include, url

    import myproject.views


    urlpatterns = patterns("",
        url(r"^account/signup/$", myproject.views.SignupView.as_view(), name="account_signup"),
        url(r"^account/", include("account.urls")),
    )

.. note::

    Make sure your ``url`` for ``/account/signup/`` comes *before* the
    ``include`` of ``account.urls``. Django will short-circuit on yours.

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

           form_class = account.forms.LoginEmailForm

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

       import myproject.forms


       class SignupView(account.views.SignupView):

           form_class = myproject.forms.SignupForm
           identifier_field = 'email'

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


Allow non-unique email addresses
================================

If your site requires that you support non-unique email addresses globally
you can tweak the behavior to allow this.

Set ``ACCOUNT_EMAIL_UNIQUE`` to ``False``. If you have already setup the
tables for django-user-accounts you will need to migrate the
``account_emailaddress`` table::

   ALTER TABLE "account_emailaddress" ADD CONSTRAINT "account_emailaddress_user_id_email_key" UNIQUE ("user_id", "email");
   ALTER TABLE "account_emailaddress" DROP CONSTRAINT "account_emailaddress_email_key";

``ACCOUNT_EMAIL_UNIQUE = False`` will allow duplicate email addresses per
user, but not across users.


Including accounts in fixtures
==============================

If you want to include account_account in your fixture, you may notice
that when you load that fixture there is a conflict because
django-user-accounts defaults to creating a new account for each new
user.

Example::

    IntegrityError: Problem installing fixture \
          ...'/app/fixtures/some_users_and_accounts.json': \
          Could not load account.Account(pk=1): duplicate key value violates unique constraint \
          "account_account_user_id_key"
    DETAIL:  Key (user_id)=(1) already exists.

To prevent this from happening, subclass DiscoverRunner and in
setup_test_environment set CREATE_ON_SAVE to False.  For example in a
file called lib/tests.py::

    from django.test.runner import DiscoverRunner
    from account.conf import AccountAppConf

    class MyTestDiscoverRunner(DiscoverRunner):

        def setup_test_environment(self, **kwargs):
            super(MyTestDiscoverRunner, self).setup_test_environment(**kwargs)
            aac = AccountAppConf()
            aac.CREATE_ON_SAVE = False


And in your settings::

    TEST_RUNNER = "lib.tests.MyTestDiscoverRunner"


Enabling password expiration
============================

Password expiration is disabled by default. In order to enable password expiration
you must add entries to your settings file::

    ACCOUNT_PASSWORD_EXPIRY = 60*60*24*5  # seconds until pw expires, this example shows five days
    ACCOUNT_PASSWORD_USE_HISTORY = True

and include `ExpiredPasswordMiddleware` with your middleware settings::

    MIDDLEWARE_CLASSES = {
        ...
        "account.middleware.ExpiredPasswordMiddleware",
    }

``ACCOUNT_PASSWORD_EXPIRY`` indicates the duration a password will stay valid. After that period
the password must be reset in order to view any page. If ``ACCOUNT_PASSWORD_EXPIRY`` is zero (0)
then passwords never expire.

If ``ACCOUNT_PASSWORD_USE_HISTORY`` is False, no history will be generated and password
expiration WILL NOT be checked.

If ``ACCOUNT_PASSWORD_USE_HISTORY`` is True, a password history entry is created each time
the user changes their password. This entry links the user with their most recent
(encrypted) password and a timestamp. Unless deleted manually, PasswordHistory items
are saved forever, allowing password history checking for new passwords.

For an authenticated user, ``ExpiredPasswordMiddleware`` prevents retrieving or posting
to any page except the password change page and log out page when the user password is expired.
However, if the user is "staff" (can access the Django admin site), the password check is skipped.
