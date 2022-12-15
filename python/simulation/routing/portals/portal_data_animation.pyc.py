# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\portals\portal_data_animation.py
# Compiled at: 2022-07-21 18:49:30
# Size of source mod 2**32: 5527 bytes
from _math import Transform
from animation import get_throwaway_animation_context
from animation.animation_utils import StubActor
from animation.arb import Arb
from animation.asm import create_asm
from protocolbuffers import Routing_pb2 as routing_protocols
from routing import Location
from routing.portals.portal_data_base import _PortalTypeDataBase
from routing.portals.portal_tuning import PortalType
from sims4.tuning.tunable import TunableReference, Tunable
import build_buy, services, sims4

class _PortalTypeDataAnimation(_PortalTypeDataBase):
    FACTORY_TUNABLES = {'animation_element':TunableReference(description='\n            The animation to play when a Sim traverses this portal.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.ANIMATION)), 
     'requires_los_between_entry_and_exit':Tunable(description='\n            If checked, this portal will only be valid if there is LOS between\n            the entry and exit points. If unchecked, LOS is not required.\n            ',
       tunable_type=bool,
       default=True), 
     'requires_height_check':Tunable(description="\n            If checked, We will check height between the portal points and the object's location. \n            If either the portal entry point or the portal exit point is at a location whose y \n            position differs by more than portal_height_offset_threshold from the object's, \n            the portal is not created. \n            Portal_height_offset_threshold is tuned at Native Build Buy Tuning.\n            ",
       tunable_type=bool,
       default=False)}

    @property
    def portal_type(self):
        return PortalType.PortalType_Animate

    @property
    def requires_los_between_points(self):
        return self.requires_los_between_entry_and_exit

    def _get_arb(self, actor, obj, *, is_mirrored):
        arb = Arb()
        asm = create_asm((self.animation_element.asm_key), context=(get_throwaway_animation_context()))
        asm.set_actor(self.animation_element.actor_name, actor)
        asm.set_actor(self.animation_element.target_name, obj)
        asm.set_parameter('isMirrored', is_mirrored)
        self.animation_element.append_to_arb(asm, arb)
        return arb

    def add_portal_data(self, actor, portal_instance, is_mirrored, walkstyle):
        arb = self._get_arb(actor, (portal_instance.obj), is_mirrored=is_mirrored)
        op = routing_protocols.RouteAnimateData()
        op.arb_data = arb._bytes()
        node_data = routing_protocols.RouteNodeData()
        node_data.type = routing_protocols.RouteNodeData.DATA_ANIMATE
        node_data.data = op.SerializeToString()
        return node_data

    def get_portal_duration(self, portal_instance, is_mirrored, walkstyle, age, gender, species):
        actor = StubActor(1, species=species)
        arb = self._get_arb(actor, (portal_instance.obj), is_mirrored=is_mirrored)
        _, duration, _ = arb.get_timing()
        return duration

    def get_portal_locations(self, obj):
        locations = []
        actor = StubActor(1)
        arb_there = self._get_arb(actor, obj, is_mirrored=False)
        boundary_condition = arb_there.get_boundary_conditions(actor)
        there_entry = Transform.concatenate(boundary_condition.pre_condition_transform, obj.transform)
        there_entry = Location((there_entry.translation), orientation=(there_entry.orientation), routing_surface=(obj.routing_surface))
        there_exit = Transform.concatenate(boundary_condition.post_condition_transform, obj.transform)
        there_exit = Location((there_exit.translation), orientation=(there_exit.orientation), routing_surface=(obj.routing_surface))
        arb_back = self._get_arb(actor, obj, is_mirrored=True)
        boundary_condition = arb_back.get_boundary_conditions(actor)
        back_entry = Transform.concatenate(boundary_condition.pre_condition_transform, obj.transform)
        back_entry = Location((back_entry.translation), orientation=(back_entry.orientation), routing_surface=(obj.routing_surface))
        back_exit = Transform.concatenate(boundary_condition.post_condition_transform, obj.transform)
        back_exit = Location((back_exit.translation), orientation=(back_exit.orientation), routing_surface=(obj.routing_surface))
        if self.requires_height_check and self.is_offset_from_object(there_entry, obj, build_buy.get_portal_height_offset_threshold()) or not self.is_offset_from_object(there_exit, obj, build_buy.get_portal_height_offset_threshold()):
            locations.append((there_entry, there_exit, back_entry, back_exit, 0))
        return locations