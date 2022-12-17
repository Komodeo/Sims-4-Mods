# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\travel_group\travel_group_telemetry.py
# Compiled at: 2020-03-27 15:54:09
# Size of source mod 2**32: 1504 bytes
import sims4.telemetry, telemetry_helper
from world.region import get_region_description_id_from_zone_id
TELEMETRY_GROUP_TRAVEL_GROUPS = 'TGRP'
TELEMETRY_HOOK_TRAVEL_GROUP_ADD = 'TGAD'
TELEMETRY_HOOK_TRAVEL_GROUP_START = 'TGST'
TELEMETRY_HOOK_TRAVEL_GROUP_EXTEND = 'TGEX'
TELEMETRY_HOOK_TRAVEL_GROUP_END = 'TGEN'
TELEMETRY_HOOK_TRAVEL_GROUP_REMOVE = 'TGRM'
TELEMETRY_TRAVEL_GROUP_ID = 'tgid'
TELEMETRY_TRAVEL_GROUP_ZONE_ID = 'tgzo'
TELEMETRY_TRAVEL_GROUP_SIZE = 'tgsz'
TELEMETRY_TRAVEL_GROUP_DURATION = 'tgdu'
TELEMETRY_TRAVEL_GROUP_REGION_DESC_ID = 'rgni'
travel_group_telemetry_writer = sims4.telemetry.TelemetryWriter(TELEMETRY_GROUP_TRAVEL_GROUPS)

def write_travel_group_telemetry(group, hook_tag, sim_info):
    with telemetry_helper.begin_hook(travel_group_telemetry_writer, hook_tag, sim_info=sim_info) as (hook):
        hook.write_int(TELEMETRY_TRAVEL_GROUP_ID, group.id)
        hook.write_int(TELEMETRY_TRAVEL_GROUP_ZONE_ID, group.zone_id)
        hook.write_int(TELEMETRY_TRAVEL_GROUP_SIZE, len(group))
        hook.write_int(TELEMETRY_TRAVEL_GROUP_DURATION, int(group.duration_time_in_minutes))
        hook.write_int(TELEMETRY_TRAVEL_GROUP_REGION_DESC_ID, int(get_region_description_id_from_zone_id(group.zone_id)))