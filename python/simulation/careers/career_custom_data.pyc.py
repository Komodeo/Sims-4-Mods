# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\careers\career_custom_data.py
# Compiled at: 2018-09-14 16:39:31
# Size of source mod 2**32: 2279 bytes
from careers.career_tuning import Career

class CustomCareerData:

    def __init__(self):
        self._custom_name = None
        self._custom_description = None

    def set_custom_career_data(self, custom_name=None, custom_description=None):
        self._custom_name = custom_name
        self._custom_description = custom_description

    def get_custom_career_name(self):
        return self._custom_name

    def get_custom_career_description(self):
        return self._custom_description

    def save_custom_data(self, proto_buff):
        if self._custom_name is not None:
            proto_buff.custom_career_name = self._custom_name
        if self._custom_description is not None:
            proto_buff.custom_career_description = self._custom_description

    def load_custom_data(self, proto_buff):
        if proto_buff.HasField('custom_career_name'):
            self._custom_name = proto_buff.custom_career_name
        if proto_buff.HasField('custom_career_description'):
            self._custom_description = proto_buff.custom_career_description

    def show_custom_career_knowledge_notification(self, sim_info, resolver):
        notification = Career.CUSTOM_CAREER_KNOWLEDGE_NOTIFICATION(sim_info, resolver=resolver)
        notification.show_dialog(additional_tokens=(self.get_custom_career_name(),))