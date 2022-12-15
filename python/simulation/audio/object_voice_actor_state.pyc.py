# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\audio\object_voice_actor_state.py
# Compiled at: 2021-02-18 19:06:16
# Size of source mod 2**32: 2286 bytes
from audio.audio_constants import SuffixType
from distributor.ops import ElementDistributionOpMixin
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, OptionalTunable, TunableMapping, TunableEnumEntry
from sims4.tuning.tunable_hash import TunableStringHash32
import sims4.log
logger = sims4.log.Logger('SetObjectVoiceActorState', default_owner='yozhang')

class SetObjectVoiceActorState(ElementDistributionOpMixin, HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'actor_audio_suffix_override': TunableMapping(description="\n             We can override an object or sims' voice actor. This will be sent to Client,\n            then when audio request the actor suffix, we check for this override\n            on the object.\n            If the mapping is left empty, then no overrides will be applied and existing overrides will be removed.",
                                      key_type=TunableEnumEntry(description='The audio suffix type to override as in audio_constants.py ', tunable_type=SuffixType,
                                      default=(SuffixType.SUFFIX_ACTOR)),
                                      value_type=(TunableStringHash32()))}

    def __init__(self, target, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._target = target
        self._previous_actor = None

    def start(self, *args, **kwargs):
        for suffix_type, suffix_value in self.actor_audio_suffix_override.items():
            if suffix_type is SuffixType.SUFFIX_ACTOR and self._target.is_sim:
                self._previous_actor = self._target.voice_actor
                self._target.voice_actor = suffix_value
            else:
                self._target.add_voice_suffix_override(suffix_type, suffix_value)

    def stop(self, *args, **kwargs):
        if self._previous_actor is not None:
            self._target.voice_actor = self._previous_actor
        for suffix_type in self.actor_audio_suffix_override.keys():
            self._target.remove_voice_suffix_override(suffix_type)