# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\eco_footprint\eco_footprint_telemetry.py
# Compiled at: 2020-01-31 13:42:48
# Size of source mod 2**32: 1429 bytes
import sims4, telemetry_helper
TELEMETRY_GROUP_ECO_FOOTPRINT = 'NBHD'
TELEMETRY_HOOK_ECO_FOOTPRINT_STATE_CHANGE = 'FOOT'
TELEMETRY_FIELD_NEIGHBORHOOD = 'nbhd'
TELEMETRY_FIELD_OLD_FOOTPRINT_STATE = 'oldf'
TELEMETRY_FIELD_NEW_FOOTPRINT_STATE = 'newf'
TELEMETRY_FIELD_CONVERGENCE_VALUE = 'cnvg'
_telemetry_writer = sims4.telemetry.TelemetryWriter(TELEMETRY_GROUP_ECO_FOOTPRINT)

def send_eco_footprint_state_change_telemetry(world_description_id, old_state, new_state, convergence_value):
    with telemetry_helper.begin_hook(_telemetry_writer, TELEMETRY_HOOK_ECO_FOOTPRINT_STATE_CHANGE) as (hook):
        hook.write_guid(TELEMETRY_FIELD_NEIGHBORHOOD, world_description_id)
        hook.write_enum(TELEMETRY_FIELD_OLD_FOOTPRINT_STATE, old_state)
        hook.write_enum(TELEMETRY_FIELD_NEW_FOOTPRINT_STATE, new_state)
        hook.write_float(TELEMETRY_FIELD_CONVERGENCE_VALUE, convergence_value)