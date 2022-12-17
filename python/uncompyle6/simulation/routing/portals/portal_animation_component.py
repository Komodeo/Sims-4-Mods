# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\portals\portal_animation_component.py
# Compiled at: 2020-03-09 10:38:07
# Size of source mod 2**32: 1967 bytes
from animation.animation_constants import ActorType
from animation.animation_overrides_tuning import TunableParameterMapping
from distributor.fields import ComponentField, Field
from distributor.ops import SetActorType, SetActorStateMachine, SetActorStateMachineParams
from objects.components import Component
from objects.components.types import PORTAL_ANIMATION_COMPONENT
from sims4.tuning.tunable import AutoFactoryInit, HasTunableFactory, TunableInteractionAsmResourceKey

class PortalAnimationComponent(Component, HasTunableFactory, AutoFactoryInit, component_name=PORTAL_ANIMATION_COMPONENT):
    FACTORY_TUNABLES = {'_portal_asm':TunableInteractionAsmResourceKey(description='\n            The animation to use for this portal.\n            '), 
     '_portal_asm_parameters':TunableParameterMapping(description='\n            The parameters to utilize in the portal asm for this object.\n            ')}

    @ComponentField(op=SetActorType, priority=(Field.Priority.HIGH))
    def actor_type(self):
        return ActorType.Door

    @ComponentField(op=SetActorStateMachine)
    def portal_asm(self):
        return self._portal_asm

    @ComponentField(op=SetActorStateMachineParams, default=None)
    def portal_asm_params(self):
        if self._portal_asm_parameters:
            return self._portal_asm_parameters