# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\animation\focus\focus_tuning.py
# Compiled at: 2016-04-14 11:58:15
# Size of source mod 2**32: 1009 bytes
from sims4.tuning.dynamic_enum import DynamicEnum
from sims4.tuning.tunable import TunableMapping, TunableRange

class FocusScore(DynamicEnum):
    NONE = 0


class FocusTuning:
    FOCUS_SCORE_VALUES = TunableMapping(description='\n        A mapping of focus score to their numerical representation.\n        ',
      key_type=FocusScore,
      value_type=TunableRange(description='\n            The value associated with this focus score. Sims chose what to focus\n            on based on the weighted randomization of all objects they could\n            choose to focus on.\n            ',
      tunable_type=float,
      default=1,
      minimum=0))