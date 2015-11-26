PY_FILES = $(shell find thinkhazard_common -type f -name '*.py' 2> /dev/null)

.PHONY: all
all: help

.PHONY: help
help:
	@echo "Usage: make <target>"
	@echo
	@echo "Possible targets:"
	@echo
	@echo "- check                   Check the code with flake8"
	@echo

.PHONY: check
check: flake8

.PHONY: flake8
flake8: .build/dev-requirements.timestamp .build/flake8.timestamp

.build/venv:
	mkdir -p $(dir $@)
	# make a first virtualenv to get a recent version of virtualenv
	virtualenv venv
	venv/bin/pip install virtualenv
	venv/bin/virtualenv .build/venv
	# remove the temporary virtualenv
	rm -rf venv

.build/dev-requirements.timestamp: .build/venv dev-requirements.txt
	mkdir -p $(dir $@)
	.build/venv/bin/pip install -r dev-requirements.txt > /dev/null 2>&1
	touch $@

.build/flake8.timestamp: $(PY_FILES)
	mkdir -p $(dir $@)
	.build/venv/bin/flake8 $?
	touch $@

.PHONY: clean
clean:
	rm -f .build/flake8.timestamp

.PHONY: cleanall
cleanall:
	rm -rf .build
