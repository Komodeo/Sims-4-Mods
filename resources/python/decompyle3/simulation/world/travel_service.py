# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\world\travel_service.py
# Compiled at: 2017-01-11 19:00:40
# Size of source mod 2**32: 1233 bytes
from protocolbuffers import Consts_pb2, InteractionOps_pb2
from clock import ClockSpeedMode
import distributor, services

def travel_sim_to_zone(sim_id, zone_id):
    travel_sims_to_zone((sim_id,), zone_id)


def travel_sims_to_zone(sim_ids, zone_id):
    travel_info = InteractionOps_pb2.TravelSimsToZone()
    travel_info.zone_id = zone_id
    travel_info.sim_ids.extend(sim_ids)
    distributor.system.Distributor.instance().add_event(Consts_pb2.MSG_TRAVEL_SIMS_TO_ZONE, travel_info)
    services.game_clock_service().set_clock_speed(ClockSpeedMode.PAUSED)