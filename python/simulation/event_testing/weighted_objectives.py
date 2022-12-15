# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\event_testing\weighted_objectives.py
# Compiled at: 2020-03-16 19:18:00
# Size of source mod 2**32: 1578 bytes
import services
from event_testing.tests import TunableTestSet
from sims4.resources import Types
from sims4.tuning.tunable import TunableList, TunableTuple, TunableReference, TunableRange

class WeightedObjectives(TunableList):

    def __init__(self, *args, **kwargs):
        (super().__init__)(args, tunable=TunableTuple(description='\n                A set of tests that are run against the Sim. If the tests pass,\n                this objective and the weight are added to a list for randomization.\n                ',
                    objective=TunableReference(description='\n                    The objective that will be provided if the tests pass.\n                    ',
                    manager=(services.get_instance_manager(Types.OBJECTIVE))),
                    tests=TunableTestSet(description='\n                    The tests that must pass for this objective to be valid.\n                    '),
                    weight=TunableRange(description='\n                    The weight of this objective against the other passing objectives.\n                    ',
                    tunable_type=float,
                    minimum=0,
                    default=1)), **kwargs)