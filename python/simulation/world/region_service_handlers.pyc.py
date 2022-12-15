# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\world\region_service_handlers.py
# Compiled at: 2022-02-09 10:21:47
# Size of source mod 2**32: 1547 bytes
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiGridSchema
import services
region_schema = GsiGridSchema(label='Region Service')
region_schema.add_field('region_name', label='Region Name', unique_field=True)
with region_schema.add_has_many('commodities', GsiGridSchema, label='Commodities') as sub_schema:
    sub_schema.add_field('name', label='Name')
    sub_schema.add_field('value', label='Value')

@GsiHandler('region_service', region_schema)
def generate_region_service_data(*args, zone_id: int=None, **kwargs):
    region_service_data = []
    region_service = services.region_service()
    if region_service is None:
        return region_service_data
    for region_inst in region_service._region_instances.values():
        commodities_entry = []
        for commodity in region_inst.commodity_tracker.get_all_commodities():
            entry = {'name':type(commodity).__name__, 
             'value':commodity.get_value()}
            commodities_entry.append(entry)

        entry = {'region_name':type(region_inst).__name__, 
         'commodities':commodities_entry}
        region_service_data.append(entry)

    return region_service_data