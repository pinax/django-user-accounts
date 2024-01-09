import datetime
import os
import sys


extensions = []
templates_path = []
source_suffix = ".rst"
master_doc = "index"
project = "django-user-accounts"
copyright_holder = "James Tauber and contributors"
copyright = f"{datetime.datetime.now().year}, {copyright_holder}"
exclude_patterns = ["_build"]
pygments_style = "sphinx"
html_theme = "default"
htmlhelp_basename = f"{project}doc"
latex_documents = [
  ("index", f"{project}.tex", f"{project} Documentation",
   "Pinax", "manual"),
]
man_pages = [
    ("index", project, f"{project} Documentation",
     ["Pinax"], 1)
]

sys.path.insert(0, os.pardir)
m = __import__("account")

version = m.__version__
release = version
