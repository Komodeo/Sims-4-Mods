# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\whims\whim.py
# Compiled at: 2022-07-21 18:49:30
# Size of source mod 2**32: 4279 bytes
import services, sims4
from objects.mixins import SuperAffordanceProviderMixin, TargetSuperAffordanceProviderMixin
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import TunableReference, TunableEnumEntry, Tunable, OptionalTunable, TunableList, TunableTuple
from statistics.commodity import Commodity
from whims.whims_tracker import WhimType
logger = sims4.log.Logger('Whims', default_owner='mjuskelis')

class TunableWeightedWhimCollection(TunableList):

    def __init__(self, **kwargs):
        super().__init__(description='\n            List of weighted whims.\n            ',
          tunable=(TunableWeightedWhimReference()))

    def entries_by_whim_type_gen(self, whim_type):
        for entry in self:
            if entry is not None:
                if entry.whim is not None:
                    if entry.whim.type is whim_type:
                        yield entry


class TunableWeightedWhimReference(TunableTuple):

    def __init__(self, **kwargs):
        super().__init__(weight=Tunable(description='\n                A higher number means a higher chance of being selected.\n                ',
          tunable_type=float,
          default=1.0),
          whim=TunableReference(description='\n                The whim that will be used when selecting this entry.\n                ',
          manager=(services.get_instance_manager(sims4.resources.Types.WHIM)),
          pack_safe=True))


class Whim(SuperAffordanceProviderMixin, TargetSuperAffordanceProviderMixin, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.WHIM)):
    INSTANCE_TUNABLES = {'goal':TunableReference(description='\n            The goal for this whim.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.SITUATION_GOAL)), 
     'type':TunableEnumEntry(description='\n            The type of whim that this whim is.\n            ',
       tunable_type=WhimType,
       default=WhimType.INVALID,
       invalid_enums=(
      WhimType.INVALID,)), 
     'fluff_description':TunableLocalizedStringFactory(description='\n            A description of the whim from the owning sim\'s perspective.\n            For example, if the whim is "buy a pool", the fluff description might be\n            "I\'ve always wanted to swim in my own backyard. I should get a pool."\n            '), 
     'chaining_whimset_chance_multiplier':OptionalTunable(description='\n            When this whim completes and if this field is tuned,\n            we will multiply this whim\'s source whimset\'s\n            \'chance to be picked\' by this multiplier. This\n            allows us to have a higher chance of "chaining"\n            whims from the same whimset, without outright\n            forcing it.\n            ',
       tunable=Tunable(description="\n                The multiplier to apply to the whimset's\n                'chance to be picked'.\n                ",
       tunable_type=float,
       default=1.0)), 
     'commodity':OptionalTunable(description='\n            If set, this whim will give a commodity when enabled.\n            ',
       tunable=Commodity.TunableReference())}

    @classmethod
    def _verify_tuning_callback(cls):
        if cls.commodity:
            if cls.commodity.persisted_tuning:
                logger.error('Commodity {0} tuned in whim {1} should not be set to persist.', cls.commodity, cls)