# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\new_object_component.py
# Compiled at: 2017-06-07 11:18:54
# Size of source mod 2**32: 2873 bytes
import operator
from interactions.base.super_interaction import SuperInteraction
from objects.components import Component
from sims4.tuning.tunable import TunableSet
from statistics.commodity import Commodity
import objects.components.types, sims4

class NewObjectTuning:
    NEW_OBJECT_COMMODITY = Commodity.TunableReference()
    NEW_OBJECT_AFFORDANCES = TunableSet(description='\n        Affordances available on an object as long as its considered as new.\n        ',
      tunable=SuperInteraction.TunableReference(description='\n            Affordance reference to add to new objects.\n            ',
      pack_safe=True))


class NewObjectComponent(Component, component_name=objects.components.types.NEW_OBJECT_COMPONENT, allow_dynamic=True):

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._initialize_commodity()
        self.owner.is_new_object = True

    def _initialize_commodity(self):
        new_object_commodity = self.owner.commodity_tracker.add_statistic(NewObjectTuning.NEW_OBJECT_COMMODITY)
        threshold = sims4.math.Threshold(new_object_commodity.min_value, operator.le)
        self._commodity_listener = self.owner.commodity_tracker.create_and_add_listener(NewObjectTuning.NEW_OBJECT_COMMODITY.stat_type, threshold, self._new_object_expired)

    def component_super_affordances_gen(self, **kwargs):
        if not self.owner.is_new_object:
            return
        yield from NewObjectTuning.NEW_OBJECT_AFFORDANCES
        if False:
            yield None

    def _new_object_expired(self, stat):
        self.owner.is_new_object = False
        self.owner.commodity_tracker.remove_listener(self._commodity_listener)
        self.owner.remove_component(objects.components.types.NEW_OBJECT_COMPONENT)

    def on_add(self, *_, **__):
        self.owner.update_component_commodity_flags()

    def on_remove(self, *_, **__):
        self.owner.update_component_commodity_flags()
        if self._commodity_listener is None:
            return
        self.owner.commodity_tracker.remove_listener(self._commodity_listener)
        self._commodity_listener = None