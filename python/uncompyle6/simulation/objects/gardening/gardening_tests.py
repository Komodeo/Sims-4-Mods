# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\gardening\gardening_tests.py
# Compiled at: 2018-11-28 12:03:38
# Size of source mod 2**32: 1118 bytes
from event_testing import test_base
from event_testing.results import TestResult
from objects.components.types import GARDENING_COMPONENT
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit
import services

class LotHasGardenTest(HasTunableSingletonFactory, AutoFactoryInit, test_base.BaseTest):

    def get_expected_args(self):
        return {}

    def __call__(self):
        gardening_objects = services.object_manager().get_all_objects_with_component_gen(GARDENING_COMPONENT)
        if gardening_objects is not None:
            for gardening_obj in gardening_objects:
                if gardening_obj.is_on_active_lot():
                    return gardening_obj.is_in_inventory() or TestResult.TRUE

        return TestResult(False, 'Active lot has no gardening plants.', tooltip=(self.tooltip))