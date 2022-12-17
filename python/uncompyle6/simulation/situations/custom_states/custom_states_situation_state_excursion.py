# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\custom_states\custom_states_situation_state_excursion.py
# Compiled at: 2020-04-09 20:07:21
# Size of source mod 2**32: 620 bytes
from situations.custom_states.custom_states_situation_states import CustomStatesSituationState
from snippets import define_snippet, EXCURSION_SITUATION_STATE

class ExcursionSituationState(CustomStatesSituationState):
    pass


TunableExcursionSituationStateReference, TunableExcursionSituationStateSnippet = define_snippet(EXCURSION_SITUATION_STATE, ExcursionSituationState.TunableFactory())