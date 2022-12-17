# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\animation\awareness\awareness_elements.py
# Compiled at: 2016-06-06 11:26:43
# Size of source mod 2**32: 1163 bytes
from element_utils import build_critical_section_with_finally
from animation.awareness.awareness_enums import AwarenessChannel
from animation.awareness.awareness_tuning import AwarenessSourceRequest

def with_audio_awareness(*actors, sequence=()):
    awareness_modifiers = []

    def begin(_):
        for actor in actors:
            if actor is None:
                continue
            if actor.is_sim:
                continue
            else:
                awareness_modifier = AwarenessSourceRequest(actor, awareness_sources={AwarenessChannel.AUDIO_VOLUME: 1})
                awareness_modifier.start()
                awareness_modifiers.append(awareness_modifier)

    def end(_):
        for awareness_modifier in awareness_modifiers:
            awareness_modifier.stop()

    return build_critical_section_with_finally(begin, sequence, end)