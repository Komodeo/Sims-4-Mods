# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\waypoints\waypoint_generator_tags.py
# Compiled at: 2021-02-24 21:37:04
# Size of source mod 2**32: 808 bytes
from routing.waypoints.waypoint_generator_object_mixin import _WaypointGeneratorMultipleObjectMixin
from tag import TunableTags
import services

class _WaypointGeneratorMultipleObjectByTag(_WaypointGeneratorMultipleObjectMixin):
    FACTORY_TUNABLES = {'object_tags': TunableTags(description='\n            Find all of the objects based on these tags.\n            ',
                      filter_prefixes=('func', ))}

    def _get_objects(self):
        return services.object_manager().get_objects_matching_tags((self.object_tags), match_any=True)