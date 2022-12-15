# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\autonomy\autonomy_liabilities.py
# Compiled at: 2017-06-08 16:33:37
# Size of source mod 2**32: 609 bytes
from interactions.liability import Liability

class AutonomousGetComfortableLiability(Liability):
    LIABILITY_TOKEN = 'AutonomousGetComfortable'

    def __init__(self, sim, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._sim = sim

    def release(self):
        self._sim.push_get_comfortable_interaction()