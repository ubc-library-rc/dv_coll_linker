'''
Dataverse collection level linking tool dv_coll_linker.

Implements collection level linking even if collection level
linking is non-functional within a Dataverse installation.
'''
import os
import ast

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

init = os.path.join(
    os.path.dirname(__file__), 'dv_coll_linker', '__init__.py')

version_line = list(
    filter(lambda l: l.startswith('VERSION'),
           open(init, encoding='utf-8')))[0].strip()


def get_version(version_tuple):
    '''Get version from module'''
    if not isinstance(version_tuple[-1], int):
        return '.'.join(
            map(str, version_tuple[:-1])
        ) + version_tuple[-1]
    return '.'.join(map(str, version_tuple))

PKG_VERSION = get_version(ast.literal_eval(version_line.split('=')[-1].strip()))
REQUIRES = [req.strip().replace('==',' >= ') for req in
            open('requirements.txt', encoding='utf-8').readlines()]

CONFIG = {
    'description': 'Dataverse collection level linking',
    'author': 'Paul Lesack',
    'license': 'MIT',
    'url': 'https://ubc-library-rc.github.io/dv_coll_linker/',
    'download_url': 'https://github.com/ubc-library-rc/dv_coll_linker',
    'author_email': 'paul.lesack@ubc.ca',
    'classifiers' : ['Development Status :: 4 - Beta',
                     'Intended Audience :: Education',
                     'License :: OSI Approved :: MIT License'
                     'Programming Language :: Python :: 3.6',
                     'Programming Language :: Python :: 3.7',
                     'Programming Language :: Python :: 3.8',
                     'Programming Language :: Python :: 3.9',
                     'Programming Language :: Python :: 3.10',
                     'Topic :: Education'],
    'project_urls' : {'Documentation': 'https://ubc-library-rc.github.io/dv_coll_linker',
                      'Source': 'https://github.com/ubc-library-rc/dv_coll_linker',
                      'Tracker': 'https://github.com/ubc-library-rc/dv_coll_linker/issues'},
    'keywords' : ['Dataverse', 'collections', 'dataverse.org'],
    'version' : PKG_VERSION,
    'python_requires': '>=3.6',
    'install_requires': REQUIRES,
    'packages': ['dv_coll_linker'],
    'name': 'dv_coll_linker',
    'entry_points':  {'console_scripts': ['dv_coll_linker=dv_coll_linker.app:main',
                                          'testme=dv_coll_linker.app:testme']}
}

setup(**CONFIG)
