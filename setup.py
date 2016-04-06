#!/usr/bin/env python

import sys
from setuptools import setup, find_packages

setup(name='heroprotocol',
      version='41810',
      author='Blizzard',
      url='http://github.com/Blizzard/heroprotocol',
      description='Python library to decode Heroes of the Storm replay protocols',
      packages=find_packages(exclude=['ez_setup', 'tests', 'tests.*']),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Games/Entertainment :: Real Time Strategy',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Archiving',
      ],
      install_requires=['argparse', 'six'] if float(sys.version[:3]) < 2.7 else ['six'],)
