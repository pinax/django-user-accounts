from __future__ import unicode_literals

import os
import sys


extensions = []
templates_path = []
source_suffix = ".rst"
master_doc = "index"
project = "django-user-accounts"
copyright_holder = "James Tauber and contributors"
copyright = "2014, {0}".format(copyright_holder)
exclude_patterns = ["_build"]
pygments_style = "sphinx"
html_theme = "default"
htmlhelp_basename = "{0}doc".format(project)
latex_documents = [
  ("index", "{0}.tex".format(project), "{0} Documentation".format(project),
   "Pinax", "manual"),
]
man_pages = [
    ("index", project, "{0} Documentation".format(project),
     ["Pinax"], 1)
]

sys.path.insert(0, os.pardir)
m = __import__("account")

version = m.__version__
release = version
