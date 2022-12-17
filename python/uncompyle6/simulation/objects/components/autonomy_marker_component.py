# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\autonomy_marker_component.py
# Compiled at: 2019-09-23 18:22:29
# Size of source mod 2**32: 529 bytes
from objects.components import Component, types
from sims4.tuning.tunable import HasTunableFactory
import services

class AutonomyMarkerComponent(Component, HasTunableFactory, component_name=types.AUTONOMY_MARKER_COMPONENT):

    def on_remove(self):
        services.current_zone().clear_autonomy_area()