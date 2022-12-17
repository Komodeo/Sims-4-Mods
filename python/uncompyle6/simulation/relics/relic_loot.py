# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\relics\relic_loot.py
# Compiled at: 2017-11-03 12:34:38
# Size of source mod 2**32: 1102 bytes
from interactions.utils.loot_basic_op import BaseLootOperation
from relics.relic_tuning import RelicComboId
from sims4.tuning.tunable import TunableEnumEntry

class AddRelicCombo(BaseLootOperation):
    FACTORY_TUNABLES = {'relic_combo_id': TunableEnumEntry(description="\n            The relic combo ID to add to the Sim's Relic Tracker.\n            ",
                         tunable_type=RelicComboId,
                         default=(RelicComboId.INVALID),
                         invalid_enums=(
                        RelicComboId.INVALID,))}

    def __init__(self, *args, relic_combo_id, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._relic_combo_id = relic_combo_id

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if subject is None:
            return
        relic_tracker = subject.relic_tracker
        relic_tracker.add_relic_combo(self._relic_combo_id)