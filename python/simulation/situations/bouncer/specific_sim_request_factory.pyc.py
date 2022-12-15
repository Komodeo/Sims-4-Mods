# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\bouncer\specific_sim_request_factory.py
# Compiled at: 2018-09-17 11:23:26
# Size of source mod 2**32: 871 bytes
from situations.bouncer.bouncer_request import BouncerRequestFactory

class SpecificSimRequestFactory(BouncerRequestFactory):

    def __init__(self, situation, callback_data, job_type, request_priority, exclusivity, sim_id):
        super().__init__(situation, callback_data=callback_data,
          job_type=job_type,
          request_priority=request_priority,
          user_facing=False,
          exclusivity=exclusivity)
        self._sim_id = sim_id

    def _can_assign_sim_to_request(self, sim):
        return sim.sim_id == self._sim_id