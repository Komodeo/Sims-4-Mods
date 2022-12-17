# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\fixup\sim_info_favorites_fixup_action.py
# Compiled at: 2020-07-28 09:38:17
# Size of source mod 2**32: 2528 bytes
from sims.fixup.sim_info_fixup_action import _SimInfoFixupAction
from sims4.tuning.tunable import TunableList, TunableCasPart, TunableReference, TunableTuple, TunableRange
from tag import TunableTag
import services, sims4.random

class _SimInfoFavoritesFixupAction(_SimInfoFixupAction):
    FACTORY_TUNABLES = {'favorite_info_list': TunableList(description='\n            A List of favorite categories to randomly set on new Sims.\n            ',
                             tunable=TunableTuple(description='\n                Tuple containing a tag to set the favorite of, and a list of object definitions\n                and weights to choose for the favorite.\n                ',
                             favorite_tag=TunableTag(description='\n                    The tag to set the favorite of.\n                    ',
                             filter_prefixes=('Func', )),
                             favorite_definition_ids=TunableList(description='\n                    A list of tuples of object definitions, and corresponding weights \n                    One definition is chosen by a weighted random and set as the favorite \n                    for the tag above. \n                    ',
                             tunable=TunableTuple(weight=TunableRange(description='\n                            The weight to use for the choosing of this object. Any positive value works.\n                            ',
                             tunable_type=float,
                             default=1.0,
                             minimum=0),
                             object=TunableReference(description='\n                            The definition of the object to choose as a favorite.\n                            ',
                             manager=(services.definition_manager()))))))}

    def __call__(self, sim_info):
        favorites_tracker = sim_info.favorites_tracker
        if favorites_tracker is None:
            return
        for favorite_info in self.favorite_info_list:
            favorite = sims4.random.weighted_random_item((favorite_info.favorite_definition_ids), flipped=True)
            favorites_tracker.set_favorite(favorite_info.favorite_tag, None, favorite.id)