# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\careers\detective\detective_crime_scene.py
# Compiled at: 2015-02-07 18:00:54
# Size of source mod 2**32: 1608 bytes
from careers.career_event_zone_director import CareerEventZoneDirector
import sims4.log
logger = sims4.log.Logger('Crime Scene', default_owner='bhill')

class CrimeSceneZoneDirector(CareerEventZoneDirector):

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._should_load_sims = False

    def _load_custom_zone_director(self, zone_director_proto, reader):
        self._should_load_sims = True
        super()._load_custom_zone_director(zone_director_proto, reader)

    def _on_maintain_zone_saved_sim(self, sim_info):
        if self._should_load_sims:
            super()._on_maintain_zone_saved_sim(sim_info)
        else:
            logger.info('Discarding saved sim: {}', sim_info)

    def _process_injected_sim(self, sim_info):
        logger.info('Discarding injected sim: {}', sim_info)