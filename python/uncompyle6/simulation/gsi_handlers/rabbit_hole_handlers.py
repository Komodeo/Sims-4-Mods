# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\rabbit_hole_handlers.py
# Compiled at: 2022-07-21 18:49:30
# Size of source mod 2**32: 2527 bytes
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiGridSchema
import services
rabbit_holes_schema = GsiGridSchema(label='Rabbit Holes')
rabbit_holes_schema.add_field('sim', label='Sim', width=2, unique_field=True)
rabbit_holes_schema.add_field('sim_id', label='Sim ID', hidden=True)
rabbit_holes_schema.add_field('rabbit_hole_uid', label='UID', hidden=True)
rabbit_holes_schema.add_field('rabbit_hole_name', label='Name', width=2)
rabbit_holes_schema.add_field('rabbit_hole_zone', label='Zone')
rabbit_holes_schema.add_field('rabbit_hole_time', label='Remaining Time')
rabbit_holes_schema.add_field('rabbit_hole_linked_sims', label='Linked Sims')
rabbit_holes_schema.add_field('rabbit_hole_phase', label='Phase')

@GsiHandler('rabbit_holes', rabbit_holes_schema)
def generate_rabbit_hole_data(zone_id: int=None, filter=None):
    rabbit_hole_datas = []
    rabbit_hole_service = services.get_rabbit_hole_service()
    sim_info_manager = services.sim_info_manager()
    if rabbit_hole_service is None:
        return rabbit_hole_datas
    for sim_id, rabbit_holes in rabbit_hole_service._rabbit_holes.items():
        sim_info = sim_info_manager.get(sim_id)
        if sim_info is None:
            continue
        for rabbit_hole in rabbit_holes:
            alarm_handle_remaining_time = rabbit_hole.alarm_handle.get_remaining_time() if rabbit_hole.alarm_handle else 'no time limit'
            zone_name = 'undefined'
            persistence_service = services.get_persistence_service()
            if persistence_service is not None:
                zone_data = persistence_service.get_zone_proto_buff(sim_info.zone_id)
                if zone_data is not None:
                    zone_name = zone_data.name
            rabbit_hole_datas.append({'sim':str(sim_info), 
             'sim_id':str(sim_id), 
             'rabbit_hole_uid':str(rabbit_hole.guid64), 
             'rabbit_hole_name':str(rabbit_hole), 
             'rabbit_hole_zone':str(zone_name), 
             'rabbit_hole_time':str(alarm_handle_remaining_time), 
             'rabbit_hole_linked_sims':str([sim_info_manager.get(sim_id) for sim_id, _ in rabbit_hole.linked_rabbit_holes]), 
             'rabbit_hole_phase':str(rabbit_hole.current_phase)})

    return rabbit_hole_datas