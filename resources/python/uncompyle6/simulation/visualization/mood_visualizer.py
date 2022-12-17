# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\visualization\mood_visualizer.py
# Compiled at: 2018-07-10 14:45:11
# Size of source mod 2**32: 1424 bytes
from debugvis import Context
import sims4.math

def strip_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


class MoodVisualizer:

    def __init__(self, sim, layer):
        self._sim = sim.ref()
        self.layer = layer
        self.start()

    @property
    def sim(self):
        if self._sim is not None:
            return self._sim()

    def start(self):
        self.sim.Buffs.on_mood_changed.append(self._on_mood_changed)
        self._on_mood_changed()

    def stop(self):
        sim = self.sim
        if sim is not None:
            if sim.Buffs is not None:
                sim.Buffs.on_mood_changed.remove(self._on_mood_changed)

    def _on_mood_changed(self, **kwargs):
        offset = sims4.math.Vector3.Y_AXIS() * 0.4
        BONE_INDEX = 5
        mood_name = strip_prefix(self.sim.get_mood().__name__, 'Mood_')
        with Context(self.layer) as (context):
            context.add_text_object((self.sim), offset, mood_name, bone_index=BONE_INDEX)