# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\walkstyle\walkstyle_enums.py
# Compiled at: 2017-06-23 15:16:01
# Size of source mod 2**32: 943 bytes
import enum
from sims4.tuning.dynamic_enum import DynamicEnum

class WalkStyleRunAllowedFlags(enum.IntFlags):
    RUN_ALLOWED_INDOORS = 1
    RUN_ALLOWED_OUTDOORS = 2


class WalkstyleBehaviorOverridePriority(DynamicEnum):
    DEFAULT = 0


class WalkStylePriority(DynamicEnum):
    INVALID = 0
    COMBO = 1