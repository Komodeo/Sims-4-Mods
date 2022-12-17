# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\statistic_types.py
# Compiled at: 2014-01-17 14:08:32
# Size of source mod 2**32: 964 bytes
from sims4.tuning.tunable import Tunable

class StatisticComponentGlobalTuning:
    DEFAULT_RADIUS_TO_CONSIDER_OFF_LOT_OBJECTS = Tunable(description='\n        The radius from the Sim that an off-lot object must be for a Sim to consider it.\n        If the object is not on the active lot and outside of this radius, the Sim will \n        ignore it.\n        ',
      tunable_type=float,
      default=20)
    DEFAULT_OFF_LOT_TOLERANCE = Tunable(description="\n        The tolerance for when a Sim is considered off the lot.  If a Sim is off the \n        lot but within this tolerance, he will be considered on the lot from autonomy's \n        perspective.  Note that this only effects autonomy, nothing else. \n        ",
      tunable_type=float,
      default=5)