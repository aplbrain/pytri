#!/bin/bash

mypy --ignore-missing-imports .
pylint -r n pytri
# nosetests --with-coverage --cover-package=pytri
