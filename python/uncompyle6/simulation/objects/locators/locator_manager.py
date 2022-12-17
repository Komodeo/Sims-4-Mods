# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\locators\locator_manager.py
# Compiled at: 2018-11-26 11:47:21
# Size of source mod 2**32: 4284 bytes
from _collections import defaultdict
from objects.locators.locator import LocatorObject
from sims4.callback_utils import CallableList
from sims4.service_manager import Service
import services, tag

class LocatorManager(Service):
    SPAWN_TAG_PREFIX = 'spawn_'

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._locators = defaultdict(list)
        self._spawn_point_definitions = set()
        self._locators_changed_callbacks = CallableList()

    def __contains__(self, key):
        if not isinstance(key, int):
            raise TypeError('LocatorManager keys must be integers.')
        return key in self._locators

    def __getitem__(self, key):
        if not isinstance(key, int):
            raise TypeError('LocatorManager keys must be integers.')
        return self._locators[key]

    def __iter__(self):
        return iter(self._locators)

    def __len__(self):
        return len(self._locators)

    def __bool__(self):
        if self._locators:
            return True
        return False

    def get(self, key):
        return self._locators.get(key, ())

    def keys(self):
        return self._locators.keys()

    def values(self):
        return self._locators.values()

    def items(self):
        return self._locators.items()

    def register_locators_changed_callback(self, callback):
        self._locators_changed_callbacks.append(callback)

    def unregister_locators_changed_callback(self, callback):
        if callback in self._locators_changed_callbacks:
            self._locators_changed_callbacks.remove(callback)

    def _is_locator_for_spawn_point(self, locator):
        tags = locator.get_tags()
        if locator.obj_def_guid in self._spawn_point_definitions:
            return True
        if locator.obj_def_guid in self._locators:
            return False
        for tag_val in tags:
            if self.SPAWN_TAG_PREFIX in str(tag.Tag.value_to_name[tag_val]).lower():
                self._spawn_point_definitions.add(locator.obj_def_guid)
                return True

        return False

    def set_up_locators(self, locator_data_array):
        spawn_point_locators = []
        for locator_data in locator_data_array:
            locator = LocatorObject(*locator_data)
            if self._is_locator_for_spawn_point(locator):
                spawn_point_locators.append(locator)
                continue
            self._locators[locator.obj_def_guid].append(locator)

        services.current_zone().set_up_world_spawn_points(spawn_point_locators)