# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\cython_utils.py
# Compiled at: 2021-02-23 13:06:48
# Size of source mod 2**32: 644 bytes
import cython, sims4.log
from postures.posture_specs import cython_log
from sims4.log import Logger
logger = Logger('CythonUtils')
if cython.compiled:
    cython_log.always('CYTHON cython_utils is imported!', color=(sims4.log.LEVEL_WARN))
else:
    cython_log.always('Pure Python cython_utils is imported!', color=(sims4.log.LEVEL_WARN))
if not cython.compiled:
    from cython_utils_ph import *