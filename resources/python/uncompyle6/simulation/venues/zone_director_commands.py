# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\venues\zone_director_commands.py
# Compiled at: 2016-05-31 16:32:33
# Size of source mod 2**32: 735 bytes
import services, sims4.commands

@sims4.commands.Command('zone_director.print_situation_shifts')
def print_situation_shifts(_connection=None):
    zone_director = services.venue_service().get_zone_director()
    if not hasattr(zone_director, 'situation_shifts'):
        sims4.commands.output('{} has no schedule'.format(zone_director), _connection)
        return

    def output(s):
        sims4.commands.output(s, _connection)

    for shift in zone_director.situation_shifts:
        shift.shift_curve.debug_output_schedule(output)