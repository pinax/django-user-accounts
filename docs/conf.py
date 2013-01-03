import os
import sys


extensions = []
templates_path = []
source_suffix = ".rst"
master_doc = "index"
project = u"django-user-accounts"
copyright_holder = "James Tauber and contributors"
copyright = u"2013, %s" % copyright_holder
exclude_patterns = ["_build"]
pygments_style = "sphinx"
html_theme = "default"
htmlhelp_basename = "%sdoc" % project
latex_documents = [
  ("index", "%s.tex" % project, u"%s Documentation" % project,
   "Pinax", "manual"),
]
man_pages = [
    ("index", project, u"%s Documentation" % project,
     ["Pinax"], 1)
]

sys.path.insert(0, os.pardir)
m = __import__("account")

version = m.__version__
release = version
