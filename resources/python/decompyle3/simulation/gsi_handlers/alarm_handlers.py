# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\alarm_handlers.py
# Compiled at: 2014-04-11 16:45:01
# Size of source mod 2**32: 880 bytes
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiGridSchema, GsiFieldVisualizers
import alarms
alarm_schema = GsiGridSchema(label='Alarms')
alarm_schema.add_field('time', label='Absolute Time', width=2)
alarm_schema.add_field('time_left', label='Time Left', width=1)
alarm_schema.add_field('ticks', label='Ticks Left', type=(GsiFieldVisualizers.INT))
alarm_schema.add_field('handle', label='Handle', width=1, unique_field=True, hidden=True)
alarm_schema.add_field('owner', label='Owner', width=3)
alarm_schema.add_field('callback', label='Callback', width=3)

@GsiHandler('alarms', alarm_schema)
def generate_alarm_data(*args, zone_id: int=None, **kwargs):
    return alarms.get_alarm_data_for_gsi()