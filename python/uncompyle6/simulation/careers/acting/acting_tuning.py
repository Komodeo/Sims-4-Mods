# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\careers\acting\acting_tuning.py
# Compiled at: 2018-04-03 14:58:38
# Size of source mod 2**32: 504 bytes
from sims4.tuning.tunable import TunablePackSafeLotDescription

class ActingTuning:
    STUDIO_LOT_DESCRIPTION = TunablePackSafeLotDescription(description='\n        A reference to the lot description file for the acting studio lot. This\n        is used for easier zone ID lookups.\n        ')