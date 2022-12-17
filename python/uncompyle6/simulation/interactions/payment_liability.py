# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\payment_liability.py
# Compiled at: 2018-09-21 15:30:55
# Size of source mod 2**32: 576 bytes
from interactions.liability import Liability

class PaymentLiability(Liability):
    LIABILITY_TOKEN = 'PaymentLiability'

    def __init__(self, amount, payment_destinations, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.amount = amount
        self.payment_destinations = payment_destinations