# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\dust\dust_commands.py
# Compiled at: 2020-11-20 14:39:02
# Size of source mod 2**32: 825 bytes
import services, sims4
from event_testing.game_option_tests import TestableGameOptions
from event_testing.test_events import TestEvent
from sims4.common import Pack

@sims4.commands.Command('dust.set_dust_enabled', pack=(Pack.SP22), command_type=(sims4.commands.CommandType.Live))
def set_dust_enabled(enabled: bool=True, _connection=None):
    services.get_event_manager().process_event((TestEvent.TestedGameOptionChanged), custom_keys=(
     TestableGameOptions.DUST_SYSTEM_ENABLED,))
    dust_service = services.dust_service()
    if dust_service is not None:
        dust_service.set_enabled(enabled)
    return True