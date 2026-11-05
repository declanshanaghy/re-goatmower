.PHONY: typecheck build test

typecheck:
	mypy tools/

build:
	python3 -m py_compile tools/eco_passwd.py

test:
	@echo "No automated test suite (documentation/research project)"
