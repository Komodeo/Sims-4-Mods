# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\crafting\photography_service.py
# Compiled at: 2021-04-22 15:39:41
# Size of source mod 2**32: 2237 bytes
from sims4.callback_utils import CallableList
from sims4.service_manager import Service
import sims4.log
logger = sims4.log.Logger('Photography', default_owner='shipark')

class PhotographyService(Service):

    def __init__(self):
        self._loots = []
        self._callbacks = None

    def add_loot_for_next_photo_taken(self, loot):
        self._loots.append(loot)

    def apply_loot_for_photo(self, siminfo):
        for photoloot in self._loots:
            photoloot.apply_loot(siminfo)

    def get_loots_for_photo(self):
        return self._loots

    def add_callbacks(self, post_create_callbacks):
        if self._callbacks is not None:
            logger.error('Callbacks are still present in the photography service, which means we failed to clean them up previously.')
        self._callbacks = CallableList()
        for callback in post_create_callbacks:
            self._callbacks.register(callback)

    def run_callbacks(self, photo_object, photographer_sim, photo_resource_key, second_photo_resource_key):
        if self._callbacks is None:
            return
        self._callbacks(photo_object, sim=photographer_sim, photo_resource_key=photo_resource_key, second_photo_resource_key=second_photo_resource_key)

    def cleanup(self):
        self._loots = []
        self._callbacks = None

    def stop(self):
        self.cleanup()