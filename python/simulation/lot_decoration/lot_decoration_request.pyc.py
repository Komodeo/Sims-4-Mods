# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\lot_decoration\lot_decoration_request.py
# Compiled at: 2018-03-21 17:17:37
# Size of source mod 2**32: 2647 bytes
from lot_decoration.decoration_provider import DEFAULT_DECORATION_TYPE
from lot_decoration.lot_decoration_enums import LOT_DECORATION_DEFAULT_ID
import enum, services

class LotDecorationPriority(enum.Int, export=False):
    DEFAULT = 0
    PRE_HOLIDAY = ...
    HOLIDAY = ...


class LotDecorationRequestBase:

    @property
    def priority(self):
        raise NotImplementedError

    @property
    def provider(self):
        raise NotImplementedError


class EverydayDecorationRequest:

    @property
    def priority(self):
        return LotDecorationPriority.DEFAULT

    @property
    def provided_type(self):
        return LOT_DECORATION_DEFAULT_ID


EVERYDAY_DECORATION_REQUEST = EverydayDecorationRequest()

class HolidayDecorationRequest:

    def __init__(self, holiday_drama_node):
        self._drama_node = holiday_drama_node

    @property
    def priority(self):
        if not self._drama_node.is_running:
            return LotDecorationPriority.PRE_HOLIDAY
        if self._drama_node.holiday is services.active_household().holiday_tracker.active_holiday_id:
            return LotDecorationPriority.HOLIDAY
        return LotDecorationPriority.PRE_HOLIDAY

    @property
    def provided_type(self):
        return self._drama_node.holiday_id