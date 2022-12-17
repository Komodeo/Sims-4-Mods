# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\buildbuy_commands.py
# Compiled at: 2020-02-06 11:37:04
# Size of source mod 2**32: 1999 bytes
from sims4.common import Pack
import build_buy, services, sims4.commands

@sims4.commands.Command('bb.getuserinbuildbuy')
def get_user_in_buildbuy(_connection=None):
    zone_id = services.current_zone_id()
    account_id = build_buy.get_user_in_build_buy(zone_id)
    sims4.commands.output('User in Build Buy: {0}'.format(account_id), _connection)


@sims4.commands.Command('bb.initforceexit')
def init_force_exit_buildbuy(_connection=None):
    zone_id = services.current_zone_id()
    sims4.commands.output('Starting Force User out of BB...', _connection)
    build_buy.init_build_buy_force_exit(zone_id)


@sims4.commands.Command('bb.forceexit')
def force_exit_buildbuy(_connection=None):
    zone_id = services.current_zone_id()
    sims4.commands.output('Forcing User out of BB...', _connection)
    build_buy.build_buy_force_exit(zone_id)


@sims4.commands.Command('qa.is_in_build_buy', command_type=(sims4.commands.CommandType.Automation))
def qa_is_in_build_buy(_connection=None):
    sims4.commands.automation_output('BuildBuy; IsInBuildBuy:{}'.format(services.current_zone().is_in_build_buy), _connection)


@sims4.commands.Command('bb.set_build_eco_effects_enabled', pack=(Pack.EP09), command_type=(sims4.commands.CommandType.Live))
def set_build_eco_effects_enabled(enabled: bool=True, _connection=None):
    zone_modifier_service = services.get_zone_modifier_service()
    zone_modifier_service.set_build_eco_effects_enabled(enabled)