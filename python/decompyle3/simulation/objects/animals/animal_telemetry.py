# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\animals\animal_telemetry.py
# Compiled at: 2021-03-09 14:00:10
# Size of source mod 2**32: 680 bytes
import sims4, telemetry_helper
TELEMETRY_GROUP_ANIMAL = 'ANML'
writer = sims4.telemetry.TelemetryWriter(TELEMETRY_GROUP_ANIMAL)
TELEMETRY_HOOK_ADD_ANIMAL = 'AADD'
TELEMETRY_FIELD_DEFINITION = 'type'
TELEMETRY_FIELD_INSTANCE = 'anid'

def send_animal_added_telemetry(animal):
    with telemetry_helper.begin_hook(writer, TELEMETRY_HOOK_ADD_ANIMAL) as hook:
        definition_id = animal.definition.id if hasattr(animal, 'definition') else 0
        hook.write_int(TELEMETRY_FIELD_DEFINITION, definition_id)
        hook.write_int(TELEMETRY_FIELD_INSTANCE, animal.id)