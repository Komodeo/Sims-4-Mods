# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\event_testing\test_utils.py
# Compiled at: 2017-06-08 11:18:00
# Size of source mod 2**32: 641 bytes
from sims.sim_info_tests import SimInfoTest
import caches, sims.sim_info_types

@caches.cached
def get_disallowed_ages(affordance):
    disallowed_ages = set()
    for test in affordance.test_globals:
        if isinstance(test, SimInfoTest):
            if test.ages is None:
                continue
            else:
                for age in sims.sim_info_types.Age:
                    if age not in test.ages:
                        disallowed_ages.add(age)

    return disallowed_ages