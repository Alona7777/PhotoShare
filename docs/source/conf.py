import sys
import os
from pathlib import Path

# sys.path.insert(0, os.path.abspath('__file__'))
base_dir = Path(__file__).parent.parent.parent
# print(base_dir)
# sys.path.abspath(base_dir)
sys.path.insert(0, str(base_dir))
# p = sys.path.insert(0, '..')
# print(p)

project = 'Contact project'
copyright = '2024, Naboka Artem'
author = 'Naboka Artem'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'nature'
html_static_path = ['_static']
