How to Build the Documentation
================================

This guide explains how the HTML documentation was set up using
`Sphinx <https://www.sphinx-doc.org>`_ and how to rebuild it after making
changes to the source code.

Prerequisites
-------------

You need Python 3 and the packages listed in ``docs/requirements.txt``.
Install them once with::

    pip install -r docs/requirements.txt

Then install the project's own dependencies so that Sphinx can import the
source code and read the docstrings::

    pip install scipy numpy pandas ezc3d matplotlib

Step 1 — Understand the folder layout
--------------------------------------

After setup the ``docs/`` folder looks like this::

    docs/
    ├── Makefile              ← build commands (Linux / macOS)
    ├── requirements.txt      ← Sphinx dependency list
    └── source/
        ├── conf.py           ← Sphinx configuration (theme, extensions, path)
        ├── index.rst         ← documentation home page / table of contents
        └── api/
            ├── index.rst          ← API section table of contents
            ├── biomech_ops.rst    ← one page per module
            ├── processing.rst
            ├── conversion.rst
            ├── imu.rst
            ├── linear_algebra_ops.rst
            ├── statistics.rst
            └── utils.rst

The HTML output is written to ``docs/build/html/``.

Step 2 — How ``conf.py`` works
--------------------------------

``docs/source/conf.py`` is the central configuration file.
The key settings are:

.. code-block:: python

    # Tell Sphinx where the Python source code lives
    sys.path.insert(0, os.path.abspath('../../src'))

    # Extensions used
    extensions = [
        'sphinx.ext.autodoc',    # pulls docstrings automatically
        'sphinx.ext.napoleon',   # understands NumPy-style docstrings
        'sphinx.ext.viewcode',   # adds "View source" links
        'sphinx_copybutton',     # copy button on code blocks
    ]

    # Enable NumPy docstring parsing (not Google style)
    napoleon_numpy_docstring = True
    napoleon_google_docstring = False

    # Visual theme
    html_theme = 'furo'

Step 3 — How ``.rst`` API pages work
--------------------------------------

Each file in ``docs/source/api/`` is a reStructuredText (``.rst``) file that
tells Sphinx which Python modules to document.

The ``.. automodule::`` directive reads every public function's docstring
from the source code and renders it as HTML automatically:

.. code-block:: rst

    .. automodule:: biomechzoo.biomech_ops.filter_data
       :members:

To **add a new module** to the docs:

1. Create (or edit) the relevant ``.rst`` file in ``docs/source/api/``.
2. Add a new ``.. automodule::`` block pointing to the module.
3. Rebuild (see Step 4).

Step 4 — Build the HTML docs
------------------------------

From inside the ``docs/`` directory, run::

    python3 -m sphinx source build/html

Or, if ``sphinx-build`` is available on your PATH, you can use the Makefile::

    cd docs
    make html

Then open the output in a browser::

    open docs/build/html/index.html      # macOS
    start docs/build/html/index.html     # Windows
    xdg-open docs/build/html/index.html  # Linux

Step 5 — Keeping docs in sync with code
-----------------------------------------

Sphinx reads docstrings at **build time**, so the HTML is only updated when
you rebuild.  After changing any docstring or adding a new function:

1. Update or add the docstring in the ``.py`` source file (NumPy style).
2. If the function is in a module already listed in an ``.rst`` file, just
   rebuild — no ``.rst`` changes needed.
3. If it is a **brand new module**, add a ``.. automodule::`` entry in the
   appropriate ``docs/source/api/<section>.rst`` file, then rebuild.

Step 6 — NumPy docstring format (required)
-------------------------------------------

All docstrings must follow NumPy style so that ``sphinx.ext.napoleon`` can
parse them correctly.  Example:

.. code-block:: python

    def my_function(data, mode='remove'):
        """
        Short one-line summary.

        Longer description goes here if needed.

        Parameters
        ----------
        data : dict
            Description of data.
        mode : {'remove', 'keep'}, optional
            Description of mode. Default is 'remove'.

        Returns
        -------
        dict
            Description of return value.

        Raises
        ------
        ValueError
            When mode is invalid.

        Notes
        -----
        Any extra information goes here.
        """
