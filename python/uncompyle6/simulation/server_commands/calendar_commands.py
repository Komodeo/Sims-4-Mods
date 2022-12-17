# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\calendar_commands.py
# Compiled at: 2021-06-07 16:47:06
# Size of source mod 2**32: 610 bytes
from server_commands.argument_helpers import TunableInstanceParam
import sims4.commands, services

@sims4.commands.Command('calendar.set_favorite_calendar_entry', command_type=(sims4.commands.CommandType.Live))
def set_favorite_calendar_entry(event_id: int, is_favorite: bool=False, _connection=None):
    services.calendar_service().set_favorited_calendar_entry(event_id, is_favorite)