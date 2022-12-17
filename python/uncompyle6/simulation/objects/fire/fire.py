# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\fire\fire.py
# Compiled at: 2020-02-04 16:38:50
# Size of source mod 2**32: 2135 bytes
from objects.persistence_groups import PersistenceGroups
import objects.game_object, services

class Fire(objects.game_object.GameObject):

    def __init__(self, definition, **kwargs):
        (super().__init__)(definition, **kwargs)
        self._raycast_context_dirty = True

    def on_remove(self):
        fire_service = services.get_fire_service()
        fire_service.remove_fire_object(self)
        super().on_remove()

    def flammable(self):
        return True

    def raycast_context(self, for_carryable=False):
        if self._raycast_context_dirty:
            self._create_raycast_context(for_carryable=for_carryable)
            burning_objects = services.get_fire_service().objects_burning_from_fire_object(self)
            for obj in burning_objects:
                if obj.routing_context is None:
                    continue
                object_footprint_id = obj.routing_context.object_footprint_id
                if object_footprint_id is not None:
                    self._raycast_context.ignore_footprint_contour(object_footprint_id)

            self._raycast_context_dirty = False
        return super().raycast_context(for_carryable=for_carryable)

    @property
    def raycast_context_dirty(self):
        return self._raycast_context_dirty

    @raycast_context_dirty.setter
    def raycast_context_dirty(self, value):
        self._raycast_context_dirty = value

    @property
    def persistence_group(self):
        return PersistenceGroups.NONE

    @persistence_group.setter
    def persistence_group(self, value):
        pass