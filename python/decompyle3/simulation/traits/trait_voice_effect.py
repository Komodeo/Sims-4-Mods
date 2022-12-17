# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\traits\trait_voice_effect.py
# Compiled at: 2016-03-17 17:22:56
# Size of source mod 2**32: 1283 bytes
from sims4.tuning.dynamic_enum import DynamicEnum
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory, TunableEnumEntry
from sims4.tuning.tunable_hash import TunableStringHash64

class VoiceEffectRequestPriority(DynamicEnum):
    INVALID = 0


class VoiceEffectRequest(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'voice_effect':TunableStringHash64(description='\n            When set, this voice effect will be applied to the Sim when the\n            trait is added and removed when the trait is removed.\n            '), 
     'priority':TunableEnumEntry(description='\n            The requests priority.\n            ',
       tunable_type=VoiceEffectRequestPriority,
       default=VoiceEffectRequestPriority.INVALID)}