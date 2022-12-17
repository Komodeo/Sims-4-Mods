# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\clubs\__init__.py
# Compiled at: 2018-08-21 14:23:05
# Size of source mod 2**32: 656 bytes
import services

class UnavailableClubError(Exception):
    pass


class UnavailableClubCriteriaError(Exception):
    pass


def on_sim_killed_or_culled(sim_info):
    club_service = services.get_club_service()
    if club_service is not None:
        club_service.on_sim_killed_or_culled(sim_info)