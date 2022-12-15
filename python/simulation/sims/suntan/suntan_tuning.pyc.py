# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\suntan\suntan_tuning.py
# Compiled at: 2019-05-08 11:33:02
# Size of source mod 2**32: 1173 bytes
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, TunableEnumEntry
import enum

class TanLevel(enum.Int):
    NO_TAN = 0
    DEEP = 1
    SUNBURNED = 2


class ChangeTanLevel(HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'tan_level': TunableEnumEntry(description='\n            The tan level to set for the Sim.\n            ',
                    tunable_type=TanLevel,
                    default=(TanLevel.NO_TAN))}

    def __init__(self, target, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.target = target

    def start(self):
        suntan_tracker = self.target.sim_info.suntan_tracker
        suntan_tracker.set_tan_level(tan_level=(self.tan_level))

    def stop(self, *_, **__):
        pass