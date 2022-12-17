# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\university\university_scholarship_enums.py
# Compiled at: 2019-08-20 18:43:41
# Size of source mod 2**32: 313 bytes
import enum

class ScholarshipStatus(enum.Int):
    ACTIVE = 0
    PENDING = 1
    ACCEPTED = 2
    REJECTED = 3