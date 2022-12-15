# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\clock_handlers.py
# Compiled at: 2014-07-15 21:22:37
# Size of source mod 2**32: 1190 bytes
from gsi_handlers.gameplay_archiver import GameplayArchiver
from sims4.gsi.schema import GsiGridSchema
speed_change_schema = GsiGridSchema(label='Speed Change Request Log')
speed_change_schema.add_field('sim', label='Sim')
speed_change_schema.add_field('interaction', label='Interaction', width=3)
speed_change_schema.add_field('request_type', label='Request Type')
speed_change_schema.add_field('requested_speed', label='Requested Speed')
speed_change_schema.add_field('is_request', label='Is Request')
speed_change_archiver = GameplayArchiver('speed_change_log', speed_change_schema)

def archive_speed_change(interaction, request_type, requested_speed, is_request):
    archive_data = {'sim':str(interaction.sim), 
     'interaction':str(interaction), 
     'request_type':str(request_type), 
     'requested_speed':str(requested_speed), 
     'is_request':is_request}
    speed_change_archiver.archive(data=archive_data)