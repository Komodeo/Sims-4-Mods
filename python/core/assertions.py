# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\assertions.py
# Compiled at: 2015-02-04 14:14:34
# Size of source mod 2**32: 4799 bytes
import functools
from sims4.collections import ListSet
from sims4.repr_utils import standard_repr
import sims4.log
logger = sims4.log.Logger('Assertions')
ENABLE_INTRUSIVE_ASSERTIONS = False

def not_recursive(func):
    return func


def not_recursive_gen(func):
    return func


def hot_path(fn):
    return fn