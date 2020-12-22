from setuptools import find_packages, setup

setup(
    name="django-user-accounts",
    version="3.0.2",
    author="Brian Rosner",
    author_email="brosner@gmail.com",
    description="a Django user account app",
    long_description=open("README.md").read(),
    license="MIT",
    url="http://github.com/pinax/django-user-accounts",
    packages=find_packages(),
    install_requires=[
        "Django>=2.2",
        "django-appconf>=1.0.4",
        "pytz>=2020.4"
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
        "Framework :: Django",
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ]
)
