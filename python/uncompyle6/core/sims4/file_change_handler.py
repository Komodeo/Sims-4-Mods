# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\sims4\file_change_handler.py
# Compiled at: 2012-05-01 16:50:39
# Size of source mod 2**32: 2199 bytes
import sims4.log, sims4.resources
logger = sims4.log.Logger('File Change Handler')

class FileChangeHandler:

    def __init__(self, name=None, type_filter=None, group_filter=None):
        self._registration_key = None
        self._name = name
        if type_filter is None:
            self._type_filter = sims4.resources.Types.INVALID
        else:
            self._type_filter = type_filter
        if group_filter is None:
            self._group_filter = sims4.resources.Groups.INVALID
        else:
            self._group_filter = group_filter

    def _handle(self, key):
        raise NotImplementedError('_handle not implemented in a FileChangeHandler subclass')

    def start(self):
        self._registration_key = sims4.resources.register_change_notification((self._handle), group_filter=(self._group_filter), type_filter=(self._type_filter))
        return self._registration_key is not None

    def stop(self):
        sims4.resources.unregister_change_notification(self._registration_key)
        self._registration_key = None