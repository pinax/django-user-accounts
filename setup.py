from setuptools import setup, find_packages

import account


setup(
    name = "django-user-accounts",
    version = account.__version__,
    author = "Brian Rosner",
    author_email = "brosner@gmail.com",
    description = "a Django user account app",
    long_description = open("README.rst").read(),
    license = "MIT",
    url = "http://github.com/pinax/django-user-accounts",
    packages = find_packages(),
    install_requires = [
        "django-appconf==0.6",
        "pytz==2013b"
    ],
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python 3",
        "Framework :: Django",
    ]
)
