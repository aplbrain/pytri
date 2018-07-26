#!/bin/bash

mypy --ignore-missing-imports .
pylint -r n pytri
echo `which node`
eslint pytri/js
