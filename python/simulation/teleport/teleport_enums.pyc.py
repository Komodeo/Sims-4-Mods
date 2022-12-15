# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\teleport\teleport_enums.py
# Compiled at: 2019-07-08 11:59:27
# Size of source mod 2**32: 651 bytes
from sims4.tuning.dynamic_enum import DynamicEnum
import enum

class TeleportStyle(DynamicEnum, partitioned=True):
    NONE = 0


class TeleportStyleSource(enum.Int, export=False):
    TUNED_LIABILITY = 0
    TELEPORT_STYLE_SUPER_INTERACTION = 1