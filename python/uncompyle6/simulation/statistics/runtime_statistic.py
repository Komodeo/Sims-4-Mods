# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\statistics\runtime_statistic.py
# Compiled at: 2014-12-14 21:42:30
# Size of source mod 2**32: 904 bytes
from statistics.statistic import Statistic
import sims4.resources

class RuntimeStatistic(Statistic):
    INSTANCE_SUBCLASSES_ONLY = True

    @classmethod
    def generate(cls, name):
        ProxyClass = type(cls)(name, (cls,), {'INSTANCE_SUBCLASSES_ONLY': True})
        ProxyClass.reloadable = False
        key = sims4.resources.get_resource_key(name, ProxyClass.tuning_manager.TYPE)
        ProxyClass.tuning_manager.register_tuned_class(ProxyClass, key)
        return ProxyClass