# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\payment\payment_info.py
# Compiled at: 2016-06-09 14:53:47
# Size of source mod 2**32: 858 bytes
import enum

class PaymentInfo:

    def __init__(self, amount, resolver):
        self.amount = amount
        self.resolver = resolver


class BusinessPaymentInfo(PaymentInfo):

    def __init__(self, *args, revenue_type, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.revenue_type = revenue_type


class PaymentBusinessRevenueType(enum.Int):
    ITEM_SOLD = 0
    SEED_MONEY = 1