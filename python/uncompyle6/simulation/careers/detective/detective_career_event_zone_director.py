# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\careers\detective\detective_career_event_zone_director.py
# Compiled at: 2017-11-17 23:46:59
# Size of source mod 2**32: 1325 bytes
from buffs.tunable import TunableBuffReference
from careers.career_event_zone_director import CareerEventZoneDirector
from sims4.tuning.tunable import TunableReference
import services, sims4.resources

class DetectiveCareerEventZoneDirector(CareerEventZoneDirector):
    INSTANCE_TUNABLES = {'criminal_trait':TunableReference(description='\n            The trait that signifies that a sim is a criminal at the police station.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.TRAIT)), 
     'in_holding_cell_buff':TunableBuffReference(description='\n            The buff that indicates that this sim is in a holding cell.\n            ')}

    def _did_sim_overstay(self, sim_info):
        if sim_info.has_trait(self.criminal_trait):
            return False
        if sim_info.has_buff(self.in_holding_cell_buff.buff_type):
            return False
        return super()._did_sim_overstay(sim_info)