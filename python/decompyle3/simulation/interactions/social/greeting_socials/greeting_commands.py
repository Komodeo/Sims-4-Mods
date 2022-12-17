# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\social\greeting_socials\greeting_commands.py
# Compiled at: 2015-08-27 15:52:59
# Size of source mod 2**32: 2184 bytes
from interactions.social.greeting_socials import greetings
from server_commands.argument_helpers import get_optional_target, OptionalSimInfoParam
import services, sims4.commands

@sims4.commands.Command('greetings.make_sim_ungreeted')
def make_sim_ungreeted(source_sim: OptionalSimInfoParam=None, _connection=None):
    source_sim_info = get_optional_target(source_sim, target_type=OptionalSimInfoParam, _connection=_connection)
    if source_sim_info is None:
        return False
    sim_info_manager = services.sim_info_manager()
    for other_sim in sim_info_manager.instanced_sims_gen():
        if other_sim.sim_info is source_sim_info:
            continue
        else:
            greetings.remove_greeted_rel_bit(source_sim_info, other_sim.sim_info)


@sims4.commands.Command('greetings.make_all_sims_ungreeted')
def make_all_sims_ungreeted(_connection=None):
    sim_info_manager = services.sim_info_manager()
    instanced_sims = list(sim_info_manager.instanced_sims_gen())
    for source_sim in instanced_sims:
        for other_sim in instanced_sims:
            if other_sim is source_sim:
                continue
            else:
                greetings.remove_greeted_rel_bit(source_sim.sim_info, other_sim.sim_info)


@sims4.commands.Command('greetings.toggle_greeted_rel_bit')
def toggle_greeted_rel_bit(_connection=None):
    greetings.debug_add_greeted_rel_bit = not greetings.debug_add_greeted_rel_bit
    if not greetings.debug_add_greeted_rel_bit:
        sims4.commands.output('Greetings: Greetings Persistence Disabled. Sims will NOT recieve the greeted rel bit.', _connection)
    else:
        sims4.commands.output('Greetings: Greetings Persistence Enabled. Sims WILL recieve the greeted rel bit.', _connection)