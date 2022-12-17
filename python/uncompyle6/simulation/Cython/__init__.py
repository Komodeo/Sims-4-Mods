# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\Cython\__init__.py
# Compiled at: 2020-02-05 19:30:39
# Size of source mod 2**32: 370 bytes
from __future__ import absolute_import
from .Shadow import __version__
from .Shadow import *

def load_ipython_extension(ip):
    from Build.IpythonMagic import CythonMagics
    ip.register_magics(CythonMagics)