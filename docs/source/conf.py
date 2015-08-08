# -*- coding: utf-8 -*-
import os
import sys

import mock

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
intersphinx_mapping = {'python': ('http://docs.python.org/2.7', None),
                       'pyside': ('https://deptinfo-ensip.univ-poitiers.fr/ENS/pyside-docs/', None)}

autosummary_generate = True

# -- Jinjaapidoc Config ---------------------------------------------------

jinjaapi_srcdir = os.path.abspath(os.path.join(thisdir, '..', '..', 'src'))
jinjaapi_outputdir = os.path.abspath(os.path.join(thisdir, 'reference'))
jinjaapi_nodelete = False
jinjaapi_addsummarytemplate = False


class Mock(mock.Mock):

    @classmethod
    def mock_modules(cls, *modules):
        for module in modules:
            sys.modules[module] = cls()

    def __init__(self, *args, **kwargs):
        super(Mock, self).__init__()

    def __call__(self, *args, **kwargs):
        return Mock()

    def __getattr__(self, attribute):
        try:
            attr = super(Mock, self).__getattr__(attribute)
            if not isinstance(attr, mock.Mock):
                return attr
        except AttributeError:
            pass
        if attribute in ('__file__', '__path__'):
            return os.devnull
        else:
            # return the *class* object here.  Mocked attributes may be used as
            # base class in pydev code, thus the returned mock object must
            # behave as class, or else Sphinx autodoc will fail to recognize
            # the mocked base class as such, and "autoclass" will become
            # meaningless
            if attribute[0].capitalize() == attribute[0] and\
               attribute not in ['QtGui', 'QtCore']:
                cls = Mock
            else:
                cls = Mock()
            return cls

import os
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
if on_rtd:
    # mock out native modules used throughout pyudev to enable Sphinx autodoc even
    # if these modules are unavailable, as on readthedocs.org
    Mock.mock_modules('PySide', 'PySide.QtCore', 'PySide.QtGui',)
