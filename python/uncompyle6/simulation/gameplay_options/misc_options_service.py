# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gameplay_options\misc_options_service.py
# Compiled at: 2022-07-21 18:49:30
# Size of source mod 2**32: 1834 bytes
from sims4.service_manager import Service

class MiscOptionsService(Service):

    def __init__(self):
        self._restrict_npc_werewolves = False
        self._npc_relationship_autonomy_enabled = True

    def save_options(self, options_proto):
        options_proto.restrict_npc_werewolves = self._restrict_npc_werewolves
        options_proto.npc_relationship_autonomy_enabled = self._npc_relationship_autonomy_enabled

    def load_options(self, options_proto):
        self._restrict_npc_werewolves = options_proto.restrict_npc_werewolves
        self._npc_relationship_autonomy_enabled = options_proto.npc_relationship_autonomy_enabled

    @property
    def restrict_npc_werewolves(self):
        return self._restrict_npc_werewolves

    def set_restrict_npc_werewolves(self, enabled: bool):
        self._restrict_npc_werewolves = enabled

    @property
    def npc_relationship_autonomy_enabled(self):
        return self._npc_relationship_autonomy_enabled

    def set_npc_relationship_autonomy_enabled(self, enabled: bool):
        self._npc_relationship_autonomy_enabled = enabled