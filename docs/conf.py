import os
import sys


extensions = []
templates_path = []
source_suffix = ".rst"
master_doc = "index"
project = u"django-user-accounts"
copyright_holder = "James Tauber and contributors"
copyright = u"2013, {0}",format(copyright_holder)
exclude_patterns = ["_build"]
pygments_style = "sphinx"
html_theme = "default"
htmlhelp_basename = "{0}doc".format(project)
latex_documents = [
  ("index", "{0}.tex".format(project), u"{0} Documentation".format(project),
   "Pinax", "manual"),
]
man_pages = [
    ("index", project, u"{0} Documentation".format(project),
     ["Pinax"], 1)
]

sys.path.insert(0, os.pardir)
m = __import__("account")

version = m.__version__
release = version
