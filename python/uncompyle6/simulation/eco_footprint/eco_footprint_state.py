# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\eco_footprint\eco_footprint_state.py
# Compiled at: 2020-02-20 16:06:47
# Size of source mod 2**32: 2519 bytes
import services, sims4
from display_snippet_tuning import DisplaySnippet
from sims4.tuning.tunable import TunableList, TunableReference

class EcoFootprintState(DisplaySnippet):
    INSTANCE_TUNABLES = {'effects': TunableList(description='\n            A list of StreetEffects that will be enabled when this\n            state is entered and disabled when this state is exited.\n            ',
                  tunable=TunableReference(description='\n                A Street Effect to include.\n                ',
                  manager=(services.get_instance_manager(sims4.resources.Types.SNIPPET)),
                  class_restrictions=('StreetEffect', ),
                  pack_safe=True))}

    def __init__(self, provider, **kwargs):
        self._provider = provider
        self._effect_instances = []
        self._enacted = False
        for effect in self.effects:
            self._effect_instances.append(effect())

    def finalize_startup(self, is_active):
        self._enacted = is_active
        for effect in self._effect_instances:
            effect.finalize_startup(self)

    @property
    def provider(self):
        return self._provider

    @property
    def enacted(self):
        return self._enacted

    def enter(self):
        self._enacted = True
        for effect in self._effect_instances:
            effect.enact()

    def exit(self):
        self._enacted = False
        for effect in self._effect_instances:
            effect.repeal()