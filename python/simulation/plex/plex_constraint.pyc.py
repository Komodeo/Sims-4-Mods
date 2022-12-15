# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\plex\plex_constraint.py
# Compiled at: 2020-03-05 18:37:27
# Size of source mod 2**32: 2655 bytes
from interactions.constraints import Nowhere, Constraint, ANYWHERE
from sims4.geometry import CompoundPolygon, RestrictedPolygon
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableVariant, TunableTuple
from singletons import DEFAULT
import services, sims4.log
logger = sims4.log.Logger('PlexConstraint', default_owner='tingyul')

class PlexConstraint(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'non_plex_constraint': TunableVariant(description="\n            What the behavior of this constraint should be if it's used from\n            not a plex.\n            ",
                              anywhere=TunableTuple(description='\n                Use Anywhere constraint. This effectively means this plex\n                constraint does nothing if the player is not on a plex zone.\n                ',
                              locked_args={'constraint': ANYWHERE}),
                              nowhere=TunableTuple(description='\n                Use Nowhere constraint. This effectively makes this plex\n                constraint unsatisfiable if the player is not on a plex zone.\n                ',
                              locked_args={'constraint': Nowhere('PlexConstraint: non-plex zone')}),
                              default='anywhere')}

    def create_constraint(self, sim, target=None, target_position=DEFAULT, routing_surface=DEFAULT, **kwargs):
        if target is None:
            target = sim
        if routing_surface is DEFAULT:
            routing_surface = target.intended_routing_surface
        plex_service = services.get_plex_service()
        zone_id = services.current_zone_id()
        if not plex_service.is_zone_a_plex(zone_id):
            return self.non_plex_constraint.constraint
        level = routing_surface.secondary_id
        polygons = plex_service.get_plex_polygons(level)
        if not polygons:
            return Nowhere('PlexConstraint: plex {} not on level {}', zone_id, level)
        compound_polygon = CompoundPolygon(polygons)
        restricted_polygon = RestrictedPolygon(compound_polygon, [])
        constraint = Constraint(geometry=restricted_polygon,
          routing_surface=routing_surface,
          debug_name=('Plex zone id: {}, level: {}'.format(zone_id, level)))
        return constraint