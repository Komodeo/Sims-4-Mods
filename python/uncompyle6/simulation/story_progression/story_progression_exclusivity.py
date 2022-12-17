# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\story_progression\story_progression_exclusivity.py
# Compiled at: 2022-03-10 17:35:10
# Size of source mod 2**32: 3897 bytes
from sims4.tuning.dynamic_enum import DynamicEnumFlags
from sims4.tuning.tunable import TunableList, TunableTuple, TunableEnumEntry

class StoryProgressionExclusivityCategory(DynamicEnumFlags):
    NEUTRAL = 0


class StoryProgressionExclusivity:
    EXCLUSIVITY_RULES = TunableList(description='\n        A list of exclusivity rules.  Each exclusivity rule is a pair of  Story Progression\n        Exclusivity Categories.  Categories are bi directional so you do not need to tune both directions of\n        categories.\n        \n        Any rules that are tuned make it so that when seeding a new arc we will not seed the arc on Sims that have\n        an incompatible category on them or on the household.  With households we will check the exclusivity against\n        all of the arcs on Sims within the household.\n        \n        If an exclusivity pair is not tuned here that means that they are compatible.  The Neutral category is always\n        compatible with everything.\n        \n        Example:\n        If you want two groups of arcs to be incompatible with each other, tune each exclusivity category.\n        category 1: DEATH\n        category 2: CAREER\n        This will make it so that if a death arc is on a Sim then a career arc will not be added and vice versa if a\n        career arc is on a Sim then a death arc will not be added.\n        \n        If you want to create a mutually incompatible grouping of arcs, tune the same exclusivity category twice.\n        category 1: CAREER\n        category 2: CAREER\n        This will make it so that multiple different career arcs cannot be placed on the same Sim.  This can be used\n        to prevent adding a career and retiring/quitting a career to be tuned at the same time.\n        ',
      tunable=TunableTuple(description='\n            An exclusivity rule.\n            \n            Please read the Exclusivity Rules Definition for how to use this.\n            ',
      category_1=TunableEnumEntry(description='\n                The first Exclusivity Category.\n                \n                Please read the Exclusivity Rules Definition for how to use this.\n                ',
      tunable_type=StoryProgressionExclusivityCategory,
      default=(StoryProgressionExclusivityCategory.NEUTRAL),
      invalid_enums=(
     StoryProgressionExclusivityCategory.NEUTRAL,)),
      category_2=TunableEnumEntry(description='\n                The second. Exclusivity Category.\n                \n                Please read the Exclusivity Rules Definition for how to use this.\n                ',
      tunable_type=StoryProgressionExclusivityCategory,
      default=(StoryProgressionExclusivityCategory.NEUTRAL),
      invalid_enums=(
     StoryProgressionExclusivityCategory.NEUTRAL,))))
    EXCLUSIVITY = None

    @classmethod
    def are_story_progression_arcs_compatible(cls, arc_1, arc_2):
        if cls.EXCLUSIVITY is None:
            cls.EXCLUSIVITY = set()
            for exclusivity_rule in cls.EXCLUSIVITY_RULES:
                rule = exclusivity_rule.category_1 | exclusivity_rule.category_2
                cls.EXCLUSIVITY.add(rule)

        target_rule = arc_1.exclusivity_category | arc_2.exclusivity_category
        return target_rule not in cls.EXCLUSIVITY