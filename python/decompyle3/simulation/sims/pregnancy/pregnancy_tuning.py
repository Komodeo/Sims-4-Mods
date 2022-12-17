# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\pregnancy\pregnancy_tuning.py
# Compiled at: 2019-01-16 19:02:44
# Size of source mod 2**32: 1733 bytes
from sims.sim_dialogs import SimPersonalityAssignmentDialog
from sims.sim_info_types import Species
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory, TunableMapping, TunableEnumEntry
from snippets import define_snippet
from ui.ui_dialog_generic import TEXT_INPUT_FIRST_NAME, TEXT_INPUT_LAST_NAME

class PregnancyData(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'dialog': SimPersonalityAssignmentDialog.TunableFactory(description="\n            The dialog that is displayed when an offspring is created. It allows\n            the player to enter a first and last name for the Sim. An additional\n            token is passed in: the offspring's Sim data.\n            ",
                 text_inputs=(
                TEXT_INPUT_FIRST_NAME, TEXT_INPUT_LAST_NAME))}


TunablePregnancyDataReference, _ = define_snippet('Pregnancy', PregnancyData.TunableFactory())

class PregnancyTuning:
    PREGNANCY_DATA = TunableMapping(description='\n        A mapping of species to pregnancy data.\n        ',
      key_type=TunableEnumEntry(description="\n            The newborn's species.\n            ",
      tunable_type=Species,
      default=(Species.HUMAN),
      invalid_enums=(
     Species.INVALID,)),
      value_type=TunablePregnancyDataReference(pack_safe=True))

    @classmethod
    def get_pregnancy_data(cls, sim_info):
        return cls.PREGNANCY_DATA.get(sim_info.species)