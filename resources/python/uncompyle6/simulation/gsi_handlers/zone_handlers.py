# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\zone_handlers.py
# Compiled at: 2014-04-14 15:29:07
# Size of source mod 2**32: 623 bytes
import services
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiSchema
zone_view_schema = GsiSchema()
zone_view_schema.add_field('zoneId')

@GsiHandler('zone_view', zone_view_schema)
def generate_zone_view_data():
    zone_list = []
    for zone in services._zone_manager.objects:
        if zone.is_instantiated:
            zone_list.append({'zoneId':hex(zone.id),  'zoneName':'ZoneName'})

    return zone_list