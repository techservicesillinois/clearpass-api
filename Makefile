VENV_PYTHON:=venv/bin/python
VENV_REQS:=.requirements.venv
SRCS:=$(shell find src tests -name '*.py')

all: test

# BSD `sed` treats the `-i` option differently than Linux and others.
# Check for Mac OS X 'Darwin' and set our `-i` option accordingly.
ifeq ($(UNAME), Darwin)
# macOS (BSD sed)
	SED_INPLACE := -i ''
else
# Linux and others (GNU sed)
	SED_INPLACE := -i
endif

venv: requirements-test.txt
	rm -rf $@
	python -m venv venv
	$(VENV_PYTHON) -m pip install -r requirements-test.txt
# Install dependencies from pyproject.toml
	$(VENV_PYTHON) -m pip install -e .
	

requirements-test.txt: export VCR_CLEANER_REPO=git+https://github.com/techservicesillinois/vcrpy-cleaner.git
requirements-test.txt: requirements-test.in
	rm -rf $(VENV_REQS)
	python -m venv $(VENV_REQS)
	# Workaround for wheel install failures.
	$(VENV_REQS)/bin/python -m pip install --upgrade pip
	$(VENV_REQS)/bin/python -m pip install -r $^
	$(VENV_REQS)/bin/python -m pip freeze -qqq > $@
	sed $(SED_INPLACE) "s;^vcr-cleaner==.*;$(VCR_CLEANER_REPO);" $@

lint: venv .lint
.lint: $(SRCS) $(TSCS)
	$(VENV_PYTHON) -m flake8 $?
	touch $@

static: venv .static
.static: $(SRCS) $(TSCS)
	echo "Code: $(SRCS)"
	echo "Test: $(TSCS)"
	$(VENV_PYTHON) -m mypy $^
	touch $@

autopep8:
	autopep8 --in-place $(SRCS)

unit: venv
	$(VENV_PYTHON) -m pytest

test: lint static unit

clean:
	rm -rf venv $(VENV_REQS)
	rm -rf .lint .static
	rm -rf .mypy_cache
	-find src -type d -name __pycache__ -exec rm -fr "{}" \;

force-clean: clean
	rm -f requirements-test.txt