from setuptools import setup, find_packages


setup(
    name="django-user-accounts",
    version="2.0.3",
    author="Brian Rosner",
    author_email="brosner@gmail.com",
    description="a Django user account app",
    long_description=open("README.rst").read(),
    license="MIT",
    url="http://github.com/pinax/django-user-accounts",
    packages=find_packages(),
    install_requires=[
        "Django>=1.8",
        "django-appconf>=1.0.1",
        "pytz>=2015.6"
    ],
    zip_safe=False,
    package_data={
        "account": [
            "locale/*/LC_MESSAGES/*",
        ],
    },
    extras_require={
        "pytest": ["pytest", "pytest-django"]
    },
    test_suite="runtests.runtests",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Framework :: Django",
    ]
)
