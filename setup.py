#!/usr/bin/env python3
"""
Flask-Websockets enables Flask-style use of gevent-websockets.
"""

import re
from setuptools import setup

from pathlib import Path

version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                    Path('flask_websockets.py').read_text(),
                    re.MULTILINE).group(1)
repository = 'https://github.com/shoeffner/Flask-Websockets'

setup(
    name='Flask-Websockets',
    version=version,
    description=__doc__,
    long_description=Path('README.rst').read_text(),
    author='Sebatian Höffner',
    author_email='info@sebastian-hoeffner.de',
    url=repository,
    download_url='{}/tarball/{}'.format(repository, version),
    py_modules=['flask_websockets'],
    include_package_data=True,
    platforms='any',
    python_requires=">= 3.6",
    install_requires=[
        'Flask',
        'gevent-websocket',
    ],
    license='MIT',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords=[
        'flask', 'websockets', 'sockets'
    ],
)
