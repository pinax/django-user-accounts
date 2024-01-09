.. _installation:

============
Installation
============

Install the development version::

    pip install django-user-accounts

Make sure that ``django.contrib.sites`` is in ``INSTALLED_APPS`` and add
 ``account`` to this setting::::

    INSTALLED_APPS = (
        "django.contrib.sites",
        # ...
        "account",
        # ...
    )

See the list of :ref:`settings` to modify the default behavior of
django-user-accounts and make adjustments for your website.

Add ``account.urls`` to your URLs definition::

    urlpatterns = patterns("",
        ...
        url(r"^account/", include("account.urls")),
        ...
    )

Add ``account.context_processors.account`` to ``context_processors``::

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [ ],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',

                    # add django-user-accounts context processor
                    'account.context_processors.account',
                ],
            },
        },
    ]

Add ``account.middleware.LocaleMiddleware`` and
``account.middleware.TimezoneMiddleware`` to ``MIDDLEWARE_CLASSES``::

    MIDDLEWARE_CLASSES = [
        ...
        "account.middleware.LocaleMiddleware",
        "account.middleware.TimezoneMiddleware",
        ...
    ]

Optionally include ``account.middleware.ExpiredPasswordMiddleware`` in
``MIDDLEWARE_CLASSES`` if you need password expiration support::

    MIDDLEWARE_CLASSES = [
        ...
        "account.middleware.ExpiredPasswordMiddleware",
        ...
    ]

Set the authentication backends to the following::

    AUTHENTICATION_BACKENDS = [
        'account.auth_backends.AccountModelBackend',
        'django.contrib.auth.backends.ModelBackend'
    ]

Once everything is in place make sure you run ``migrate`` to modify the
database with the ``account`` app models.

.. _dependencies:

Dependencies
============

``django.contrib.auth``
-----------------------

This is bundled with Django. It is enabled by default with all new Django
projects, but if you adding django-user-accounts to an existing project you
need to make sure ``django.contrib.auth`` is installed.

``django.contrib.sites``
------------------------

This is bundled with Django. It is enabled by default with all new Django
projects. It is used to provide links back to the site in emails or various
places in templates that need an absolute URL.

django-appconf_
---------------

We use django-appconf for app settings. It is listed in ``install_requires``
and will be installed when pip installs.

.. _django-appconf: https://github.com/jezdez/django-appconf

pytz_
-----

pytz is used for handling timezones for accounts. This dependency is critical
due to its extensive dataset for timezones.

.. _pytz: http://pypi.python.org/pypi/pytz/
