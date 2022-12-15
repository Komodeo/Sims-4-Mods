# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\death_commands.py
# Compiled at: 2017-05-02 17:32:41
# Size of source mod 2**32: 1938 bytes
from interactions.utils.death import DeathType
import interactions.utils.death, services, sims4.commands
from objects import ALL_HIDDEN_REASONS

@sims4.commands.Command('death.toggle', command_type=(sims4.commands.CommandType.Cheat))
def death_toggle(enabled: bool=None, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    interactions.utils.death.toggle_death(enabled=enabled)
    output('Toggling death, Enabled: {}'.format(interactions.utils.death._is_death_enabled))


@sims4.commands.Command('death.kill_many_npcs')
def death_kill_npcs(_connection=None):
    household_manager = services.household_manager()
    for household in tuple(household_manager.get_all()):
        if not household.home_zone_id:
            continue
        if household is services.active_household():
            continue
        else:
            for sim_info in household:
                if sim_info.can_live_alone:
                    if len(tuple(household.can_live_alone_info_gen())) <= 1:
                        break
                if sim_info.is_instanced(allow_hidden_flags=ALL_HIDDEN_REASONS):
                    continue
                if sim_info.is_toddler_or_younger:
                    continue
                if sim_info.death_type:
                    continue
                else:
                    death_type = DeathType.get_random_death_type()
                    sim_info.death_tracker.set_death_type(death_type, is_off_lot_death=True)

    return True