# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\careers\acting\stage_mark_component.py
# Compiled at: 2018-04-25 18:20:19
# Size of source mod 2**32: 664 bytes
from objects.components import Component, types

class StageMarkComponent(Component, allow_dynamic=True, component_name=types.STAGE_MARK_COMPONENT):

    def __init__(self, *args, performance_interactions=(), **kwargs):
        (super().__init__)(*args, **kwargs)
        self._performance_interactions = performance_interactions

    def component_super_affordances_gen(self, **kwargs):
        yield from self._performance_interactions
        if False:
            yield None