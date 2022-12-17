# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\global_flags\global_flag_commands.py
# Compiled at: 2021-06-01 14:47:18
# Size of source mod 2**32: 736 bytes
import services, sims4.commands
from global_flags.global_flags import GlobalFlags

@sims4.commands.Command('flags.add_flag', command_type=(sims4.commands.CommandType.Automation))
def add_flag(flag: GlobalFlags, connection=None):
    services.global_flag_service().add_flag(flag)


@sims4.commands.Command('flags.remove_flag', command_type=(sims4.commands.CommandType.Automation))
def remove_flag(flag: GlobalFlags, connection=None):
    services.global_flag_service().remove_flag(flag)