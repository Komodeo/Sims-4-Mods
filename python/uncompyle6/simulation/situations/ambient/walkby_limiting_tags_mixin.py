# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\ambient\walkby_limiting_tags_mixin.py
# Compiled at: 2016-10-27 15:10:40
# Size of source mod 2**32: 1357 bytes
from tag import Tag
import services, sims4.tuning.tunable

class WalkbyLimitingTagsMixin:
    INSTANCE_TUNABLES = {'can_start_walkby_limiting_tags': sims4.tuning.tunable.TunableSet(description="\n            Don't start a situation of this type if another situation is\n            already running that has any of these tags in its tags field.\n            \n            For instance, if you only want one Streaker at a time you would\n            create a new tag SITUATION_STREAKER. Then set that in both this\n            field and in the tags field of situation_streaker.\n            ",
                                         tunable=sims4.tuning.tunable.TunableEnumWithFilter(tunable_type=Tag,
                                         default=(Tag.INVALID),
                                         filter_prefixes=[
                                        'situation']))}

    @classmethod
    def _can_start_walkby(cls, lot_id: int):
        return not services.get_zone_situation_manager().is_situation_with_tags_running(cls.can_start_walkby_limiting_tags)