# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\aspirations\aspiration_instance_manager.py
# Compiled at: 2018-06-11 13:26:46
# Size of source mod 2**32: 753 bytes
from aspirations.aspiration_types import AspriationType
from sims4.tuning.instance_manager import InstanceManager
import sims4.log
logger = sims4.log.Logger('Aspirations')

class AspirationInstanceManager(InstanceManager):

    def all_whim_sets_gen(self):
        for aspiration in self.types.values():
            if aspiration.aspiration_type == AspriationType.WHIM_SET:
                yield aspiration