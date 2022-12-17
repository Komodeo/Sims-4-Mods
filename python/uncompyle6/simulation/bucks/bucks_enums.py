# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\bucks\bucks_enums.py
# Compiled at: 2016-08-01 18:02:05
# Size of source mod 2**32: 567 bytes
from sims4.tuning.dynamic_enum import DynamicEnumLocked
import enum

class BucksType(DynamicEnumLocked, partitioned=True):
    INVALID = 0


class BucksTrackerType(enum.Int):
    HOUSEHOLD = 0
    CLUB = 1
    SIM = 2