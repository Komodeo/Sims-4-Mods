# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\autonomy\autonomy_outside_supression.py
# Compiled at: 2018-02-23 16:42:39
# Size of source mod 2**32: 2610 bytes
import functools, operator, services, sims4
logger = sims4.log.Logger('OutsideSupressor', default_owner='camilogarcia')

class OutsideSupressor:

    def __init__(self):
        self._outside_lock_counter = 0
        self._outside_unlock_counter = 0
        self.outside_multiplier = 1
        self._outside_multiplier_list = []

    def is_not_allowed_outside(self):
        if not (self._outside_unlock_counter > 0 or services.time_service().is_sun_out()):
            return False
        return self._outside_lock_counter > 0

    def add_lock_counter(self):
        self._outside_lock_counter += 1

    def remove_lock_counter(self):
        if self._outside_lock_counter == 0:
            logger.error('Trying to remove a lock from a Sim that had no locks applied')
            return
        self._outside_lock_counter -= 1

    def add_multiplier(self, value):
        self._outside_multiplier_list.append(value)
        self.outside_multiplier *= value

    def remove_multiplier(self, value):
        self._outside_multiplier_list.remove(value)
        self.outside_multiplier = functools.reduce(operator.mul, self._outside_multiplier_list, 1)

    def add_unlock_counter(self):
        self._outside_unlock_counter += 1

    def remove_unlock_counter(self):
        if self._outside_unlock_counter == 0:
            logger.error('Trying to remove an unlock from a Sim that had no locks applied')
            return
        self._outside_unlock_counter -= 1