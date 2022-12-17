# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\reputation\reputation_commands.py
# Compiled at: 2018-07-19 13:35:24
# Size of source mod 2**32: 1553 bytes
from server_commands.argument_helpers import OptionalTargetParam, get_optional_target
import sims4.commands

@sims4.commands.Command('reputation.set_allow_reputation', command_type=(sims4.commands.CommandType.Automation))
def set_allow_reputation(allow_reputation: bool, opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        sims4.commands.output('No target Sim to manipulate the reputation of.', _connection)
        return False
    sim.allow_reputation = allow_reputation
    sims4.commands.output("{}'s allow_reputation setting is set to {}".format(sim, sim.allow_reputation), _connection)
    return True


@sims4.commands.Command('reputation.show_allow_reputation', command_type=(sims4.commands.CommandType.Automation))
def show_allow_reputation(opt_sim: OptionalTargetParam=None, _connection=None):
    sim = get_optional_target(opt_sim, _connection)
    if sim is None:
        sims4.commands.output('No target Sim to get the value of allow_reputation from.', _connection)
        return False
    sims4.commands.output("{}'s allow_reputation setting is set to {}".format(sim, sim.allow_reputation), _connection)
    return True