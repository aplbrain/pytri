#!/bin/bash

mypy --ignore-missing-imports .
pylint -r n pytri
eslint pytri/js --ignore-pattern '*.min.js'
