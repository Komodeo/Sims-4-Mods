# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\carry\put_down_strategy.py
# Compiled at: 2019-01-16 18:59:06
# Size of source mod 2**32: 5644 bytes
from sims.sim_info_types import Species
from sims4.tuning.instances import TunedInstanceMetaclass
from sims4.tuning.tunable import HasTunableReference, OptionalTunable, Tunable, TunableList, TunableReference, TunableMapping, TunableEnumEntry, AutoFactoryInit, HasTunableSingletonFactory, TunableVariant, TunableRange
from singletons import DEFAULT
import services, sims4.resources

class PutDownStrategyOverride(HasTunableSingletonFactory, AutoFactoryInit):

    class _TunablePutDownOverrideVariant(TunableVariant):

        def __init__(self, *args, **kwargs):
            (super().__init__)(args, cost_override=TunableRange(description="\n                    A cost multiplier to apply to the generic cost. A multiplier\n                    that's less than 1 makes the choice more optimal, while a\n                    multiplier greater than 1 makes the choice less optimal.\n                    ",
  tunable_type=float,
  minimum=0,
  default=1), 
             locked_args={'dont_override':DEFAULT, 
 'disallow':None, 
 'heavily_discouraged':100}, 
             default='dont_override', **kwargs)

    FACTORY_TUNABLES = {'slot_cost_override':_TunablePutDownOverrideVariant(), 
     'object_inventory_cost_override':_TunablePutDownOverrideVariant()}


class PutDownStrategy(HasTunableReference, metaclass=TunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.STRATEGY)):
    INSTANCE_TUNABLES = {'preferred_slot_cost':OptionalTunable(enabled_by_default=True,
       tunable=Tunable(description='\n                Base cost for a slot that this object prefers.\n                ',
       tunable_type=float,
       default=0)), 
     'normal_slot_cost':OptionalTunable(enabled_by_default=True,
       tunable=Tunable(description='\n                Base score for a slot that this object does not prefer.\n                ',
       tunable_type=float,
       default=1)), 
     'object_inventory_cost':OptionalTunable(enabled_by_default=True,
       tunable=Tunable(description='\n                Base cost for a sim putting the object in a valid object\n                inventory.\n                ',
       tunable_type=float,
       default=5)), 
     'floor_cost':OptionalTunable(enabled_by_default=True,
       tunable=Tunable(description='\n                The base cost used to compare putting an object on the ground\n                with other options.\n                ',
       tunable_type=float,
       default=15)), 
     'inventory_cost':OptionalTunable(enabled_by_default=True,
       tunable=Tunable(description='\n                Cost for how likely a sim puts the object in their inventory\n                instead of putting it down.\n                ',
       tunable_type=float,
       default=20)), 
     'affordances':TunableList(description='\n            A list of interactions that should be considered to be an\n            alternative to putting the object down.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)))), 
     'put_down_on_terrain_facing_sim':Tunable(description="\n            If true, the object will face the Sim when placing it on terrain.\n            Guitars and violins will enable this so they don't pop 180 degrees\n            after the Sim puts it down.\n            ",
       tunable_type=bool,
       default=False), 
     'ideal_slot_type_set':OptionalTunable(tunable=TunableReference(description="\n                If specified, this set of slots will have the cost specified in\n                the 'preferred_slot_cost' field in put_down_tuning.\n                \n                This allows us to tell Sims to weight specific slot types higher\n                than others when considering where to put down this object.\n                ",
       manager=(services.get_instance_manager(sims4.resources.Types.SLOT_TYPE_SET))))}


class TunablePutDownStrategySpeciesMapping(TunableMapping):

    def __init__(self, *args, **kwargs):
        (super().__init__)(args, key_type=TunableEnumEntry(description="\n                The Sim's species.\n                ",
  tunable_type=Species,
  default=(Species.HUMAN),
  invalid_enums=(
 Species.INVALID,)), 
         value_type=PutDownStrategy.TunableReference(), **kwargs)