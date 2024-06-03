VENV_PYTHON:=venv/bin/python
VENV_REQS:=.requirements.venv/bin
SRCS:=$(shell find src tests -name '*.py')

all: test

venv: requirements-dev.txt
	rm -rf $@
	python -m venv $@
	$(VENV_PYTHON) -m pip install -r $^

requirements-test.txt:
	python -m venv $(VENV_REQS)
	$(VENV_REQS)/bin/pip install -r requirements-test.in
	$(VENV_REQS)/bin/pip freeze -qqq > $@

test: static

static: $(SRCS)
	mypy $^
	touch $@

clean:
	rm -f static

force-clean: clean
	rm -f requirements-test.txt
	rm -rf venv
