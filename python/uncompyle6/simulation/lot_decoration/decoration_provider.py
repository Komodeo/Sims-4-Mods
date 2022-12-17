# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\lot_decoration\decoration_provider.py
# Compiled at: 2018-04-11 18:38:49
# Size of source mod 2**32: 1529 bytes
from lot_decoration.lot_decoration_enums import LOT_DECORATION_DEFAULT_ID
import services
DEFAULT_DECORATION_TYPE = 'DefaultDecorations'

class DefaultDecorationProvider:

    @property
    def decoration_preset(self):
        pass

    @property
    def decoration_type_id(self):
        return LOT_DECORATION_DEFAULT_ID


DEFAULT_DECORATION_PROVIDER = DefaultDecorationProvider()

class HolidayDecorationProvider:

    def __init__(self, holiday_id):
        self._holiday_id = holiday_id

    @property
    def decoration_preset(self):
        return services.holiday_service().get_decoration_preset(self._holiday_id)

    @property
    def decoration_type_id(self):
        return self._holiday_id