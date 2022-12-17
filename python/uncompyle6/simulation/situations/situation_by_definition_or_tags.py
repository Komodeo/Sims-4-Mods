# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\situation_by_definition_or_tags.py
# Compiled at: 2017-08-14 12:39:55
# Size of source mod 2**32: 3602 bytes
from sims4.resources import Types
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory, TunableSet, TunableReference, TunableVariant
from tag import TunableTags
import services

class _SituationMatchBase:

    def get_situations_for_sim_info(self, sim_info):
        sim = sim_info.get_sim_instance()
        if sim is None:
            return ()
        situation_manager = services.get_zone_situation_manager()
        situations = set((s for s in situation_manager.get_situations_sim_is_in(sim) if self.match(s)))
        return situations

    def get_all_matching_situations(self):
        situation_manager = services.get_zone_situation_manager()
        situations = set((s for s in situation_manager.running_situations() if self.match(s)))
        return situations

    def match(self, situation):
        raise NotImplementedError('Match must be implemented by subclasses of _SituationMatchBase!')


class SituationByDefinition(_SituationMatchBase, HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'situations': TunableSet(description='\n            Situation types to match.\n            ',
                     tunable=TunableReference(manager=(services.get_instance_manager(Types.SITUATION)),
                     pack_safe=True),
                     minlength=1)}

    def match(self, situation):
        return type(situation) in self.situations


class SituationByTags(_SituationMatchBase, HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'situation_tags': TunableTags(description='\n            Situation tags to match.\n            \n            A situation that matches ANY of these tags will match.\n            ',
                         filter_prefixes=('situation', ),
                         minlength=1)}

    def match(self, situation):
        return self.situation_tags & situation.tags


class SituationSearchByDefinitionOrTagsVariant(TunableVariant):

    def __init__(self, *args, **kwargs):
        (super().__init__)(args, by_definition=SituationByDefinition.TunableFactory(), 
         by_tags=SituationByTags.TunableFactory(), 
         default='by_definition', **kwargs)