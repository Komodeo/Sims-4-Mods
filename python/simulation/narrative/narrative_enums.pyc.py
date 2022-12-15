# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\narrative\narrative_enums.py
# Compiled at: 2020-05-20 10:18:13
# Size of source mod 2**32: 2115 bytes
from sims4.tuning.dynamic_enum import DynamicEnum, DynamicEnumLocked
from weather.weather_enums import WeatherEffectType, CloudType
import enum

class NarrativeGroup(DynamicEnum, partitioned=True):
    INVALID = 0


class NarrativeEvent(DynamicEnum, partitioned=True):
    INVALID = 0


class NarrativeProgressionEvent(DynamicEnumLocked, partitioned=True):
    INVALID = 0


class NarrativeSituationShiftType(DynamicEnum, partitioned=True):
    INVALID = 0


class NarrativeEnvironmentParams(enum.Int):
    StrangerVille_Act = WeatherEffectType.STRANGERVILLE_ACT
    BatuuFactionState_RES = WeatherEffectType.STARWARS_RESISTANCE
    BatuuFactionState_FO = WeatherEffectType.STARWARS_FIRST_ORDER
    StrangerVille_Strange_Skybox = CloudType.STRANGE
    StrangerVille_VeryStrange_Skybox = CloudType.VERY_STRANGE