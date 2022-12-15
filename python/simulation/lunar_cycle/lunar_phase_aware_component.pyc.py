# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\lunar_cycle\lunar_phase_aware_component.py
# Compiled at: 2022-06-13 15:18:17
# Size of source mod 2**32: 2582 bytes
import services
from lunar_cycle.lunar_cycle_enums import LunarPhaseType
from objects.components import Component, componentmethod
from objects.components.state import TunableStateValueReference
from objects.components.types import LUNAR_PHASE_AWARE_COMPONENT
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, TunableMapping, TunableEnumEntry, TunableList

class LunarPhaseAwareComponent(Component, HasTunableFactory, AutoFactoryInit, component_name=LUNAR_PHASE_AWARE_COMPONENT):
    FACTORY_TUNABLES = {'lunar_phase_state_mapping': TunableMapping(description='\n            A tunable mapping linking a phase to the state(s) the component owner should have.\n            ',
                                    key_type=TunableEnumEntry(description='\n                The lunar phase we are interested in.\n                ',
                                    tunable_type=LunarPhaseType,
                                    default=(LunarPhaseType.NEW_MOON)),
                                    value_type=TunableList(description='\n                A tunable list of states to apply to the owning object of this component when it is the specified phase.\n                ',
                                    tunable=TunableStateValueReference(pack_safe=True)))}

    def on_add(self):
        zone = services.current_zone()
        if zone.is_zone_loading:
            return
        services.lunar_cycle_service().register_lunar_phase_aware_object(self)

    def on_remove(self):
        services.lunar_cycle_service().deregister_lunar_phase_aware_object(self)

    def on_finalize_load(self):
        services.lunar_cycle_service().register_lunar_phase_aware_object(self)

    @componentmethod
    def on_lunar_phase_set(self, lunar_phase_type):
        if lunar_phase_type in self.lunar_phase_state_mapping:
            for state_value in self.lunar_phase_state_mapping[lunar_phase_type]:
                self.owner.set_state(state_value.state, state_value)