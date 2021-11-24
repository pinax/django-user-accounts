![](https://pinaxproject.com/pinax-design/social-banners/DUA.png)

[![](https://img.shields.io/pypi/v/django-user-accounts.svg)](https://pypi.python.org/pypi/django-user-accounts/)

[![CircleCi](https://img.shields.io/circleci/project/github/pinax/django-user-accounts.svg)](https://circleci.com/gh/pinax/django-user-accounts)
[![Codecov](https://img.shields.io/codecov/c/github/pinax/django-user-accounts.svg)](https://codecov.io/gh/pinax/django-user-accounts)
[![](https://img.shields.io/github/contributors/pinax/django-user-accounts.svg)](https://github.com/pinax/django-user-accounts/graphs/contributors)
[![](https://img.shields.io/github/issues-pr/pinax/django-user-accounts.svg)](https://github.com/pinax/django-user-accounts/pulls)
[![](https://img.shields.io/github/issues-pr-closed/pinax/django-user-accounts.svg)](https://github.com/pinax/django-user-accounts/pulls?q=is%3Apr+is%3Aclosed)

[![](http://slack.pinaxproject.com/badge.svg)](http://slack.pinaxproject.com/)
[![](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)


# Table of Contents

* [About Pinax](#about-pinax)
* [Overview](#overview)
  * [Features](#features)
  * [Supported Django and Python versions](#supported-django-and-python-versions)
* [Requirements](#requirements)
* [Documentation](#documentation)
* [Templates](#templates)
* [Contribute](#contribute)
* [Code of Conduct](#code-of-conduct)
* [Connect with Pinax](#connect-with-pinax)
* [License](#license)


## About Pinax

Pinax is an open-source platform built on the Django Web Framework. It is an ecosystem of reusable Django apps, themes, and starter project templates. This collection can be found at http://pinaxproject.com.


## django-user-accounts

### Overview

`django-user-accounts` provides a Django project with a very extensible infrastructure for dealing with user accounts.

#### Features

* Functionality for:
  * Log in (email or username authentication)
  * Sign up
  * Email confirmation
  * Signup tokens for private betas
  * Password reset
  * Password expiration
  * Account management (update account settings and change password)
  * Account deletion
* Extensible class-based views and hooksets
* Custom `User` model support

#### Supported Django and Python versions

Django / Python | 3.6 | 3.7 | 3.8 | 3.9
--------------- | --- | --- | --- | ---
2.2  |  *  |  *  |  *  |  * 
3.0  |  *  |  *  |  *  |  * 
3.1  |  *  |  *  |  *  |  *


## Requirements

* Django 2.2, 3.0, or 3.1
* Python 3.6, 3.7, 3.8, or 3.9
* django-appconf (included in ``install_requires``)
* pytz (included in ``install_requires``)


## Documentation

See http://django-user-accounts.readthedocs.org/ for the `django-user-accounts` documentation.
On September 17th, 2015, we did a Pinax Hangout on `django-user-accounts`. You can read the recap blog post and find the video here http://blog.pinaxproject.com/2015/10/12/recap-september-pinax-hangout/.

The Pinax documentation is available at http://pinaxproject.com/pinax/. If you would like to help us improve our documentation or write more documentation, please join our Slack team and let us know!


### Templates

Default templates are provided by the `pinax-templates` app in the
[account](https://github.com/pinax/pinax-templates/tree/master/pinax/templates/templates/account) section of that project.

Reference pinax-templates
[installation instructions](https://github.com/pinax/pinax-templates/blob/master/README.md#installation) to include these templates in your project.

View live `pinax-templates` examples and source at [Pinax Templates](https://templates.pinaxproject.com/)!

See the `django-user-accounts` [templates](https://django-user-accounts.readthedocs.io/en/latest/templates.html) documentation for more information.


## Contribute

For an overview on how contributing to Pinax works read this [blog post](http://blog.pinaxproject.com/2016/02/26/recap-february-pinax-hangout/)
and watch the included video, or read our [How to Contribute](http://pinaxproject.com/pinax/how_to_contribute/) section. For concrete contribution ideas, please see our
[Ways to Contribute/What We Need Help With](http://pinaxproject.com/pinax/ways_to_contribute/) section.

In case of any questions we recommend you join our [Pinax Slack team](http://slack.pinaxproject.com) and ping us there instead of creating an issue on GitHub. Creating issues on GitHub is of course also valid but we are usually able to help you faster if you ping us in Slack.

We also highly recommend reading our blog post on [Open Source and Self-Care](http://blog.pinaxproject.com/2016/01/19/open-source-and-self-care/).


## Code of Conduct

In order to foster a kind, inclusive, and harassment-free community, the Pinax Project
has a [code of conduct](http://pinaxproject.com/pinax/code_of_conduct/).
We ask you to treat everyone as a smart human programmer that shares an interest in Python, Django, and Pinax with you.


## Connect with Pinax

For updates and news regarding the Pinax Project, please follow us on Twitter [@pinaxproject](https://twitter.com/pinaxproject) and check out our [Pinax Project blog](http://blog.pinaxproject.com).


## License

Copyright (c) 2012-present James Tauber and contributors under the [MIT license](https://opensource.org/licenses/MIT).
