# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\audio\audio_effect_data.py
# Compiled at: 2018-07-16 18:27:57
# Size of source mod 2**32: 859 bytes


class AudioEffectData:

    def __init__(self, effect_id, track_flags=None):
        self._effect_id = effect_id
        self._track_flags = track_flags

    @property
    def effect_id(self):
        return self._effect_id

    @property
    def track_flags(self):
        return self._track_flags