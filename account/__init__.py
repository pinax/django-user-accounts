try:
	from importlib.metadata import version
except ImportError:
	import pkg_resources
	__version__ = pkg_resources.get_distribution("django-user-accounts").version
else:
	__version__ = version("django-user-accounts")
