# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\crafting\set_photo_filter.py
# Compiled at: 2019-05-09 10:42:28
# Size of source mod 2**32: 1682 bytes
from crafting.photography_enums import PhotoStyleType
from interactions import ParticipantTypeSingle, ParticipantType
from interactions.utils.interaction_elements import XevtTriggeredElement
from sims4.tuning.tunable import TunableEnumEntry
import sims4
logger = sims4.log.Logger('Photography', default_owner='rrodgers')

class SetPhotoFilter(XevtTriggeredElement):
    FACTORY_TUNABLES = {'participant':TunableEnumEntry(description='\n            The participant object that is the photo.\n            ',
       tunable_type=ParticipantTypeSingle,
       default=ParticipantType.Object), 
     'photo_filter':TunableEnumEntry(description='\n            The photo filter that you want this photo to use.\n            ',
       tunable_type=PhotoStyleType,
       default=PhotoStyleType.NORMAL)}

    def _do_behavior(self):
        photo_obj = self.interaction.get_participant(self.participant)
        if photo_obj is None:
            logger.error('set_photo_filter basic extra tuned participant does not exist.')
            return False
        canvas_component = photo_obj.canvas_component
        if canvas_component is None:
            logger.error('set_photo_filter basic extra tuned participant does not have a canvas component.')
            return False
        canvas_component.painting_effect = self.photo_filter
        return True