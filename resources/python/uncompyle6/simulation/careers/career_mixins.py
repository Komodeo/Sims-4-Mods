# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\careers\career_mixins.py
# Compiled at: 2019-10-15 16:55:43
# Size of source mod 2**32: 972 bytes
from sims4.utils import flexmethod

class CareerKnowledgeMixin:

    @flexmethod
    def show_knowledge_notification(cls, inst, sim_info, resolver):
        inst_or_cls = inst if inst is not None else cls
        if inst_or_cls.current_track_tuning.knowledge_notification:
            notification = inst_or_cls.current_track_tuning.knowledge_notification(sim_info, resolver=resolver)
            notification.show_dialog(additional_tokens=(inst_or_cls.get_career_text_tokens()))