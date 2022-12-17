# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\utils\apply_overlay_loot.py
# Compiled at: 2019-06-12 17:56:39
# Size of source mod 2**32: 1668 bytes
from distributor.ops import CompositeImages
from distributor.rollback import ProtocolBufferRollback
from distributor.system import Distributor
from interactions.utils.loot_basic_op import BaseTargetedLootOperation
from sims4.tuning.tunable import TunableResourceKey
import sims4

class ApplyCanvasOverlay(BaseTargetedLootOperation):
    FACTORY_TUNABLES = {'overlay_image': TunableResourceKey(description="\n            An image which will be composited with the texture of the target\n            object's canvas component. The resulting composited image will then\n            be set to be the object's new texture.\n            ",
                        resource_types=[
                       sims4.resources.Types.TGA],
                        default=None)}

    def __init__(self, overlay_image, **kwargs):
        (super().__init__)(**kwargs)
        self.overlay_image = overlay_image

    def _apply_to_subject_and_target(self, subject, target, resolver):
        canvas_texture_id = target.canvas_component.get_canvas_texture_id()
        composite_target_effect = target.canvas_component.painting_state.effect
        op = CompositeImages(canvas_texture_id, composite_target_effect, target.id)
        with ProtocolBufferRollback(op.op.additional_composite_operations) as (additional_composite_operations):
            additional_composite_operations.texture_hash = self.overlay_image.instance
        Distributor.instance().add_op_with_no_owner(op)