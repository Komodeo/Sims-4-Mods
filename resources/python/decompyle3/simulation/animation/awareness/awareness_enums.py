# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\animation\awareness\awareness_enums.py
# Compiled at: 2016-07-25 12:29:27
# Size of source mod 2**32: 1449 bytes
from sims4.tuning.dynamic_enum import DynamicEnum
import enum

class AwarenessChannel(DynamicEnum, dynamic_max_length=10, dynamic_offset=1000):
    PROXIMITY = 0
    AUDIO_VOLUME = 1

    def get_type_name(self):
        return str(self).split('.')[-1].lower()


class AwarenessChannelEvaluationType(enum.Int):
    PEAK = 0
    AVERAGE = 1
    SUM = 2