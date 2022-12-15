# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\fixup\sim_info_outfit_fixup_actions.py
# Compiled at: 2020-09-23 09:26:17
# Size of source mod 2**32: 3021 bytes
from sims.fixup.sim_info_fixup_action import _SimInfoFixupAction
from sims.outfits.outfit_enums import OutfitCategory
from sims.outfits.outfit_generator import TunableOutfitGeneratorSnippet, OutfitGenerator
from sims4.tuning.tunable import TunableEnumEntry, Tunable

class _SimInfoOutfitTransferFixupAction(_SimInfoFixupAction):
    FACTORY_TUNABLES = {'source_outfit_category':TunableEnumEntry(description='\n            ',
       tunable_type=OutfitCategory,
       default=OutfitCategory.SITUATION,
       invalid_enums=(
      OutfitCategory.CURRENT_OUTFIT,)), 
     'destination_outfit_category':TunableEnumEntry(description='\n            ',
       tunable_type=OutfitCategory,
       default=OutfitCategory.CAREER,
       invalid_enums=(
      OutfitCategory.CURRENT_OUTFIT, OutfitCategory.SPECIAL)), 
     'set_destination_outfit':Tunable(description='\n            Whether to immediately set the destination outfit upon add to household.\n            ',
       tunable_type=bool,
       default=False)}

    def __call__(self, sim_info):
        destination_outfit = (
         self.destination_outfit_category, 0)
        sim_info.generate_merged_outfit(sim_info, destination_outfit,
          (sim_info.get_current_outfit()),
          (
         self.source_outfit_category, 0),
          preserve_outfit_flags=True)
        if self.set_destination_outfit:
            sim_info.set_current_outfit(destination_outfit)


class _SimInfoRandomizeOutfitFixupAction(_SimInfoFixupAction):
    FACTORY_TUNABLES = {'outfit_to_randomize':TunableEnumEntry(description='\n            ',
       tunable_type=OutfitCategory,
       default=OutfitCategory.EVERYDAY,
       invalid_enums=(
      OutfitCategory.CURRENT_OUTFIT, OutfitCategory.SPECIAL)), 
     'generator':TunableOutfitGeneratorSnippet()}

    def __call__(self, sim_info):
        OutfitGenerator.generate_outfit(self, sim_info, self.outfit_to_randomize)