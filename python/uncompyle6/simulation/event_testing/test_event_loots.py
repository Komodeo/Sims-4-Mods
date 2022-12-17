# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\event_testing\test_event_loots.py
# Compiled at: 2019-07-11 18:36:53
# Size of source mod 2**32: 1374 bytes
from event_testing.test_events import TestEvent
from interactions import ParticipantTypeSingleSim
from interactions.utils.loot_basic_op import BaseLootOperation
from sims4.tuning.tunable import TunableEnumEntry, TunableFactory
import services, singletons

class ProcessEventOp(BaseLootOperation):
    FACTORY_TUNABLES = {'test_event': TunableEnumEntry(description="\n            The test event we'd like to process\n            ",
                     tunable_type=TestEvent,
                     default=(TestEvent.Invalid))}

    def __init__(self, test_event, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._test_event = test_event

    @TunableFactory.factory_option
    def subject_participant_type_options(description=singletons.DEFAULT, **kwargs):
        return (BaseLootOperation.get_participant_tunable)('subject', participant_type_enum=ParticipantTypeSingleSim, **kwargs)

    def _apply_to_subject_and_target(self, subject, target, resolver):
        services.get_event_manager().process_event((self._test_event), sim_info=(subject.sim_info))