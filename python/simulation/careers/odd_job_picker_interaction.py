# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\careers\odd_job_picker_interaction.py
# Compiled at: 2021-03-18 15:42:19
# Size of source mod 2**32: 2166 bytes
from drama_scheduler.drama_node_picker_interaction import DramaNodePickerInteraction
from sims4.tuning.tunable import TunableReference
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import flexmethod
from ui.ui_dialog_picker import UiOddJobPicker
import services, sims4

class OddJobPickerInteraction(DramaNodePickerInteraction):
    INSTANCE_TUNABLES = {'picker_dialog':UiOddJobPicker.TunableFactory(description='\n            The odd job picker dialog.\n            ',
       tuning_group=GroupNames.PICKERTUNING), 
     'odd_job_career':TunableReference(description='\n            The career this gig is associated with.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.CAREER),
       tuning_group=GroupNames.PICKERTUNING)}

    def _setup_dialog(self, dialog, **kwargs):
        (super()._setup_dialog)(dialog, **kwargs)
        gig_career = self.sim.career_tracker.get_career_by_uid(self.odd_job_career.guid64)
        if gig_career is not None:
            dialog.star_ranking = gig_career.level

    def on_multi_choice_selected(self, choice_tags, **kwargs):
        for choice_tag in choice_tags:
            (self.on_choice_selected)(choice_tag, **kwargs)

    def _get_current_selected_count(self):
        gig_career = self.sim.career_tracker.get_career_by_uid(self.odd_job_career.guid64)
        if gig_career is not None:
            if gig_career.current_gig_limit > 1:
                return len(gig_career.get_current_gigs())
        return super()._get_current_selected_count()