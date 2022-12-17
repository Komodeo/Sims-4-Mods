# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\balloon\balloon_category.py
# Compiled at: 2018-03-01 13:29:23
# Size of source mod 2**32: 2480 bytes
import random
from balloon.balloon_enums import BalloonTypeEnum
from balloon.balloon_variant import BalloonVariant
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import HasTunableReference, TunableEnumEntry, TunablePercent, TunableList
from singletons import DEFAULT
import services, sims4.resources

class BalloonCategory(HasTunableReference, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.BALLOON)):
    INSTANCE_TUNABLES = {'balloon_type':TunableEnumEntry(description='\n             The visual style of the balloon background.\n             ',
       tunable_type=BalloonTypeEnum,
       default=BalloonTypeEnum.THOUGHT), 
     'balloon_chance':TunablePercent(description='\n             The chance that a balloon from the list is actually shown.\n             ',
       default=100), 
     'balloons':TunableList(description='\n             The list of possible balloons.\n             ',
       tunable=BalloonVariant.TunableFactory(balloon_type=None))}

    @classmethod
    def get_balloon_icons(cls, resolver, balloon_type=DEFAULT, gsi_category=None, **kwargs):
        if gsi_category is None:
            gsi_category = cls.__name__
        else:
            gsi_category = '{}/{}'.format(gsi_category, cls.__name__)
        possible_balloons = []
        if random.random() <= cls.balloon_chance:
            for balloon in cls.balloons:
                for balloon_icon in (balloon.get_balloon_icons)(resolver, balloon_type=cls.balloon_type, 
                 gsi_category=gsi_category, **kwargs):
                    if balloon_icon:
                        possible_balloons.append(balloon_icon)

        return possible_balloons