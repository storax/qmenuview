# -*- coding: utf-8 -*-
import os
import sys

import sphinx_rtd_theme

thisdir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(thisdir, '../src')))

# -- General configuration -----------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    'jinjaapidoc',
    'sphinx.ext.autodoc',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autosummary',
]
if os.getenv('SPELLCHECK'):
    extensions += 'sphinxcontrib.spelling',
    spelling_show_suggestions = True
    spelling_lang = 'en_US'

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

# General information about the project.
project = u'Pyside QMenuView'
copyright = u'2015, David Zuber'

version = '0.1.0'
release = '0.1.0'

exclude_patterns = ['_build']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# -- Options for HTML output ---------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = ['_static']
# Output file base name for HTML help builder.
htmlhelp_basename = 'qmenuviewdoc'

# -- Options for LaTeX output --------------------------------------------------

latex_elements = {
# The paper size ('letterpaper' or 'a4paper').
#'papersize': 'letterpaper',

# The font size ('10pt', '11pt' or '12pt').
#'pointsize': '10pt',

# Additional stuff for the LaTeX preamble.
#'preamble': '',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
  ('index', 'qmenuview.tex', u'Pyside QMenuView Documentation',
   u'David Zuber', 'manual'),
]


# -- Autodoc Config -------------------------------------------------------

autoclass_content = 'class'  # include __init__ docstring
autodoc_member_order = 'bysource'
autodoc_default_flags = ['members', 'undoc-members', 'show-inheritance']


# -- Intersphinx Config ---------------------------------------------------
intersphinx_mapping = {'python': ('http://docs.python.org/2.7', None)}

autosummary_generate = True

# -- Jinjaapidoc Config ---------------------------------------------------

jinjaapi_srcdir = os.path.abspath(os.path.join(thisdir, '..', '..', 'src'))
jinjaapi_outputdir = os.path.abspath(os.path.join(thisdir, 'source', 'reference'))
jinjaapi_nodelete = False
