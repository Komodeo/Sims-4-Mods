# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\loot_commands.py
# Compiled at: 2018-01-23 11:37:27
# Size of source mod 2**32: 2243 bytes
from event_testing.resolver import SingleSimResolver, DoubleObjectResolver
from server_commands.argument_helpers import TunableInstanceParam, OptionalSimInfoParam, get_optional_target, RequiredTargetParam
import services, sims4.commands

@sims4.commands.Command('loot.apply_to_sim', command_type=(sims4.commands.CommandType.DebugOnly))
def loot_apply_to_sim(loot_type: TunableInstanceParam(sims4.resources.Types.ACTION), opt_sim_id: OptionalSimInfoParam=None, _connection=None):
    sim_info = get_optional_target(opt_sim_id, target_type=OptionalSimInfoParam, _connection=_connection)
    if sim_info is None:
        sims4.commands.output('No sim_info specified', _connection)
        return
    resolver = SingleSimResolver(sim_info)
    loot_type.apply_to_resolver(resolver)


@sims4.commands.Command('loot.apply_to_sim_and_target', command_type=(sims4.commands.CommandType.DebugOnly))
def loot_apply_to_sim_and_target(loot_type: TunableInstanceParam(sims4.resources.Types.ACTION), actor_sim: RequiredTargetParam=None, target_obj: RequiredTargetParam=None, _connection=None):
    actor = actor_sim.get_target(manager=(services.sim_info_manager()))
    if actor is None:
        sims4.commands.output('No actor', _connection)
        return
    target = target_obj.get_target(manager=(services.object_manager()))
    if target is None:
        sims4.commands.output('No target', _connection)
        return
    resolver = DoubleObjectResolver(actor, target)
    loot_type.apply_to_resolver(resolver)