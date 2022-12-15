# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\audio\tunable_audio.py
# Compiled at: 2019-06-05 15:07:17
# Size of source mod 2**32: 648 bytes
from sims4.resources import Types
from sims4.tuning.tunable import TunablePackSafeResourceKey

class TunableAudioAllPacks(TunablePackSafeResourceKey):

    def __init__(self, *, description='The audio file.', **kwargs):
        (super().__init__)(None, resource_types=(Types.PROPX,), description=description, **kwargs)

    @property
    def validate_pack_safe(self):
        return False