#!/usr/bin/env python3

"""
pytri.

look at stuff.
"""

import codecs
import os
import re
from setuptools import setup, find_packages

def read(*parts):
    with codecs.open(os.path.join(HERE, *parts), 'r', encoding='utf-8') as fp:
        return fp.read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    else:
        return "UNKNOWN"

HERE = os.path.abspath(os.path.dirname(__file__))
VERSION = find_version("pytri", "version.py")
LONG_DESCRIPTION = read("README.md")
ALL_REQS = read("requirements.txt").split('\n')

INSTALL_REQUIRES = [x.strip() for x in ALL_REQS if 'git+' not in x]
DEPENDENCY_LINKS = [
    x.strip().replace('git+', '') for x in ALL_REQS if x.startswith('git+')
]

setup(
    name='pytri',
    version=VERSION,
    description='Visualize using substrate. For Jupyter notebooks.',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    download_url='https://github.com/aplbrain/pytri/tarball/' + VERSION,
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords=[
        "viz", "substrate", "3D", "visualization"
    ],
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    author='Jordan Matelsky',
    install_requires=INSTALL_REQUIRES,
    dependency_links=DEPENDENCY_LINKS,
    author_email='jordan@matelsky.com'
)
