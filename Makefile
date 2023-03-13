# -*- coding: utf-8 -*-
.PHONY: clean build devdeps

clean:
	rm -rf dist/ build/ *.egg-info/

build: clean
	python setup.py sdist bdist_wheel --universal

devdeps:
	pip install -e .
