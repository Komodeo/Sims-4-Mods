# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\clubs\club_ops.py
# Compiled at: 2015-10-21 15:30:07
# Size of source mod 2**32: 1503 bytes
from clubs.club_enums import ClubGatheringVibe
from interactions.utils.loot_basic_op import BaseLootOperation
from sims4.tuning.tunable import TunableEnumEntry
import services

class SetClubGatheringVibe(BaseLootOperation):
    FACTORY_TUNABLES = {'vibe': TunableEnumEntry(description='\n            The vibe to set the gathering to.\n            ',
               tunable_type=ClubGatheringVibe,
               default=(ClubGatheringVibe.NO_VIBE))}

    def __init__(self, vibe, **kwargs):
        (super().__init__)(**kwargs)
        self._vibe = vibe

    def _apply_to_subject_and_target(self, subject, target, resolver):
        club_service = services.get_club_service()
        if club_service is None:
            return
        subject_sim = subject.get_sim_instance()
        if subject_sim is None:
            return
        gathering = club_service.sims_to_gatherings_map.get(subject_sim)
        if gathering is None:
            return
        gathering.set_club_vibe(self._vibe)