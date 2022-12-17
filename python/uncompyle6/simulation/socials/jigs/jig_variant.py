# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\socials\jigs\jig_variant.py
# Compiled at: 2017-03-10 12:36:03
# Size of source mod 2**32: 919 bytes
from sims4.tuning.tunable import TunableVariant
from socials.jigs.jig_type_animation import SocialJigAnimation
from socials.jigs.jig_type_definition import SocialJigFromDefinition
from socials.jigs.jig_type_explicit import SocialJigExplicit
from socials.jigs.jig_type_legacy import SocialJigLegacy

class TunableJigVariant(TunableVariant):

    def __init__(self, **kwargs):
        (super().__init__)(definition=SocialJigFromDefinition.TunableFactory(), 
         explicit=SocialJigExplicit.TunableFactory(), 
         legacy=SocialJigLegacy.TunableFactory(), 
         animation=SocialJigAnimation.TunableFactory(), 
         default='definition', **kwargs)