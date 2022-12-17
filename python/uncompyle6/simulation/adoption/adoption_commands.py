# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\adoption\adoption_commands.py
# Compiled at: 2017-09-14 11:43:34
# Size of source mod 2**32: 832 bytes
from server_commands.argument_helpers import OptionalSimInfoParam, get_optional_target
from sims4.commands import CommandType
import services, sims4.commands

@sims4.commands.Command('adoption.remove_sim_info', command_type=(CommandType.Live))
def remove_sim_info(opt_sim: OptionalSimInfoParam=None, _connection=None):
    sim_info = get_optional_target(opt_sim, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_info is None:
        return False
    adoption_service = services.get_adoption_service()
    adoption_service.remove_sim_info(sim_info)
    return True