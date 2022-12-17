# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\locators\locator_tuning.py
# Compiled at: 2020-04-30 12:48:17
# Size of source mod 2**32: 528 bytes
import services, sims4
from sims4.tuning.tunable import TunableReference

class LocatorTuning:
    TARGET_LOCATOR_ID_STAT = TunableReference(description='\n        The stat name used to check for a target locator id on the routing object.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)))