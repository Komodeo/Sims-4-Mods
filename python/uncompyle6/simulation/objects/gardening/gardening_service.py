# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\gardening\gardening_service.py
# Compiled at: 2018-11-16 16:04:28
# Size of source mod 2**32: 2017 bytes
from _collections import defaultdict
from sims4.service_manager import Service
import sims4.geometry

class GardeningService(Service):

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._gardening_quadtrees = defaultdict(sims4.geometry.QuadTree)

    def add_gardening_object(self, obj):
        quadtree = self._gardening_quadtrees[obj.level]
        quadtree.insert(obj, obj.get_bounding_box())

    def get_gardening_objects(self, *, level, center, radius):
        if level not in self._gardening_quadtrees:
            return
        if isinstance(center, sims4.math.Vector3):
            center = sims4.math.Vector2(center.x, center.z)
        bounds = sims4.geometry.QtCircle(center, radius)
        quadtree = self._gardening_quadtrees[level]
        results = quadtree.query(bounds)
        return results

    def move_gardening_object(self, obj):
        for quadtree in self._gardening_quadtrees.values():
            quadtree.remove(obj)

        self.add_gardening_object(obj)

    def remove_gardening_object(self, obj):
        quadtree = self._gardening_quadtrees[obj.level]
        quadtree.remove(obj)