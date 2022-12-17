# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\traits\preference_tracker_mixin.py
# Compiled at: 2021-04-07 12:49:52
# Size of source mod 2**32: 1982 bytes
from traits.preference_enums import PreferenceTypes
from traits.preference_tuning import PreferenceTuning
import services

class PreferenceTrackerMixin:

    def get_object_preferences(self, types):
        raise NotImplementedError

    def get_preferences(self, types):
        raise NotImplementedError

    @property
    def preferences(self):
        return self.get_preferences(PreferenceTypes)

    @property
    def likes(self):
        return self.get_preferences((PreferenceTypes.LIKE,))

    @property
    def dislikes(self):
        return self.get_preferences((PreferenceTypes.DISLIKE,))

    def at_preference_capacity(self):
        return len(self.preferences) >= PreferenceTuning.PREFERENCE_CAPACITY

    def get_preferences_for_subject(self, preference_types, subject):
        return [t for t in self.get_preferences(preference_types) if t.is_preference_subject(subject)]

    def get_preferences_for_subjects(self, preference_types, subjects):
        return [t for t in self.get_preferences(preference_types) if t.is_preference_subject_in_subject_set(subjects)]