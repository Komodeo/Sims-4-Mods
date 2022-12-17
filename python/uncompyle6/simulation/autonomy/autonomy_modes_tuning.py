# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\autonomy\autonomy_modes_tuning.py
# Compiled at: 2020-06-19 16:17:49
# Size of source mod 2**32: 358 bytes
from sims4.tuning.tunable import TunableSimMinute

class AutonomyModesTuning:
    LOCKOUT_TIME = TunableSimMinute(description='\n        Number of sim minutes to lockout a failed interaction push or routing failure.\n        ',
      default=240)