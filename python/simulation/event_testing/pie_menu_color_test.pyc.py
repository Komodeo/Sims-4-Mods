# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\event_testing\pie_menu_color_test.py
# Compiled at: 2022-07-21 18:49:30
# Size of source mod 2**32: 1012 bytes
from event_testing.tests import TestListLoadingMixin
from sims.sim_info_tests import MoodTest
from sims4.tuning.tunable import TunableVariant
import event_testing

class TunablePieMenuColorTestVariant(TunableVariant):

    def __init__(self, **kwargs):
        tunables = {'mood': MoodTest.TunableFactory()}
        kwargs.update(tunables)
        (super().__init__)(**kwargs)


class PieMenuColorTestList(event_testing.tests.TestListLoadingMixin):
    DEFAULT_LIST = event_testing.tests.TestList()

    def __init__(self, description=None):
        super().__init__(description=description, tunable=(TunablePieMenuColorTestVariant()))