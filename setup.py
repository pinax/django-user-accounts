from setuptools import setup, find_packages


setup(
    name = "django-user-accounts",
    version = "1.0b1.dev1",
    author = "Brian Rosner",
    author_email = "brosner@gmail.com",
    description = "a Django user account app",
    long_description = open("README.rst").read(),
    license = "MIT",
    url = "http://github.com/pinax/django-user-accounts",
    packages = find_packages(),
    install_requires = [
        "django-appconf==0.5",
        "pytz==2012b"
    ],
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ]
)
