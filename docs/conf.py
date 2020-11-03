from pallets_sphinx_themes import get_version
from pallets_sphinx_themes import ProjectLink

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'Flask-Websockets'
copyright = '2020, Sebastian Höffner'
author = 'Sebastian Höffner'
release, version = get_version('Flask-Websockets')


# -- General configuration ---------------------------------------------------

master_doc = "index"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "pallets_sphinx_themes"
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "flask": ("https://flask.palletsprojects.com/", None),
    "werkzeug": ("https://werkzeug.palletsprojects.com/", None),
}

html_context = {
    "project_links": [
        ProjectLink("Flask-Websockets Website", "https://Flask-Websockets.readthedocs.io/en/latest/"),
        # ProjectLink("PyPI releases", "https://pypi.org/project/Flask-Websockets/"),
        ProjectLink("Source Code", "https://github.com/shoeffner/Flask-Websockets/"),
        ProjectLink("Issue Tracker", "https://github.com/shoeffner/Flask-Websockets/issues/"),
        ProjectLink("Flask Website", "https://palletsprojects.com/p/flask/"),
    ]
}

html_sidebars = {
    "**": ["project.html", "localtoc.html", "relations.html", "searchbox.html"],
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

html_theme = 'flask'
html_title = f"Flask Documentation ({version})"
html_static_path = ['_static']
