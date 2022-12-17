# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\occult\occult_tuning.py
# Compiled at: 2016-08-22 15:48:09
# Size of source mod 2**32: 402 bytes
from traits.traits import Trait

class OccultTuning:
    NO_OCCULT_TRAIT = Trait.TunableReference(description='\n        The trait that indicates a sim has no occult type.\n        ')