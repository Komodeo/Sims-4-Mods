# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\global_flags\global_flag_service.py
# Compiled at: 2021-06-01 14:43:27
# Size of source mod 2**32: 736 bytes
from sims4.service_manager import Service

class GlobalFlagService(Service):

    def __init__(self):
        self._flags = 0

    def add_flag(self, flag):
        self._flags |= flag

    def remove_flag(self, flag):
        self._flags &= ~flag

    def has_any_flag(self, flags):
        return bool(self._flags & flags)