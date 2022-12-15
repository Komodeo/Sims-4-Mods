# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\clans\__init__.py
# Compiled at: 2022-06-13 15:18:17
# Size of source mod 2**32: 377 bytes
import services

def on_sim_killed_or_culled(sim_info):
    clan_service = services.clan_service()
    if clan_service is not None:
        clan_service.on_sim_killed_or_culled(sim_info)