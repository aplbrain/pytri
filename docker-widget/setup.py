# -*- coding: utf-8 -*-

from __future__ import print_function
from setuptools import setup, find_packages
import os
import sys

from setupbase import (
    create_cmdclass,
    install_npm,
)


from distutils import log
log.set_verbosity(log.DEBUG)
log.info('setup.py entered')
log.info('$PATH=%s' % os.environ['PATH'])

LONG_DESCRIPTION = 'A jupyter widget for substrate.'


here = os.path.abspath(os.path.dirname(sys.argv[0]))


version_ns = {}
with open(os.path.join(here, 'pytri', '_version.py')) as f:
    exec(f.read(), {}, version_ns)


cmdclass = create_cmdclass(['js'])
cmdclass['js'] = install_npm(
    path=os.path.join(here, 'js'),
    build_dir=os.path.join(here, 'pytri', 'static'),
    source_dir=os.path.join(here, 'js'),
    build_cmd='prepublish'
)

setup_args = {
    'name': 'pytri',
    'version': version_ns['__version__'],
    'description': 'A jupyter-substrate pair.',
    'long_description': LONG_DESCRIPTION,
    'License': '',
    'include_package_data': True,
    'data_files': [
        ('share/jupyter/nbextensions/jupyter-threejs', [
            'pytri/static/extension.js',
            'pytri/static/index.js',
            'pytri/static/index.js.map',
        ]),
    ],
    'install_requires': ['ipywidgets>=7.0.0a9', 'traittypes'],
    'packages': find_packages(),
    'zip_safe': False,
    'cmdclass': cmdclass,
    'author': 'Joseph Downs',
    'author_email': 'Joseph.Downs@jhuapl.edu',
    'url': 'https://github.com/j6k4m8/pytri',
    'keywords': [
        'ipython',
        'jupyter',
        'widgets',
    ],
    'classifiers': [
        'Development Status :: 4 - Beta',
        'Framework :: IPython',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Multimedia :: Graphics',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
}

setup(**setup_args)
