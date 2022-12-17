# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\weather\weather_tuning_mixin.py
# Compiled at: 2020-09-03 11:56:49
# Size of source mod 2**32: 2367 bytes
import enum
from seasons.seasons_enums import SeasonType
from sims4.tuning.tunable import TunableMapping, TunableEnumEntry
from weather.weather_enums import SnowBehavior
from weather.weather_forecast import TunableWeatherSeasonalForecastsReference, TunableWeatherForecastListReference

class WeatherTuningMixin:
    INSTANCE_TUNABLES = {'weather':TunableMapping(description='\n            Forecasts for this location for the various seasons\n            ',
       key_type=TunableEnumEntry(description='\n                The Season.\n                ',
       tunable_type=SeasonType,
       default=(SeasonType.SPRING)),
       value_type=TunableWeatherSeasonalForecastsReference(description='\n                The forecasts for the season by part of season\n                ',
       pack_safe=True)), 
     'weather_no_seasons':TunableWeatherForecastListReference(description='\n            Forecast(s) for this location for players without EP05 installed\n            ',
       pack_safe=True,
       allow_none=True), 
     'snow_behavior':TunableMapping(description='\n            Snow behavior for this location for the various seasons\n            Defaults to NO_SNOW if not tuned for the current season\n            If set to PERMANENT, it will also set initial water to frozen\n            and windows to frosted\n            ',
       key_type=TunableEnumEntry(description='\n                The Season.\n                ',
       tunable_type=SeasonType,
       default=(SeasonType.SPRING)),
       value_type=TunableEnumEntry(description='\n                How snow behaves during this season at this location\n                ',
       tunable_type=SnowBehavior,
       default=(SnowBehavior.NO_SNOW))), 
     'snow_behavior_no_seasons':TunableEnumEntry(description='\n            How snow behaves during this season at this location\n            ',
       tunable_type=SnowBehavior,
       default=SnowBehavior.NO_SNOW)}