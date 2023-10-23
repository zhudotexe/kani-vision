# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import sys

# ensure kani is available in path
sys.path.append("..")

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "kani-vision"
copyright = "2023, Andrew Zhu"
author = "Andrew Zhu"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.githubpages",
    "sphinx.ext.viewcode",
    "sphinxext.opengraph",  # https://sphinxext-opengraph.readthedocs.io/en/latest/
    "sphinx_inline_tabs",  # https://sphinx-inline-tabs.readthedocs.io/en/latest/usage.html
    "sphinx_copybutton",  # https://sphinx-copybutton.readthedocs.io/en/latest/
    "sphinxemoji.sphinxemoji",  # https://sphinxemojicodes.readthedocs.io/en/stable/
    "sphinx_sitemap",  # https://sphinx-sitemap.readthedocs.io/en/latest/getting-started.html
    "myst_parser",  # https://myst-parser.readthedocs.io/en/latest/intro.html#enable-myst-in-sphinx
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

maximum_signature_line_length = 120

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
html_extra_path = ["_extra"]
html_logo = "_static/kani-vision-logo.png"
html_favicon = "_extra/favicon.ico"
html_baseurl = "https://kani-vision.readthedocs.io/en/latest/"

nitpicky = True
nitpick_ignore_regex = [
    (r"py:class", r"aiohttp\..*"),  # aiohttp intersphinx is borked
    (r"py:class", r"torch\..*"),  # idk if torch has intersphinx
]

# sphinx.ext.autodoc
autoclass_content = "both"
autodoc_member_order = "bysource"
autodoc_default_options = {
    "exclude-members": "model_config, model_fields",
}

# sphinx.ext.intersphinx
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "kani": ("https://kani.readthedocs.io/en/latest", None),
    "Pillow": ("https://pillow.readthedocs.io/en/latest", None),
}

# sphinxext.opengraph
ogp_social_cards = {
    "enable": False,  # the bundled Roboto font does not support kanji
}

# sphinx_copybutton
copybutton_exclude = ".linenos, .gp, .go"
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True
copybutton_copy_empty_lines = False

# sphinxemoji.sphinxemoji
sphinxemoji_style = "twemoji"

# sphinx_sitemap
sitemap_url_scheme = "{link}"
