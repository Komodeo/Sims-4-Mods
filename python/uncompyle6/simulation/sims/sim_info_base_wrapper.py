# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\sim_info_base_wrapper.py
# Compiled at: 2022-07-21 18:49:30
# Size of source mod 2**32: 42123 bytes
from contextlib import contextmanager, ExitStack
import random, weakref
from distributor.system import Distributor
from protocolbuffers.Localization_pb2 import LocalizedStringToken
from buffs.appearance_modifier.appearance_tracker import AppearanceTracker
from cas.cas import BaseSimInfo, generate_offspring, generate_merged_outfit, is_duplicate_merged_outfit
from distributor.shared_messages import IconInfoData
from sims.baby.baby_tuning import BabyTuning
from sims.outfits.outfit_enums import OutfitCategory, OutfitFilterFlag, BodyTypeFlag
from sims.outfits.outfit_tracker import OutfitTrackerMixin
from sims.sim_info_types import Gender, Age, SpeciesExtended, Species
from sims4.callback_utils import CallableList, protected_callback
from sims4.log import StackVar
from singletons import DEFAULT, EMPTY_SET
import distributor.fields, distributor.ops, id_generator, sims4.log
logger = sims4.log.Logger('SimInfoBaseWrapper')

class SimInfoBaseWrapper(OutfitTrackerMixin):

    def __init__(self, *args, sim_id=0, gender=Gender.MALE, age=Age.ADULT, species=SpeciesExtended.HUMAN, first_name='', last_name='', breed_name='', full_name_key=0, breed_name_key=0, physique='', skin_tone=1, skin_tone_val_shift=0.0, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.sim_id = sim_id or id_generator.generate_object_id()
        self.primitives = distributor.ops.DistributionSet(self)
        self.manager = None
        self._base = BaseSimInfo(sim_id, first_name, last_name, breed_name, full_name_key, breed_name_key, age, gender, species, skin_tone, physique, skin_tone_val_shift)
        self._base.voice_pitch = 0.0
        self._base.voice_actor = 0
        self._base.voice_effect = 0
        self._base.facial_attributes = ''
        self._base.custom_texture = 0
        self._base.pelt_layers = ''
        self._species = SpeciesExtended.get_species(species)
        self.on_base_characteristic_changed = CallableList()
        self.on_outfit_changed = CallableList()
        self.on_outfit_generated = CallableList()
        self._set_current_outfit_without_distribution((OutfitCategory.EVERYDAY, 0))
        self._previous_outfit = (OutfitCategory.EVERYDAY, 0)
        self._preload_outfit_list = []
        self.on_preload_outfits_changed = CallableList()
        self.appearance_tracker = AppearanceTracker(self)
        self.visible_to_client = False

    @property
    def id(self):
        return self.sim_id

    @id.setter
    def id(self, value):
        pass

    @property
    def base(self):
        return self._base

    @property
    def occult_tracker(self):
        pass

    def ref(self, callback=None):
        return weakref.ref(self, protected_callback(callback))

    def get_create_op(self, *args, **kwargs):
        additional_ops = self.get_additional_create_ops()
        if self.first_name_key != 0:
            if not self.first_name:
                op = distributor.ops.SetFirstNameKey(self.first_name_key)
                additional_ops.append(op)
        if self.last_name_key != 0:
            if not self.last_name:
                op = distributor.ops.SetLastNameKey(self.last_name_key)
                additional_ops.append(op)
        return (distributor.ops.SimInfoCreate)(self, *args, additional_ops=additional_ops, **kwargs)

    def get_additional_create_ops(self):
        return EMPTY_SET

    def get_delete_op(self):
        return distributor.ops.SimInfoDelete()

    def get_create_after_objs(self):
        return ()

    @property
    def valid_for_distribution(self):
        return self.manager is not None and self.id is not None

    @property
    def icon_info(self):
        return (self.id, self.manager.id)

    @staticmethod
    def copy_base_attributes(sim_info_a, sim_info_b):
        sim_info_a.age = sim_info_b.age
        sim_info_a.gender = sim_info_b.gender
        sim_info_a.extended_species = sim_info_b.extended_species

    @staticmethod
    def copy_physical_attributes(sim_info_a, sim_info_b):
        sim_info_a.physique = sim_info_b.physique
        sim_info_a.facial_attributes = sim_info_b.facial_attributes
        sim_info_a.voice_pitch = sim_info_b.voice_pitch
        sim_info_a.voice_actor = sim_info_b.voice_actor
        sim_info_a.voice_effect = sim_info_b.voice_effect
        sim_info_a.skin_tone = sim_info_b.skin_tone
        sim_info_a.skin_tone_val_shift = sim_info_b.skin_tone_val_shift
        sim_info_a.flags = sim_info_b.flags
        if hasattr(sim_info_a, 'pelt_layers'):
            if hasattr(sim_info_b, 'pelt_layers'):
                sim_info_a.pelt_layers = sim_info_b.pelt_layers
        if hasattr(sim_info_a, 'base_trait_ids'):
            if hasattr(sim_info_b, 'base_trait_ids'):
                sim_info_a.base_trait_ids = list(sim_info_b.base_trait_ids)
        SimInfoBaseWrapper.copy_genetic_data(sim_info_a, sim_info_b)

    @staticmethod
    def copy_genetic_data(sim_info_a, sim_info_b):
        genetic_data_b = sim_info_b.genetic_data
        if hasattr(genetic_data_b, 'SerializeToString'):
            genetic_data_b = genetic_data_b.SerializeToString()
        elif hasattr(sim_info_a.genetic_data, 'MergeFromString'):
            sim_info_a.genetic_data.MergeFromString(genetic_data_b)
        else:
            sim_info_a.genetic_data = genetic_data_b

    def get_icon_info_data(self):
        return IconInfoData(obj_instance=self)

    def get_icon_override(self):
        pass

    def populate_icon_canvas_texture_info(self, _):
        pass

    def populate_localization_token(self, token):
        token.type = LocalizedStringToken.SIM
        token.first_name = self.first_name
        token.last_name = self.last_name
        token.full_name_key = self.full_name_key
        token.is_female = self.is_female
        token.packed_pronouns = self.packed_pronouns

    def save_sim_info(self, sim_info_msg):
        sim_info_msg.gender = self.gender
        sim_info_msg.age = self.age
        sim_info_msg.extended_species = self.extended_species
        sim_info_msg.physique = self.physique
        sim_info_msg.facial_attributes = self.facial_attributes
        sim_info_msg.skin_tone = self.skin_tone
        sim_info_msg.skin_tone_val_shift = self.skin_tone_val_shift
        sim_info_msg.outfits = self.save_outfits()
        current_outfit_type, current_outfit_index = self.get_current_outfit()
        sim_info_msg.current_outfit_type = current_outfit_type
        sim_info_msg.current_outfit_index = current_outfit_index
        previous_outfit_type, previous_outfit_index = self.get_previous_outfit()
        sim_info_msg.previous_outfit_type = previous_outfit_type
        sim_info_msg.previous_outfit_index = previous_outfit_index

    def load_sim_info(self, sim_info_msg):
        self.gender = sim_info_msg.gender
        self.age = sim_info_msg.age
        self.extended_species = sim_info_msg.extended_species
        self.physique = sim_info_msg.physique
        self.facial_attributes = sim_info_msg.facial_attributes
        self.skin_tone = sim_info_msg.skin_tone
        self.skin_tone_val_shift = sim_info_msg.skin_tone_val_shift
        self.load_outfits(sim_info_msg.outfits)
        self.set_current_outfit((sim_info_msg.current_outfit_type, sim_info_msg.current_outfit_index))
        self._previous_outfit = (sim_info_msg.previous_outfit_type, sim_info_msg.previous_outfit_index)

    def get_traits(self):
        return ()

    def set_trait_ids_on_base(self, trait_ids_override=None):
        trait_ids = trait_ids_override if trait_ids_override is not None else self.trait_ids
        self._base.base_trait_ids = trait_ids

    def update_gender_for_traits(self, gender_override=None, trait_ids_override=None):
        gender = gender_override if gender_override is not None else self.gender
        trait_ids = trait_ids_override if trait_ids_override is not None else self.trait_ids
        self._base.update_gender_for_traits(gender, trait_ids)

    def get_sim_instance(self, *args, **kwargs):
        pass

    def _get_trait_ids(self):
        return list(self._base.base_trait_ids)

    @distributor.fields.Field(op=(distributor.ops.SetTraits), priority=(distributor.fields.Field.Priority.LOW))
    def trait_ids(self):
        return self._get_trait_ids()

    def resend_trait_ids(self, traits_to_add=None, traits_to_remove=None):
        if not self.valid_for_distribution:
            return
        all_traits = None
        if traits_to_add is None:
            if traits_to_remove is None:
                all_traits = self._get_trait_ids()
        op = distributor.ops.SetTraits(all_traits, traits_to_add, traits_to_remove)
        Distributor.instance().add_op(self, op)

    @property
    def base_trait_ids(self):
        return self._base.base_trait_ids

    @base_trait_ids.setter
    def base_trait_ids(self, value):
        self._base.base_trait_ids = value
        self.resend_trait_ids()

    def resend_physical_attributes(self):
        self.resend_skin_tone()
        self.resend_skin_tone_val_shift()
        self.resend_pelt_layers()
        self.resend_custom_texture()
        self.resend_facial_attributes()
        self.resend_physique()
        self.resend_outfits()
        self.resend_voice_pitch()
        self.resend_voice_actor()
        self.resend_voice_effect()
        self.resend_trait_ids()

    def load_from_resource(self, resource_key, age=None, resend_physical_attributes=True):
        success = self._base.load_from_resource(resource_key, age)
        if not success:
            return
        if resend_physical_attributes:
            self.resend_physical_attributes()

    def apply_genetics(self, parent_a, parent_b, **kwargs):
        generate_offspring((parent_a._base), (parent_b._base), (self._base), **kwargs)

    def add_random_variation_to_modifiers(self, variation_scale=None, resend_physical_attributes=True):
        if variation_scale is None:
            variation_scale = random.uniform(-1, 1)
        else:
            return self._base.add_random_variation_to_modifiers(variation_scale) or None
        if resend_physical_attributes:
            self.resend_physical_attributes()

    def generate_club_outfit(self, tag_list=[], outfit_category_and_index=(0, 0), single_or_all_random=0):
        cas_parts = self._base.generate_club_outfit(tag_list, int(outfit_category_and_index[0]), outfit_category_and_index[1], int(OutfitCategory.SPECIAL), 0, single_or_all_random)
        return (cas_parts[0], cas_parts[1])

    def generate_outfit(self, outfit_category, outfit_index=0, tag_list=(), filter_flag=DEFAULT, body_type_flags=DEFAULT, **kwargs):
        filter_flag = OutfitFilterFlag.USE_EXISTING_IF_APPROPRIATE if filter_flag is DEFAULT else filter_flag
        body_type_flags = BodyTypeFlag.CLOTHING_ALL if body_type_flags is DEFAULT else body_type_flags
        body_type_flags_high = body_type_flags >> 64
        if not (self._base.generate_outfit)(outfit_category, outfit_index, tag_list, filter_flag=filter_flag, body_type_flags=body_type_flags, body_type_flags_high=body_type_flags_high, **kwargs):
            return False
        self.on_outfit_generated(outfit_category, outfit_index)
        self.resend_outfits()
        self.set_outfit_dirty(outfit_category)
        return True

    def generate_merged_outfit(self, source_sim_info, destination_outfit, template_outfit, source_outfit, preserve_outfit_flags=False, from_reconcile_mannequin=False):
        if preserve_outfit_flags:
            source_outfit_data = (source_sim_info.get_outfit)(*source_outfit)
        generate_merged_outfit(self._base, source_sim_info._base, destination_outfit[0], destination_outfit[1], template_outfit[0], template_outfit[1], source_outfit[0], source_outfit[1])
        if preserve_outfit_flags:
            if source_outfit_data is not None:
                self.set_outfit_flags(destination_outfit[0], destination_outfit[1], source_outfit_data.outfit_flags)
        self.on_outfit_generated((destination_outfit[0]), (destination_outfit[1]), from_reconcile_mannequin=from_reconcile_mannequin)
        self.resend_outfits()

    @contextmanager
    def set_temporary_outfit_flags(self, outfit_category, outfit_index, outfit_flags):
        if outfit_flags != DEFAULT:
            outfit_data = self.get_outfit(outfit_category, outfit_index)
            if outfit_data is not None:
                restore_flags = outfit_data.outfit_flags
            self.set_outfit_flags(outfit_category, outfit_index, outfit_flags)
        try:
            yield
        finally:
            if outfit_flags != DEFAULT:
                if outfit_data is not None:
                    self.set_outfit_flags(outfit_category, outfit_index, restore_flags)

    @contextmanager
    def set_temporary_outfit_flags_on_all_outfits(self, outfit_flags):
        with ExitStack() as (stack):
            for outfit_category, outfit_index in self.get_all_outfit_entries():
                stack.enter_context(self.set_temporary_outfit_flags(outfit_category, outfit_index, outfit_flags))

            yield

    def generate_merged_outfits_for_category(self, source_sim_info, outfit_category, outfit_flags=DEFAULT, fallback_outfit_category=OutfitCategory.EVERYDAY, **kwargs):
        current_outfit = self.get_current_outfit()
        for outfit_index, _ in enumerate(source_sim_info.get_outfits_in_category(outfit_category)):
            merged_outfit = (
             outfit_category, outfit_index)
            if self.has_outfit(merged_outfit):
                template_outfit = merged_outfit
            else:
                if self.has_outfit((outfit_category, 0)):
                    template_outfit = (
                     outfit_category, 0)
                else:
                    template_outfit = current_outfit
            with source_sim_info.set_temporary_outfit_flags(outfit_category, outfit_index, outfit_flags):
                (self.generate_merged_outfit)(source_sim_info, merged_outfit, template_outfit, merged_outfit, **kwargs)

        while len(self.get_outfits_in_category(outfit_category)) > len(source_sim_info.get_outfits_in_category(outfit_category)):
            self.remove_outfit(outfit_category)

        if self.has_outfit(current_outfit):
            self.set_current_outfit(current_outfit)
        else:
            if self.has_outfit((outfit_category, 0)):
                self.set_current_outfit((outfit_category, 0))
            else:
                if self.has_outfit((fallback_outfit_category, 0)):
                    self.set_current_outfit((fallback_outfit_category, 0))
                else:
                    if self.has_outfit((OutfitCategory.BATHING, 0)):
                        self.set_current_outfit((OutfitCategory.BATHING, 0))

    def is_duplicate_outfit(self, source_sim_info, template_outfit, source_outfit):
        return is_duplicate_merged_outfit(self._base, source_sim_info._base, template_outfit[0], template_outfit[1], source_outfit[0], source_outfit[1])

    def is_generated_outfit_duplicate_in_category(self, source_sim_info, source_outfit):
        return any((is_duplicate_merged_outfit(self._base, source_sim_info._base, source_outfit[0], outfit_index, source_outfit[0], source_outfit[1]) for outfit_index in range(len(self.get_outfits_in_category(source_outfit[0])))))

    def get_outfits(self):
        return self

    @distributor.fields.Field(op=(distributor.ops.SetSimOutfits))
    def _client_outfits(self):
        override = self.appearance_tracker.appearance_override_sim_info
        if override is not None:
            return override
        return self

    resend_outfits = _client_outfits.get_resend()

    @distributor.fields.Field(op=(distributor.ops.PreloadSimOutfit))
    def preload_outfit_list(self):
        return tuple(self._preload_outfit_list)

    resend_preload_outfit_list = preload_outfit_list.get_resend()

    def add_preload_outfit(self, outfit):
        self._preload_outfit_list.append(outfit)
        self.resend_preload_outfit_list()
        self.on_preload_outfits_changed()

    def set_preload_outfits(self, outfit_list):
        self._preload_outfit_list = list(outfit_list)
        self.resend_preload_outfit_list()
        self.on_preload_outfits_changed()

    @distributor.fields.Field(op=(distributor.ops.ChangeSimOutfit), priority=(distributor.fields.Field.Priority.LOW))
    def _current_outfit(self):
        return self._base.outfit_type_and_index

    resend_current_outfit = _current_outfit.get_resend()

    @_current_outfit.setter
    def _current_outfit(self, value):
        self._set_current_outfit_without_distribution(value)

    def _set_current_outfit_without_distribution(self, value):
        self._base.outfit_type_and_index = value
        self.on_outfit_changed(self, value)

    def get_current_outfit(self):
        return self._current_outfit

    def get_previous_outfit(self):
        return self._previous_outfit

    def set_current_outfit(self, outfit_category_and_index) -> bool:
        if self._current_outfit == outfit_category_and_index:
            if not self.outfit_is_dirty(self._current_outfit[0]):
                return False
        if not self.has_outfit(outfit_category_and_index):
            outfit_category_and_index = (self.occult_tracker.get_fallback_outfit_category(self.current_occult_types), 0)
            logger.warn('Trying to set outfit to a possible occult sim.', owner='amohananey')
        if not self.has_outfit(outfit_category_and_index):
            error_msg = 'Trying to set outfit on Sim missing it. Sim: {}, Category: {}, Index: {}, {}'
            error_args = [self, outfit_category_and_index[0], outfit_category_and_index[1], StackVar(('interaction', ))]
            career_tracker = getattr(self, 'career_tracker', None)
            if career_tracker is None:
                error_msg += '\n\tNo career tracker'
            else:
                error_msg += '\n\tCareers:'
                for career in career_tracker.careers.values():
                    error_msg += '\n\t\t{}: {}'
                    error_args.append(str(career))
                    error_args.append(str(career.current_level_tuning))

            (logger.callstack)(error_msg, *error_args, **{'level':sims4.log.LEVEL_ERROR,  'owner':'tingyul'})
        self.set_previous_outfit(new_outfit=outfit_category_and_index)
        self._current_outfit = outfit_category_and_index
        self.clear_outfit_dirty(self._current_outfit[0])
        return True

    def set_current_outfit_for_category(self, outfit_category):
        number_of_outfits = self.get_number_of_outfits_in_category(outfit_category)
        outfit_index = random.randrange(number_of_outfits)
        self.set_current_outfit((outfit_category, outfit_index))

    def set_previous_outfit(self, new_outfit, force=False):
        if force:
            self._previous_outfit = new_outfit
            return
        if new_outfit == self._current_outfit:
            return
        self._previous_outfit = self._current_outfit

    def register_for_outfit_changed_callback(self, callback):
        if callback not in self.on_outfit_changed:
            self.on_outfit_changed.append(callback)

    def unregister_for_outfit_changed_callback(self, callback):
        if callback in self.on_outfit_changed:
            self.on_outfit_changed.remove(callback)

    @property
    def is_male(self):
        return Gender(self._base.gender) == Gender.MALE

    @property
    def is_female(self):
        return Gender(self._base.gender) == Gender.FEMALE

    @distributor.fields.Field(op=(distributor.ops.SetFirstName), default='')
    def first_name(self):
        return self._base.first_name

    @first_name.setter
    def first_name(self, value):
        if self._base.first_name != value:
            self._base.first_name = value

    @distributor.fields.Field(op=(distributor.ops.SetLastName), default='')
    def last_name(self):
        return self._base.last_name

    @last_name.setter
    def last_name(self, value):
        if self._base.last_name != value:
            self._base.last_name = value

    @property
    def first_name_key(self):
        return self._base.first_name_key

    @first_name_key.setter
    def first_name_key(self, value):
        if self._base.first_name_key != value:
            self._base.first_name_key = value

    @property
    def last_name_key(self):
        return self._base.last_name_key

    @last_name_key.setter
    def last_name_key(self, value):
        if self._base.last_name_key != value:
            self._base.last_name_key = value

    @distributor.fields.Field(op=(distributor.ops.SetFullNameKey))
    def full_name_key(self):
        return self._base.full_name_key

    @full_name_key.setter
    def full_name_key(self, value):
        if self._base.full_name_key != value:
            self._base.full_name_key = value

    @distributor.fields.Field(op=(distributor.ops.SetBreedName))
    def breed_name(self):
        return self._base.breed_name

    @breed_name.setter
    def breed_name(self, value):
        if self._base.breed_name != value:
            self._base.breed_name = value

    @distributor.fields.Field(op=(distributor.ops.SetBreedNameKey))
    def breed_name_key(self):
        return self._base.breed_name_key

    @breed_name_key.setter
    def breed_name_key(self, value):
        if self._base.breed_name_key != value:
            self._base.breed_name_key = value

    @property
    def full_name(self):
        return ''

    @distributor.fields.Field(op=(distributor.ops.SetGender), priority=(distributor.fields.Field.Priority.HIGH))
    def gender(self):
        return Gender(self._base.gender)

    @gender.setter
    def gender(self, value):
        self._base.gender = Gender(value)
        self.on_base_characteristic_changed()

    @distributor.fields.Field(op=(distributor.ops.SetAge), priority=(distributor.fields.Field.Priority.HIGH))
    def age(self):
        return Age(self._base.age)

    @age.setter
    def age(self, value):
        self._base.age = value

    resend_age = age.get_resend()

    def apply_age(self, age):
        self._base.update_for_age(age)
        self.age = age
        self.resend_physical_attributes()

    @property
    def species(self):
        return self._species

    @species.setter
    def species(self, value):
        self.extended_species = value

    @distributor.fields.Field(op=(distributor.ops.SetSpecies), priority=(distributor.fields.Field.Priority.HIGH))
    def extended_species(self):
        return self._base.species

    @extended_species.setter
    def extended_species(self, value):
        self._base.species = value
        self._species = SpeciesExtended.get_species(value)
        self.on_base_characteristic_changed()

    resend_extended_species = extended_species.get_resend()

    @property
    def is_human(self):
        return self.species == Species.HUMAN

    @property
    def is_pet(self):
        return self.species != Species.HUMAN and self.species != Species.FOX

    @property
    def is_baby(self):
        return self.age == Age.BABY

    @property
    def is_toddler(self):
        return self.age == Age.TODDLER

    @property
    def rig_key(self):
        return self._base.rig_key

    @distributor.fields.Field(op=(distributor.ops.SetSkinTone), priority=(distributor.fields.Field.Priority.HIGH))
    def skin_tone(self):
        override = self.appearance_tracker.appearance_override_sim_info
        if override is not None:
            return override._base.skin_tone
        return self._base.skin_tone

    _resend_skin_tone = skin_tone.get_resend()

    def resend_skin_tone(self, *args, **kwargs):
        (self._resend_skin_tone)(*args, **kwargs)
        if self.is_baby:
            (self.resend_baby_skin_tone)(*args, **kwargs)

    @skin_tone.setter
    def skin_tone(self, value):
        self._base.skin_tone = value
        if self.is_baby:
            self.resend_baby_skin_tone()

    @distributor.fields.Field(op=(distributor.ops.SetSkinToneValShift), priority=(distributor.fields.Field.Priority.HIGH))
    def skin_tone_val_shift(self):
        override = self.appearance_tracker.appearance_override_sim_info
        if override is not None:
            return override._base.skin_tone_val_shift
        return self._base.skin_tone_val_shift

    _resend_skin_tone_val_shift = skin_tone_val_shift.get_resend()

    def resend_skin_tone_val_shift(self, *args, **kwargs):
        (self._resend_skin_tone_val_shift)(*args, **kwargs)

    @skin_tone_val_shift.setter
    def skin_tone_val_shift(self, value):
        self._base.skin_tone_val_shift = value

    @distributor.fields.Field(op=(distributor.ops.SetBabySkinTone))
    def baby_skin_tone(self):
        return BabyTuning.get_baby_skin_tone_info(self)

    resend_baby_skin_tone = baby_skin_tone.get_resend()

    @distributor.fields.Field(op=(distributor.ops.SetPeltLayers))
    def pelt_layers(self):
        return self._base.pelt_layers

    resend_pelt_layers = pelt_layers.get_resend()

    @pelt_layers.setter
    def pelt_layers(self, value):
        self._base.pelt_layers = value

    @distributor.fields.Field(op=(distributor.ops.SetCustomTexture))
    def custom_texture(self):
        return self._base.custom_texture

    resend_custom_texture = custom_texture.get_resend()

    @custom_texture.setter
    def custom_texture(self, value):
        self._base.custom_texture = value

    @distributor.fields.Field(op=(distributor.ops.SetVoicePitch))
    def voice_pitch(self):
        return self._base.voice_pitch

    resend_voice_pitch = voice_pitch.get_resend()

    @voice_pitch.setter
    def voice_pitch(self, value):
        self._base.voice_pitch = value

    @distributor.fields.Field(op=(distributor.ops.SetVoiceActor))
    def voice_actor(self):
        return self._base.voice_actor

    resend_voice_actor = voice_actor.get_resend()

    @voice_actor.setter
    def voice_actor(self, value):
        self._base.voice_actor = value

    @distributor.fields.Field(op=(distributor.ops.SetVoiceEffect))
    def voice_effect(self):
        return self._base.voice_effect

    @voice_effect.setter
    def voice_effect(self, value):
        if value is None:
            value = 0
        self._base.voice_effect = value

    resend_voice_effect = voice_effect.get_resend()

    @distributor.fields.Field(op=(distributor.ops.SetPhysique))
    def physique(self):
        return self._base.physique

    resend_physique = physique.get_resend()

    @physique.setter
    def physique(self, value):
        self._base.physique = value

    @distributor.fields.Field(op=(distributor.ops.SetFacialAttributes))
    def facial_attributes(self):
        return self._base.facial_attributes

    @facial_attributes.setter
    def facial_attributes(self, value):
        self._base.facial_attributes = value

    resend_facial_attributes = facial_attributes.get_resend()

    @distributor.fields.Field(op=(distributor.ops.SetGeneticData))
    def genetic_data(self):
        return self._base.genetic_data

    @genetic_data.setter
    def genetic_data(self, value):
        self._base.genetic_data = value

    resend_genetic_data = genetic_data.get_resend()

    @property
    def flags(self):
        return self._base.flags

    @flags.setter
    def flags(self, value):
        self._base.flags = value

    @property
    def packed_pronouns(self):
        return self._base.packed_pronouns

    @packed_pronouns.setter
    def packed_pronouns(self, value):
        if self._base.packed_pronouns != value:
            self._base.packed_pronouns = value