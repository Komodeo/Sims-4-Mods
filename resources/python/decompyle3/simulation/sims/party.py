# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\party.py
# Compiled at: 2014-06-07 14:16:44
# Size of source mod 2**32: 779 bytes
from interactions import ParticipantType
from sims4.tuning.tunable import TunableList
from statistics.statistic_ops import TunableStatisticChange

class Party:
    RALLY_FALSE_ADS = TunableList(description=' \n        A list of false advertisement for rallyable interactions. Use this\n        tunable to entice Sims to autonomously choose rallyable over non-\n        rallyable interactions.\n        ',
      tunable=TunableStatisticChange(locked_args={'subject':ParticipantType.Actor,  'advertise':True}))