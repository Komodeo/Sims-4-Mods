# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\celebrity_fans\fan_tuning.py
# Compiled at: 2018-07-26 15:06:03
# Size of source mod 2**32: 2242 bytes
from sims4.resources import Types
from sims4.tuning.tunable import TunablePackSafeReference, TunableSet, TunableReference
from sims4.utils import classproperty
from tag import TunableTag
import services

class FanTuning:
    FANNABLE_CELEBRITY_SITUATION = TunablePackSafeReference(description='\n        Situation that will store all celebrity Sims that can be used to\n        spawn fan or stan situations. \n        ',
      manager=(services.get_instance_manager(Types.SITUATION)),
      class_restrictions='FannableCelebritySimsSituation')
    FAN_TARGETTING_TAG = TunableTag(description='\n        Tag applied to celebrities that can be targeted by fans.\n        \n        Used in conjunction with autonomy modifiers so we can consider\n        celebrities without caring about whether or not they are on or off lot.\n        ',
      filter_prefixes=('Func', ))
    FAN_SITUATION_TAG = TunableTag(description='\n        Tag which delineates which situations are fan situations.\n        ',
      filter_prefixes=('Situation', ))
    STAN_DISABLING_BITS = TunableSet(description='\n        Rel bits, which if any are found on the stan, prevents the stan\n        from kicking off their situation. \n        \n        Used to prevent a stan from being too stanny. \n        ',
      tunable=TunableReference((services.get_instance_manager(Types.RELATIONSHIP_BIT)),
      pack_safe=True))
    STAN_FILTER = TunablePackSafeReference(description='\n        Filter used to find the stan for a given Sim.  This should \n        only contain the minimum required filter terms for a Stan.\n        ',
      manager=(services.get_instance_manager(Types.SIM_FILTER)))
    STAN_PERK = TunablePackSafeReference(description='\n        Perk used to determine if a Sim is stannable.\n        ',
      manager=(services.get_instance_manager(Types.BUCKS_PERK)))

    @classproperty
    def are_fans_supported(cls):
        return cls.FANNABLE_CELEBRITY_SITUATION is not None