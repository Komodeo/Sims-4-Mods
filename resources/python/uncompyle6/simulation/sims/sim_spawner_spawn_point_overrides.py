# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\sim_spawner_spawn_point_overrides.py
# Compiled at: 2020-06-24 12:46:34
# Size of source mod 2**32: 1241 bytes
from event_testing.resolver import SingleSimResolver
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory, TunableEnumWithFilter
from tag import Tag, SPAWN_PREFIX
from tunable_utils.tested_list import TunableTestedList, STOP_PROCESSING_ALWAYS

class TestedSpawnPointOverride(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'tested_list': TunableTestedList(tunable_type=TunableEnumWithFilter(tunable_type=Tag,
                      default=(Tag.INVALID),
                      invalid_enums=(
                     Tag.INVALID,),
                      filter_prefixes=SPAWN_PREFIX),
                      stop_processing_behavior=STOP_PROCESSING_ALWAYS)}

    def get_spawner_tag(self, sim_info):
        resolver = SingleSimResolver(sim_info)
        return next(iter((tag for tag in self.tested_list(resolver=resolver))), None)