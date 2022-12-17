# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\pregnancy\pregnancy_client_mixin.py
# Compiled at: 2016-03-30 15:27:02
# Size of source mod 2**32: 881 bytes
from sims4.math import clamp
import distributor.fields, distributor.ops

class PregnancyClientMixin:

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._pregnancy_progress = 0

    @distributor.fields.Field(op=(distributor.ops.SetPregnancyProgress), default=None)
    def pregnancy_progress(self):
        return self._pregnancy_progress

    @pregnancy_progress.setter
    def pregnancy_progress(self, value):
        self._pregnancy_progress = clamp(0, value, 1) if value is not None else None