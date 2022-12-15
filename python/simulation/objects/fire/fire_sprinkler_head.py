# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\fire\fire_sprinkler_head.py
# Compiled at: 2014-06-24 13:04:34
# Size of source mod 2**32: 511 bytes
import objects.game_object

class FireSprinklerHead(objects.game_object.GameObject):

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.vfx = None

    def on_remove(self):
        if self.vfx is not None:
            self.vfx.stop()
        super().on_remove()