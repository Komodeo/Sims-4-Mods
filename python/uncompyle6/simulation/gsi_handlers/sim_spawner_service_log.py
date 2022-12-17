# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\sim_spawner_service_log.py
# Compiled at: 2018-03-05 17:00:39
# Size of source mod 2**32: 1857 bytes
from gsi_handlers.gameplay_archiver import GameplayArchiver
from sims4.gsi.schema import GsiGridSchema, GsiFieldVisualizers
import services
sim_spawner_service_log_schema = GsiGridSchema(label='Sim Spawner Service/Log')
sim_spawner_service_log_schema.add_field('action', label='Action', type=(GsiFieldVisualizers.STRING))
sim_spawner_service_log_schema.add_field('sim', label='Sim', type=(GsiFieldVisualizers.STRING))
sim_spawner_service_log_schema.add_field('reason', label='Reason', type=(GsiFieldVisualizers.STRING), width=1)
sim_spawner_service_log_schema.add_field('priority', label='Priority', type=(GsiFieldVisualizers.STRING))
sim_spawner_service_log_schema.add_field('position', label='Position', type=(GsiFieldVisualizers.STRING))
sim_spawner_service_log_schema.add_field('sim_time', label='Sim Time', type=(GsiFieldVisualizers.STRING))
sim_spawner_service_log_archiver = GameplayArchiver('sim_spawner_service_log', sim_spawner_service_log_schema, enable_archive_by_default=True,
  max_records=100)

def archive_sim_spawner_service_log_entry(action, sim_info, reason, priority, position):
    entry = {'action':action, 
     'sim':str(sim_info), 
     'reason':str(reason), 
     'priority':str(priority), 
     'position':str(position), 
     'sim_time':str(services.time_service().sim_now)}
    sim_spawner_service_log_archiver.archive(data=entry)