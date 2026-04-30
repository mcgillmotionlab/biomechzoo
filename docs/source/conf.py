import os
import sys
from importlib.metadata import version as _pkg_version

# Make the src/ package importable by Sphinx
sys.path.insert(0, os.path.abspath('../../src'))

# ---------------------------------------------------------------------------
# Project metadata
# ---------------------------------------------------------------------------
project = 'biomechzoo'
copyright = '2026, McGill Motion Lab'
author = 'McGill Motion Lab'
# Automatically read the version from pyproject.toml (via the installed package)
# so you only need to update the version in one place.
release = _pkg_version('biomechzoo')

# ---------------------------------------------------------------------------
# Extensions
# ---------------------------------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',       # Pull docstrings from source code automatically
    'sphinx.ext.napoleon',      # Parse NumPy-style docstrings
    'sphinx.ext.viewcode',      # Add "View source" links on every page
    'sphinx.ext.autosummary',   # Generate summary tables for modules
    'sphinx.ext.intersphinx',   # Cross-reference external docs (NumPy, SciPy…)
    'sphinx_copybutton',        # Add copy button to all code blocks
]

# ---------------------------------------------------------------------------
# Napoleon (NumPy docstring) settings
# ---------------------------------------------------------------------------
napoleon_numpy_docstring = True
napoleon_google_docstring = False
napoleon_include_init_with_doc = False
napoleon_use_param = False       # Keep the Parameters table compact
napoleon_use_rtype = False       # Keep the Returns table compact

# ---------------------------------------------------------------------------
# autodoc settings
# ---------------------------------------------------------------------------
autodoc_default_options = {
    'members': True,             # Document all public members
    'undoc-members': False,      # Skip members without docstrings
    'show-inheritance': True,    # Show base classes
    'member-order': 'bysource',  # Keep the order as written in source
}
autodoc_typehints = 'description'   # Show type hints in the description body

# ---------------------------------------------------------------------------
# intersphinx mapping — lets us link to numpy/scipy docs with :func:`np.array`
# ---------------------------------------------------------------------------
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy':  ('https://numpy.org/doc/stable', None),
    'scipy':  ('https://docs.scipy.org/doc/scipy', None),
}

# ---------------------------------------------------------------------------
# HTML output
# ---------------------------------------------------------------------------
html_theme = 'furo'
templates_path = ['_templates']
html_static_path = []
exclude_patterns = []
