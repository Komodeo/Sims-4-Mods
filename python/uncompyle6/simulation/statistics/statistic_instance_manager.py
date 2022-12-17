# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\statistics\statistic_instance_manager.py
# Compiled at: 2022-07-21 18:49:30
# Size of source mod 2**32: 1111 bytes
from sims4.tuning.instance_manager import InstanceManager
import sims4.log
logger = sims4.log.Logger('StatisticInstanceManager')

class StatisticInstanceManager(InstanceManager):

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._skills = []

    def register_tuned_class(self, instance, resource_key):
        super().register_tuned_class(instance, resource_key)
        if instance.is_skill:
            self._skills.append(instance)

    def create_class_instances(self):
        self._skills = []
        super().create_class_instances()

        def key(cls):
            return cls.__name__.lower()

        self._skills = tuple(sorted((self._skills), key=key))

    def all_skills_gen(self):
        yield from self._skills
        if False:
            yield None