# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\cas\cas_stories_question.py
# Compiled at: 2019-04-15 16:03:11
# Size of source mod 2**32: 2000 bytes
import services, sims4
from cas.cas_stories_answer import CasStoriesAnswer
from interactions.utils.tunable_icon import TunableIcon
from sims4.common import Pack
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import HasTunableReference, TunableList, TunableEnumEntry
from sims4.tuning.tunable_base import ExportModes, GroupNames

class CasStoriesQuestion(HasTunableReference, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.CAS_STORIES_QUESTION)):
    INSTANCE_TUNABLES = {'text':TunableLocalizedStringFactory(description='\n            The text of this question.\n            ',
       export_modes=ExportModes.ClientBinary,
       tuning_group=GroupNames.UI), 
     'icon':TunableIcon(description='\n            The icon for this question.\n            ',
       export_modes=ExportModes.ClientBinary,
       tuning_group=GroupNames.UI), 
     'possible_answers':TunableList(description='\n            Answers to this question.\n            ',
       tunable=CasStoriesAnswer.TunableReference(),
       export_modes=ExportModes.ClientBinary), 
     'pack':TunableEnumEntry(description='\n            The pack with which this question is associated. Will affect when\n            and how frequently this answer is selected by CAS Stories.\n            ',
       tunable_type=Pack,
       default=Pack.BASE_GAME,
       export_modes=ExportModes.ClientBinary)}