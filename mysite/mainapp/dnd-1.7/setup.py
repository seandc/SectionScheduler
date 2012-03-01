#!/usr/bin/env python
##
## Name:     setup.py
## Purpose:  Install DND library.
## Author:   M. J. Fromberger <http://www.dartmouth.edu/~sting/>
## Info:     $Id: setup.py 437 2006-08-13 21:56:07Z sting $
##
## Standard usage:  python setup.py install
##
from distutils.core import setup
from dnd import __version__ as lib_version

setup(name = 'dnd',
      version = lib_version,
      description = 'Dartmouth Name Directory client library',
      long_description = """
Implements a client for the Dartmouth Name Directory (DND), a central
database of public user information used by the BlitzMail system
developed at Dartmouth College.  While not widely used, this protocol
may be of interest to developers at those sites that do use BlitzMail.
""",
      author = 'M. J. Fromberger',
      author_email = "michael.j.fromberger@gmail.com",
      url = 'http://www.cs.dartmouth.edu/~sting/sw/#dnd',
      classifiers = ['Development Status :: 5 - Production/Stable',
                     'Intended Audience :: Developers',
                     'License :: Freeware',
                     'Operating System :: OS Independent',
                     'Programming Language :: Python',
                     'Topic :: Internet',
                     'Topic :: Software Development :: ' \
                     'Libraries :: Python Modules'],
      py_modules = [ 'dnd' ],
      scripts = ['dndedit', 'dndquery', 'groupedit', 'makelist',
                 'scrapeclass'])

# Here there be dragons
      
