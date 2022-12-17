# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gameplay_scenarios\scenario_service.py
# Compiled at: 2022-08-26 15:13:12
# Size of source mod 2**32: 707 bytes
import services
from sims4.service_manager import Service

class ScenarioService(Service):

    def update(self):
        active_household = services.active_household()
        if active_household is not None:
            scenario_tracker = active_household.scenario_tracker
            if scenario_tracker is not None:
                if scenario_tracker.active_scenario is not None:
                    scenario_tracker.active_scenario.update()