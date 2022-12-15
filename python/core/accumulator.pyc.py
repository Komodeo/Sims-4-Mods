# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\accumulator.py
# Compiled at: 2012-10-03 19:04:24
# Size of source mod 2**32: 1468 bytes


class HarmonicMeanAccumulator:

    def __init__(self, seq=None):
        self._fault = False
        self.num_items = 0
        self.total = 0
        if seq is not None:
            for value in seq:
                if not self.fault():
                    self.add(value)

    def add(self, value):
        if value <= 0:
            self._fault = True
            return
        self.num_items += 1
        self.total += 1 / value

    def fault(self):
        return self._fault

    def value(self):
        if self._fault:
            return 0
        return self.num_items / self.total