# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\fixup\sim_info_fixup_action.py
# Compiled at: 2020-05-01 12:47:38
# Size of source mod 2**32: 920 bytes
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit
import enum

class SimInfoFixupActionTiming(enum.Int):
    ON_FIRST_SIMINFO_LOAD = 0
    ON_ADDED_TO_ACTIVE_HOUSEHOLD = 1
    ON_SIM_INFO_CREATED = 2


class _SimInfoFixupAction(HasTunableSingletonFactory, AutoFactoryInit):

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.fixup_guid = 0

    def __call__(self, sim_info):
        raise NotImplementedError