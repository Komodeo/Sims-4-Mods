# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\restaurants\restaurant_host_log_handler.py
# Compiled at: 2016-02-23 17:05:32
# Size of source mod 2**32: 926 bytes
from gsi_handlers.gameplay_archiver import GameplayArchiver
from sims4.gsi.schema import GsiGridSchema
import services, sims4.log
logger = sims4.log.Logger('GSI')
restaurant_host_schema = GsiGridSchema(label='Restaurant Host Log')
restaurant_host_schema.add_field('game_time', label='Game Time', width=2)
restaurant_host_schema.add_field('action', label='Action', width=2)
restaurant_host_schema.add_field('result', label='Result', width=2)
host_archiver = GameplayArchiver('hostActions', restaurant_host_schema, add_to_archive_enable_functions=True)

def log_host_action(action, result):
    archive_data = {'action':action, 
     'result':result}
    host_archiver.archive(data=archive_data)