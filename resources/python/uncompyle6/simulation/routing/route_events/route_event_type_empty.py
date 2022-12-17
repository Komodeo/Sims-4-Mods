# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\route_events\route_event_type_empty.py
# Compiled at: 2019-03-18 12:13:30
# Size of source mod 2**32: 1159 bytes
from routing.route_events.route_event_mixins import RouteEventDataBase
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, TunableRange

class RouteEventTypeEmpty(RouteEventDataBase, HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'duration_override': TunableRange(description='\n            The duration we want this route event to have. This modifies\n            how much of the route time this event will take up.\n            ',
                            tunable_type=float,
                            default=0.1,
                            minimum=0.1)}

    def prepare(self, actor):
        pass

    def execute(self, actor, **kwargs):
        pass

    def process(self, actor):
        pass