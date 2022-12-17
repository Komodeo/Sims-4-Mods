# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\temple\temple_utils.py
# Compiled at: 2022-07-21 18:49:30
# Size of source mod 2**32: 837 bytes
import services

class TempleUtils:

    @classmethod
    def get_temple_zone_director(cls):
        venue_service = services.venue_service()
        if venue_service is None:
            return
        zone_director = venue_service.get_zone_director()
        if hasattr(zone_director, '_temple_data'):
            return zone_director