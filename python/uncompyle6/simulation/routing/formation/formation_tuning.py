# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\formation\formation_tuning.py
# Compiled at: 2018-08-29 16:51:24
# Size of source mod 2**32: 715 bytes
from sims4.tuning.tunable import TunableRange

class FormationTuning:
    GOAL_HEIGHT_LIMIT = TunableRange(description='\n        Max value in meters between the height of the formation master and\n        the goals generated by a routing slave.\n        If the goals have a height different higher than this value, they\n        will be ignored even though the could be inside the valid constraint\n        around the master.\n        ',
      tunable_type=float,
      default=0.5,
      minimum=0)