# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\situation_zone_director_mixin.py
# Compiled at: 2015-06-24 18:26:37
# Size of source mod 2**32: 1122 bytes
from zone_director import ZoneDirectorBase

class SituationZoneDirectorMixin:
    INSTANCE_TUNABLES = {'_zone_director': ZoneDirectorBase.TunableReference(description='\n            This zone director will automatically be requested by the situation\n            during zone spin up.\n            ')}

    @classmethod
    def get_zone_director_request(cls):
        return (
         cls._zone_director(), cls._get_zone_director_request_type())

    @classmethod
    def _get_zone_director_request_type(cls):
        raise NotImplementedError