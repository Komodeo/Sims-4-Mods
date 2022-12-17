# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\carry\carry_tuning.py
# Compiled at: 2017-04-17 13:28:51
# Size of source mod 2**32: 788 bytes
from sims4.tuning.tunable import TunableReference
import services, sims4.resources

class CarryPostureStaticTuning:
    POSTURE_CARRY_NOTHING = TunableReference(description='\n            Reference to the posture that represents carrying nothing\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.POSTURE)),
      class_restrictions='CarryingNothing')
    POSTURE_CARRY_OBJECT = TunableReference(description='\n        Reference to the posture that represents carrying an Object\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.POSTURE)),
      class_restrictions='CarryingObject')