#!/usr/bin/env python
from setuptools import setup

VERSION = "0.1.0"

setup(name="wsppy",
       version=VERSION,
       author="Luke Wahlmeier",
       author_email="lwahlmeier@gmail.com",
       url="http://lwahlmeier.github.io/wsppy/",
       download_url="https://github.com/lwahlmeier/wsppy/tarball/%s"%(VERSION),
       license="unlicense",
       description="Simple websocket frame parser",
       keywords=['websockets'],
       classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        'License :: Public Domain'
        ],
       py_modules=['wsspy'],
       test_suite='tests',
      )
