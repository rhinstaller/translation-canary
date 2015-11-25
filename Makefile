# This Makefile is just for running the tests

all:
	@echo "nothing to build"

check:
	tests/pylint/runpylint.py
