import os
import sys
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Virtual Machine Deployment'
copyright = '2024, Mira Security'
author = 'Mira Security'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',  # Automatically document Python modules
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',  # Support for Google and NumPy docstrings
    'm2r2',
]
source_suffix = ['.rst', '.md']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Paths to individual Python files to document
autodoc_member_order = 'bysource'
autodoc_default_flags = ['members', 'undoc-members', 'private-members']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Options for sphinx.ext.autodoc ------------------------------------------

autodoc_member_order = 'bysource'

# -- Options for sphinx_ansi -------------------------------------------------

ansi_roles = True  # Enable support for Ansible roles

# -- Options for napoleon ----------------------------------------------------

# Use Google-style docstrings for Python
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
# sys.path.insert(0, os.path.abspath('..'))
# Add the parent directory to the Python path to access code
code_dir = os.path.abspath('../../')
sys.path.insert(0, code_dir)
# The master toctree document.

# -- Options for intersphinx extension ---------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {'https://docs.python.org/': None}

# -- Extension configuration -------------------------------------------------

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']
