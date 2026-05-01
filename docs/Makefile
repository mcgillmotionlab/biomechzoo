# Minimal Makefile for Sphinx documentation
#
# Usage (from the project root, using uv — no manual pip install needed):
#   make -C docs html      — build HTML docs into docs/build/html/
#   make -C docs clean     — remove the build directory
#   make -C docs livehtml  — auto-rebuild on file changes (serves at http://127.0.0.1:8000)
#
# uv automatically installs sphinx and related tools from the [dependency-groups] docs
# section in pyproject.toml. No need to run `pip install -r requirements.txt` manually.

SPHINXOPTS    ?=
SPHINXBUILD   ?= uv run --extra docs sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

.PHONY: help html clean livehtml

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

html:
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo ""
	@echo "Build finished. Open build/html/index.html to view the docs."

clean:
	@$(SPHINXBUILD) -M clean "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

livehtml:
	uv run --group docs sphinx-autobuild "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)
