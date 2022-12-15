# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\fixup\sim_info_statistic_ops_fixup_action.py
# Compiled at: 2020-10-23 15:30:47
# Size of source mod 2**32: 857 bytes
from sims.fixup.sim_info_fixup_action import _SimInfoFixupAction
from sims4.tuning.tunable import TunableList
from statistics.statistic_ops import TunableStatisticChange
from event_testing.resolver import SingleSimResolver

class _SimInfoStatisticOpsFixupAction(_SimInfoFixupAction):
    FACTORY_TUNABLES = {'statistics_list': TunableList(description='\n            A list of Statistics Ops to run on the Sim.\n            ',
                          tunable=(TunableStatisticChange()))}

    def __call__(self, sim_info):
        resolver = SingleSimResolver(sim_info)
        for statistic_op in self.statistics_list:
            statistic_op.apply_to_resolver(resolver)