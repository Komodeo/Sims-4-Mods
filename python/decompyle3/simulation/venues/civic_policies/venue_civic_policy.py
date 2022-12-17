# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\venues\civic_policies\venue_civic_policy.py
# Compiled at: 2020-01-24 13:57:16
# Size of source mod 2**32: 2100 bytes
from event_testing.test_events import TestEvent
from sims4.tuning.tunable import TunableReference
from sims4.tuning.tunable_base import ExportModes
import sims4
from civic_policies.base_civic_policy import BaseCivicPolicy
import services

class VenueCivicPolicy(BaseCivicPolicy):
    INSTANCE_TUNABLES = {'sub_venue': TunableReference(description='\n            Sub-Venue to make active when this policy is enacted.\n            ',
                    manager=(services.get_instance_manager(sims4.resources.Types.VENUE)),
                    pack_safe=True,
                    export_modes=(ExportModes.All))}

    def enact(self):
        if self.enacted:
            return
        for policy in tuple(self.provider.get_enacted_policies()):
            if policy is not self:
                self.provider.repeal(policy)

        super().enact()
        if not self.enacted:
            return
        self.provider.request_active_venue(self.sub_venue)
        venue_game_service = services.venue_game_service()
        zone = None if venue_game_service is None else venue_game_service.get_zone_for_provider(self.provider)
        zone_id = None if zone is None else zone.id
        services.get_event_manager().process_event((TestEvent.CivicPoliciesChanged), custom_keys=(
         (
          zone_id, type(self)),))

    def repeal(self):
        super().repeal()
        if self.enacted:
            return
        self.provider.request_restore_default()
        venue_game_service = services.venue_game_service()
        zone = None if venue_game_service is None else venue_game_service.get_zone_for_provider(self.provider)
        zone_id = None if zone is None else zone.id
        services.get_event_manager().process_event((TestEvent.CivicPoliciesChanged), custom_keys=(
         (
          zone_id, type(self)),))