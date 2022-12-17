# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\buffs\buff_telemetry.py
# Compiled at: 2021-09-01 10:58:18
# Size of source mod 2**32: 1147 bytes
import services, sims4.log, telemetry_helper
from sims4.telemetry import TelemetryWriter
TELEMETRY_GROUP_BUFF = 'BUFF'
TELEMETRY_HOOK_ADD_BUFF = 'BADD'
TELEMETRY_HOOK_REMOVE_BUFF = 'BRMV'
TELEMETRY_FIELD_BUFF_ID = 'idbf'
buff_telemetry_writer = TelemetryWriter(TELEMETRY_GROUP_BUFF)
logger = sims4.log.Logger('BuffTelemetry', default_owner='jdimailig')

def write_buff_telemetry(hook_tag, buff, sim):
    if not sim.is_simulating:
        return
    current_zone = services.current_zone()
    if not (current_zone is None or current_zone.is_zone_running):
        return
    logger.debug('{}: buff:{}', hook_tag, buff.buff_type)
    with telemetry_helper.begin_hook(buff_telemetry_writer, hook_tag, sim=sim) as hook:
        hook.write_int(TELEMETRY_FIELD_BUFF_ID, buff.buff_type.guid64)