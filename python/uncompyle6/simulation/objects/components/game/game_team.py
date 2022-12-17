# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\game\game_team.py
# Compiled at: 2019-04-02 12:04:19
# Size of source mod 2**32: 1358 bytes
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory

class GameTeam(HasTunableSingletonFactory, AutoFactoryInit):

    def add_player(self, game, sim):
        raise NotImplementedError

    def can_be_on_same_team(self, target_a, target_b):
        return True

    def team_determines_part(self):
        return True

    def can_be_on_opposing_team(self, target_a, target_b):
        return True

    def remove_player(self, game, sim):
        raise NotImplementedError