# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\game_effect_modifier\pie_menu_modifier.py
# Compiled at: 2020-03-12 15:31:06
# Size of source mod 2**32: 1557 bytes
from game_effect_modifier.base_game_effect_modifier import BaseGameEffectModifier
from game_effect_modifier.game_effect_type import GameEffectType
from interactions.utils.affordance_filter import AffordanceFilterVariant
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.tunable import OptionalTunable, HasTunableSingletonFactory, AutoFactoryInit

class PieMenuModifier(HasTunableSingletonFactory, AutoFactoryInit, BaseGameEffectModifier):
    FACTORY_TUNABLES = {'affordance_filter':AffordanceFilterVariant(description='\n            Affordances this modifier affects.\n            '), 
     'suppression_tooltip':OptionalTunable(description='\n            If supplied, interactions are disabled with this tooltip.\n            Otherwise, interactions are hidden.\n            ',
       tunable=TunableLocalizedStringFactory(description='Reason of failure.'))}

    def __init__(self, **kwargs):
        (super().__init__)((GameEffectType.PIE_MENU_MODIFIER), **kwargs)

    def affordance_is_allowed(self, affordance):
        return self.affordance_filter(affordance)