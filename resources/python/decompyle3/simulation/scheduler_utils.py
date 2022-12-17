# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\scheduler_utils.py
# Compiled at: 2019-09-11 11:40:52
# Size of source mod 2**32: 1308 bytes
from sims4.tuning.tunable import TunableSingletonFactory, Tunable
from tunable_time import Days

def convert_string_to_enum(**day_availability_mapping):
    day_availability_dict = {}
    for day in Days:
        name = '{} {}'.format(int(day), day.name)
        available = day_availability_mapping[name]
        day_availability_dict[day] = available

    return day_availability_dict


class TunableAvailableDays(TunableSingletonFactory):
    FACTORY_TYPE = staticmethod(convert_string_to_enum)


def TunableDayAvailability():
    day_availability_mapping = {}
    for day in Days:
        name = '{} {}'.format(int(day), day.name)
        day_availability_mapping[name] = Tunable(bool, False)

    day_availability = TunableAvailableDays(description='Which days of the week to include', **day_availability_mapping)
    return day_availability