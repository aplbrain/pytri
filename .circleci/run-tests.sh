#!/bin/bash

mypy --ignore-missing-imports .
pylint -r n pytri
sudo eslint pytri/js
