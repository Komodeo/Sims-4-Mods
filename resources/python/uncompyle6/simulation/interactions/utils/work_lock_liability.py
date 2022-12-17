# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\utils\work_lock_liability.py
# Compiled at: 2016-11-09 11:43:03
# Size of source mod 2**32: 1026 bytes
from interactions.liability import Liability

class WorkLockLiability(Liability):
    LIABILITY_TOKEN = 'MasterControllerLockLiability'

    def __init__(self, *args, sim, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._sim = sim

    def on_add(self, interaction):
        self._sim.add_work_lock(self)

    def merge(self, interaction, key, new_liability):
        self.release()
        return super().merge(interaction, key, new_liability)

    def release(self):
        self._sim.remove_work_lock(self)