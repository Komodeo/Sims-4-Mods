# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\transfer_painting_state.py
# Compiled at: 2019-05-09 15:25:25
# Size of source mod 2**32: 1213 bytes
from interactions.utils.loot_basic_op import BaseTargetedLootOperation
import sims4
logger = sims4.log.Logger('PaintingTransferLoot', default_owner='rrodgers')

class TransferPaintingStateLoot(BaseTargetedLootOperation):

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if subject is not None:
            if target is not None:
                source_canvas = subject.canvas_component
                if source_canvas is None:
                    logger.error('Painting State Transfer: Subject {} has no canvas_component', subject)
                    return
                target_canvas = target.canvas_component
                if target_canvas is None:
                    logger.error('Painting State Transfer: target object {} has no canvas_component', target)
                    return
                if target_canvas.painting_state != source_canvas.painting_state:
                    target_canvas.painting_state = source_canvas.painting_state