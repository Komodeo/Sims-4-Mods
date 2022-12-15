# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\global_policies\global_policy_commands.py
# Compiled at: 2019-02-20 14:31:10
# Size of source mod 2**32: 581 bytes
from server_commands.argument_helpers import TunableInstanceParam
import services, sims4

@sims4.commands.Command('global_policy.set_progress', command_type=(sims4.commands.CommandType.Automation))
def set_global_policy_progress(policy: TunableInstanceParam(sims4.resources.Types.SNIPPET), progress_amount: int, _connection=None):
    services.global_policy_service().add_global_policy_progress(policy, progress_amount)