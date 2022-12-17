# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\api_config.py
# Compiled at: 2013-02-21 16:04:39
# Size of source mod 2**32: 4859 bytes
import sys, _trace
ERROR = [
 None, set()]
WARN = [None, set()]
INFO = [None, set()]

def log(level, msg, api_key):
    if level[0] is None:

        def make_logger(level):

            def logger(message):
                frame = sys._getframe(1)
                return _trace.trace(_trace.TYPE_LOG, message, 'ApiConfig', level, 0, frame)

            return logger

        ERROR[0] = make_logger(_trace.LEVEL_ERROR)
        WARN[0] = make_logger(_trace.LEVEL_WARN)
        INFO[0] = make_logger(_trace.LEVEL_INFO)
    log_fn, used_log_keys = level
    log_key = (api_key, msg)
    if log_key not in used_log_keys:
        used_log_keys.add(log_key)
        log_fn(msg.format(api_key))


GAMEPLAY_SUPPORTED_APIS = {
 'native.animation.arb.BoundaryCondition2',
 'native.animation.arb.BoundaryCondition.get_required_slots',
 'native.animation.arb_get_timing_looping_duration',
 'native.animation.arb.BoundaryConditionInfo',
 'native.animation.request_result_codes'}
_NATIVE_SUPPORTED_APIS = set()

def gameplay_supports_new_api(api_key: str) -> bool:
    if api_key in GAMEPLAY_SUPPORTED_APIS:
        log(ERROR, 'API {} is now supported in Assets and the old implementation should be removed from the native layer.', api_key)
        return True
    log(WARN, 'API {} is not yet supported in Assets.', api_key)
    return False


def register_native_support(api_key: str):
    _NATIVE_SUPPORTED_APIS.add(api_key)


def native_supports_new_api(api_key: str) -> bool:
    if api_key in _NATIVE_SUPPORTED_APIS:
        log(ERROR, 'API {} is now supported in the native layer and the old implementation should be removed from Assets.', api_key)
        return True
    log(WARN, 'API {} is not yet supported in the native layer.', api_key)
    return False