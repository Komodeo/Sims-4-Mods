# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\portals\portal_cost.py
# Compiled at: 2017-10-11 17:00:35
# Size of source mod 2**32: 1719 bytes
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory, TunableRange, TunableVariant

class PortalCostTraversalLength(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'multiplier': TunableRange(tunable_type=float,
                     default=1,
                     minimum=0)}

    def __call__(self, start, end):
        if self.multiplier == 1:
            return -1
        cost = (start.position - end.position).magnitude() * self.multiplier
        return cost


class PortalCostFixed(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'cost': TunableRange(tunable_type=float,
               default=1,
               minimum=0,
               maximum=9999)}

    def __call__(self, *_, **__):
        return self.cost


class TunablePortalCostVariant(TunableVariant):

    def __init__(self, *args, **kwargs):
        return (super().__init__)(args, traversal_length=PortalCostTraversalLength.TunableFactory(), 
         fixed_cost=PortalCostFixed.TunableFactory(), 
         default='traversal_length', **kwargs)