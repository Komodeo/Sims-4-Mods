# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\aging\aging_translation.py
# Compiled at: 2022-07-21 18:49:30
# Size of source mod 2**32: 555 bytes


def sim_days_to_age_progress(sim_days, age_duration):
    return sim_days / age_duration


def age_progress_to_sim_days(age_progress, age_duration):
    return age_progress * age_duration