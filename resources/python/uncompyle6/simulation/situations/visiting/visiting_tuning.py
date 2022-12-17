# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\visiting\visiting_tuning.py
# Compiled at: 2021-09-01 10:58:18
# Size of source mod 2**32: 942 bytes
from sims4.tuning.tunable import TunableList, TunableReference
import services, sims4.resources

class VisitingTuning:
    ALWAYS_WELCOME_TRAITS = TunableList(description='\n        Traits that will guarantee that after the Sim is welcomed into a \n        household, it will always be automatically welcomed if he/she comes\n        back.\n        i.e. Vampires are always welcomed after being welcomed once.\n        ',
      tunable=TunableReference(description='\n            Trait reference to make the Sim always be welcomed after they \n            are welcomed once.\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.TRAIT)),
      pack_safe=True))