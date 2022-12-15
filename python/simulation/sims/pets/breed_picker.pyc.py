# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\pets\breed_picker.py
# Compiled at: 2019-01-16 19:02:32
# Size of source mod 2**32: 4342 bytes
from interactions.base.picker_interaction import PickerSuperInteraction
from sims import sim_spawner
from sims.pets.breed_tuning import all_breeds_gen
from sims.sim_info_types import SpeciesExtended
from sims4.localization import TunableLocalizedString, LocalizationHelperTuning
from sims4.tuning.tunable import TunableMapping, TunableEnumEntry
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import flexmethod
from ui.ui_dialog_picker import TunablePickerDialogVariant, ObjectPickerTuningFlags, BasePickerRow
import sims4
logger = sims4.log.Logger('BreedPickerSuperInteraction')

class BreedPickerSuperInteraction(PickerSuperInteraction):
    INSTANCE_TUNABLES = {'picker_dialog':TunablePickerDialogVariant(description='\n            The item picker dialog.\n            ',
       available_picker_flags=ObjectPickerTuningFlags.ITEM,
       default='item_picker',
       tuning_group=GroupNames.PICKERTUNING), 
     'species_name':TunableMapping(description="\n            If specified, for a particular species, include this text in the\n            breed's name.\n            ",
       key_type=TunableEnumEntry(tunable_type=SpeciesExtended,
       default=(SpeciesExtended.HUMAN),
       invalid_enums=(
      SpeciesExtended.INVALID,)),
       value_type=TunableLocalizedString(),
       tuning_group=GroupNames.PICKERTUNING)}

    def _run_interaction_gen(self, timeline):
        self._show_picker_dialog(self.sim)
        return True
        if False:
            yield None

    @flexmethod
    def picker_rows_gen(cls, inst, target, context, **kwargs):
        if inst is not None:
            breed_species = []
            species = inst.interaction_parameters['species']
            for species_extended in SpeciesExtended:
                if species_extended == SpeciesExtended.INVALID:
                    continue
                if SpeciesExtended.get_species(species_extended) == species:
                    breed_species.append(species_extended)

        else:
            breed_species = (None, )
        for _breed_species in breed_species:
            for breed in all_breeds_gen(species=_breed_species):
                name = breed.breed_display_name
                if _breed_species in cls.species_name:
                    name = LocalizationHelperTuning.NAME_VALUE_PARENTHESIS_PAIR_STRUCTURE(name, cls.species_name[_breed_species])
                else:
                    row = BasePickerRow(name=name, row_description=(breed.breed_description), tag=breed)
                    yield row

    def on_choice_selected(self, choice_tag, **kwargs):
        breed = choice_tag
        if breed is not None:
            position = self.context.pick.location
            actor_sim_info = self.sim.sim_info
            params = self.interaction_parameters
            age = params['age']
            gender = params['gender']
            species = breed.breed_species
            sim_creator = sim_spawner.SimCreator(age=age, gender=gender, species=species, additional_tags=(breed.breed_tag,))
            sim_info_list, _ = sim_spawner.SimSpawner.create_sim_infos((sim_creator,), account=(actor_sim_info.account),
              zone_id=(actor_sim_info.zone_id),
              creation_source='cheat: BreedPickerSuperInteraction')
            sim_info = sim_info_list[0]
            sim_spawner.SimSpawner.spawn_sim(sim_info, sim_position=position,
              is_debug=True)