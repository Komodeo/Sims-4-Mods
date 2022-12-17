# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\complex\service_npc_nanny_situation.py
# Compiled at: 2016-10-19 15:14:23
# Size of source mod 2**32: 630 bytes
from event_testing.test_events import TestEvent
from situations.complex.service_npc_situation import ServiceNpcSituation
import services

class ServiceNpcNannySituation(ServiceNpcSituation):

    def _on_set_sim_job(self, sim, job_type):
        super()._on_set_sim_job(sim, job_type)
        services.get_event_manager().process_event((TestEvent.AvailableDaycareSimsChanged), sim_info=(self.service_sim().sim_info))