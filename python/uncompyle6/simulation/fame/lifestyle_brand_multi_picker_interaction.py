# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\fame\lifestyle_brand_multi_picker_interaction.py
# Compiled at: 2018-08-16 13:55:46
# Size of source mod 2**32: 1776 bytes
from interactions.base.multi_picker_interaction import MultiPickerInteraction
import sims4.log
logger = sims4.log.Logger('Dialog', default_owner='rfleig')
TEXT_INPUT_BRAND_NAME = 'brand_name'

class LifestyleBrandMultiPickerInteraction(MultiPickerInteraction):

    def _create_dialog(self, owner, **kwargs):
        dialog = (super()._create_dialog)(owner, **kwargs)
        dialog.add_text_listener(self._on_text_input)
        dialog.existing_text = self._existing_text()
        return dialog

    def _existing_text(self):
        sim = self.sim
        lifestyle_brand_tracker = sim.sim_info.lifestyle_brand_tracker
        if lifestyle_brand_tracker is None:
            logger.error("Sim {} doesn't have a Lifestyle Brand Tracker, how is this possible?", sim)
            return (None, None)
        return (
         TEXT_INPUT_BRAND_NAME, lifestyle_brand_tracker.brand_name)

    def _on_text_input(self, dialog, text_input_name, text_input):
        sim = self.sim
        lifestyle_brand_tracker = sim.sim_info.lifestyle_brand_tracker
        if lifestyle_brand_tracker is None:
            logger.error("Sim {} doesn't have a Lifestyle Brand Tracker, how is this possible?", sim)
            return
        lifestyle_brand_tracker.brand_name = text_input