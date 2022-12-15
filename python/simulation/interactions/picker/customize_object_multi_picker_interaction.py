# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\picker\customize_object_multi_picker_interaction.py
# Compiled at: 2020-06-22 22:47:39
# Size of source mod 2**32: 3577 bytes
import sims4
from interactions.base.multi_picker_interaction import MultiPickerInteraction
from objects.placement.placement_helper import PlacementHelper
from objects.system import create_object
from sims4.tuning.tunable_base import GroupNames
from ui.ui_dialog_multi_picker import UiCustomizeObjectMultiPicker
logger = sims4.log.Logger('CustomizeObjectMultiPicker', default_owner='yozhang')

class CustomizeObjectMultiPickerInteraction(MultiPickerInteraction):
    INSTANCE_TUNABLES = {'picker_dialog':UiCustomizeObjectMultiPicker.TunableFactory(description='\n            Tuning for the ui customize object multi picker. \n            ',
       tuning_group=GroupNames.PICKERTUNING), 
     'placement':PlacementHelper.TunableFactory(description='\n            Use this placement strategy when object is created, if placement fails, use sim inventory\n            and household inventory as fallback.\n            ',
       tuning_group=GroupNames.PICKERTUNING)}

    @classmethod
    def _verify_tuning_callback(cls):
        from ui.ui_dialog_picker import UiDropdownPicker
        for picker_data in cls.picker_dialog.pickers:
            if picker_data.picker_interaction.picker_dialog.factory is not UiDropdownPicker:
                logger.error('"pickers" tuning should only contain dropdown picker.\n{}', cls)

    def _on_picker_selected(self, dialog):
        obj = self._create_customize_object(dialog.customized_obj_info)
        if obj is not None:
            self.picked_item_ids = {
             obj.id}
        super()._on_picker_selected(dialog)

    def _create_customize_object(self, customized_obj_info):
        if customized_obj_info is None:
            return
        obj_def, geo_state, mat_state, obj_name = customized_obj_info
        obj = create_object(obj_def)
        if obj is None:
            logger.error('CustomizeObjectMultiPickerInteraction: Failed to create object {}', obj_def)
            return
        obj.update_ownership(self.sim.sim_info)
        if obj.state_component is not None:
            if geo_state:
                obj.set_state(geo_state.state, geo_state)
            if mat_state:
                obj.set_state(mat_state.state, mat_state)
        if obj_name is not None:
            obj.set_custom_name(obj_name)
        resolver = self.get_resolver()
        if not self.placement.try_place_object(obj, resolver):
            logger.error('Failed placing the customized object: {}', obj)
            obj.destroy(source=self, cause='Failed placing the customized object')
            return
        return obj