# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\pools\swimming_mixin.py
# Compiled at: 2019-07-19 12:52:19
# Size of source mod 2**32: 1587 bytes
import routing

class SwimmingMixin:

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._provided_routing_surface = None
        self._world_routing_surface = None

    def is_routing_surface_overlapped_at_position(self, _):
        return False

    @property
    def provided_routing_surface(self):
        return self._provided_routing_surface

    @property
    def world_routing_surface(self):
        return self._world_routing_surface

    def _build_routing_surfaces(self):
        self._provided_routing_surface = routing.SurfaceIdentifier(self.zone_id, self._location.world_routing_surface.secondary_id, routing.SurfaceType.SURFACETYPE_POOL)
        self._world_routing_surface = routing.SurfaceIdentifier(self.zone_id, self._location.world_routing_surface.secondary_id, routing.SurfaceType.SURFACETYPE_WORLD)