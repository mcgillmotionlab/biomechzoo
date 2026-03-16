How to Build the Documentation
================================

This guide explains how to build the HTML documentation using
`Sphinx <https://www.sphinx-doc.org>`_ and `uv <https://docs.astral.sh/uv/>`_.

Prerequisites
-------------

You need `uv <https://docs.astral.sh/uv/>`_ installed on your machine.
On macOS::

    brew install uv

That's it. uv handles Python, the virtual environment, and all dependencies
for you — no manual ``pip install`` needed.

Quick Start
-----------

Run these two commands from the **project root** (not inside ``docs/``)::

    uv sync --group docs
    make -C docs html

Then open the result in a browser::

    open docs/build/html/index.html      # macOS
    start docs/build/html/index.html     # Windows
    xdg-open docs/build/html/index.html  # Linux

.. note::

   ``uv sync --group docs`` only needs to be run once after cloning the repo,
   or after a new dependency is added to ``pyproject.toml``. After that, just
   run ``make -C docs html`` to rebuild.

Step 1 — How it all fits together
-----------------------------------

Sphinx reads your Python source code at **build time** and turns docstrings
into HTML.  The key files are:

.. code-block:: text

    pyproject.toml            ← version number + docs dependencies live here
    docs/
    ├── Makefile              ← shortcuts: make html / make livehtml / make clean
    └── source/
        ├── conf.py           ← Sphinx configuration (theme, extensions, path)
        ├── index.rst         ← documentation home page / table of contents
        └── api/
            ├── index.rst          ← API section table of contents
            ├── biomech_ops.rst    ← one .rst file per module group
            ├── processing.rst
            ├── conversion.rst
            ├── imu.rst
            ├── linear_algebra_ops.rst
            ├── statistics.rst
            ├── utils.rst
            └── visualization.rst

The HTML output is written to ``docs/build/html/`` (ignored by git).

Step 2 — How dependencies are managed
---------------------------------------

All docs-related packages (``sphinx``, ``furo``, ``sphinx-copybutton``,
``sphinx-autobuild``) are declared in ``pyproject.toml`` under a separate
dependency group so they do not pollute the main project environment:

.. code-block:: toml

    [dependency-groups]
    docs = [
        "sphinx>=7.0",
        "furo>=2024.1.29",
        "sphinx-copybutton>=0.5.2",
        "sphinx-autobuild>=2024.0.0",
    ]

``uv sync --group docs`` installs both the main project dependencies and this
docs group into the ``.venv`` virtual environment automatically.

Step 3 — How ``.rst`` API pages work
--------------------------------------

Each file in ``docs/source/api/`` tells Sphinx which Python modules to
document using the ``.. automodule::`` directive:

.. code-block:: rst

    .. automodule:: biomechzoo.biomech_ops.filter_data
       :members:

Sphinx imports the module, reads every public function's docstring, and
renders it as HTML.

**After adding a new Python module**, you need to register it in the docs:

1. Open the relevant ``docs/source/api/<section>.rst`` file.
2. Add a new ``.. automodule::`` block pointing to the new module.
3. Run ``make -C docs html`` to rebuild.

No ``.rst`` changes are needed if you only edited an existing function's
docstring — just rebuild.

.. _livehtml:

Step 4 — Live preview while editing
-------------------------------------

To automatically rebuild and refresh the browser whenever you save a file::

    make -C docs livehtml

Open ``http://127.0.0.1:8000`` in your browser. The page will refresh
automatically as you edit ``.rst`` files or Python docstrings.

Step 5 — Keeping docs in sync with version updates
----------------------------------------------------

The version number shown in the docs is read **automatically** from the
installed package, so you only need to update it in one place:

1. Change ``version = "x.y.z"`` in ``pyproject.toml``.
2. Run ``uv sync`` (updates the lock file and reinstalls the package).
3. Run ``make -C docs html`` — the new version appears in the docs automatically.

Step 6 — NumPy docstring format (required)
-------------------------------------------

All docstrings must follow NumPy style so that ``sphinx.ext.napoleon`` can
parse them correctly.  Example:

.. code-block:: python

    def my_function(data, mode='remove'):
        """
        Short one-line summary.

        Parameters
        ----------
        data : dict
            Description of data.
        mode : {'remove', 'keep'}, optional
            Description of mode. Default is ``'remove'``.

        Returns
        -------
        dict
            Description of return value.

        Raises
        ------
        ValueError
            When mode is invalid.
        """
