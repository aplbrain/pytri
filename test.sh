#!/bin/bash

mypy --ignore-missing-imports .
pylint -f colorized -r n pytri
nosetests --with-coverage --with-progressive --cover-package=pytri tests/
