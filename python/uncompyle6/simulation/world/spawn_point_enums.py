# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\world\spawn_point_enums.py
# Compiled at: 2016-08-31 15:09:28
# Size of source mod 2**32: 627 bytes
from sims4.tuning.dynamic_enum import DynamicEnum
import enum

class SpawnPointPriority(DynamicEnum):
    DEFAULT = 0


class SpawnPointRequestReason(enum.Int):
    DEFAULT = 0
    SPAWN = 1
    LEAVE = 2