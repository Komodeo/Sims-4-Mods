# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\constraints\constraint_functions.py
# Compiled at: 2017-08-21 13:13:13
# Size of source mod 2**32: 1334 bytes
from _math import Vector2
import math
from sims4.math import TWO_PI

class ConstraintGoalGenerationFunctionBase:

    def __call__(self):
        return ()


class ConstraintGoalGenerationFunctionIdealRadius(ConstraintGoalGenerationFunctionBase):
    COUNT = 8

    def __init__(self, center, radius):
        self.center = Vector2(center.x, center.z)
        self.radius = radius

    def __call__(self):
        goals = []
        step = TWO_PI / self.COUNT
        for angle in range(self.COUNT):
            angle *= step
            x = math.cos(angle) * self.radius
            y = math.sin(angle) * self.radius
            v = Vector2(x, y)
            v += self.center
            goals.append(v)

        return tuple(goals)