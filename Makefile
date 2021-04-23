# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = docsrc
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
default:
	@echo "make docs - generate documentation (in docs) and update Git index for it"
	@echo "make help - help for sphinx-build command"
	@echo "make test - run unittest (see jenni/tests folder)"
	@echo "Otherwise pass arguments to sphinx-build command"

docs: html
	git add -u docs
	git add -f docs
	git status

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

test:
	python3 -m unittest discover -s jenni/tests

.PHONY: bandit help Makefile test

html: Makefile
	rm -rf docs
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	mv "$(BUILDDIR)"/html docs
	touch docs/.nojekyll

bandit: venv Makefile
	venv/bin/bandit --exclude jenni/tests -r jenni

venv: requirements_dev.txt
	if ! [ -d venv ]; then python3 -m venv venv; venv/bin/pip install -U pip; fi
	venv/bin/pip install -r requirements_dev.txt

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
#%: Makefile
%::
	$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
