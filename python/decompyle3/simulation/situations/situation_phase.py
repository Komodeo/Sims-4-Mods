# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\situation_phase.py
# Compiled at: 2015-08-17 09:34:22
# Size of source mod 2**32: 1310 bytes


class SituationPhase:

    def __init__(self, job_list, exit_conditions, duration):
        self._job_list = job_list
        self._exit_conditions = exit_conditions
        self._duration = duration

    def jobs_gen(self):
        for job, role in self._job_list.items():
            yield (
             job, role)

    def exit_conditions_gen(self):
        for ec in self._exit_conditions:
            yield ec

    def get_duration(self):
        return self._duration