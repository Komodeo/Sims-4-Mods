# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\sims4\repr_utils.py
# Compiled at: 2014-04-07 16:31:00
# Size of source mod 2**32: 10583 bytes
from types import FrameType
import functools, sys

def _strip_source_path(path):
    for f in sys.path:
        if path.startswith(f):
            return path[len(f):].lstrip('\\/')

    return path


class suppress_quotes(str):

    def __str__(self):
        return self

    def __repr__(self):
        return self


def callable_repr(func):
    if isinstance(func, FrameType):
        code = func.f_code
    else:
        if isinstance(func, functools.partial):
            return 'partial({}, ...)'.format(callable_repr(func.func))
        code = func.__code__
    return '<{} at {}:{}>'.format(code.co_name, _strip_source_path(code.co_filename), code.co_firstlineno)


def standard_repr(obj, *args, **kwargs):
    type_str = type(obj).__name__ if (not isinstance(obj, str)) else obj
    args_str = None
    if args:
        args_str = [str(i) for i in args]
        args_str = ', '.join(args_str)
    kwargs_str = None
    if kwargs:
        kwargs_str = ['{}={}'.format(k, v) for k, v in kwargs.items()]
        kwargs_str = ', '.join(sorted(kwargs_str))
    if args_str:
        if kwargs_str:
            return '{}({}, {})'.format(type_str, args_str, kwargs_str)
    if args_str or kwargs_str:
        return '{}({})'.format(type_str, args_str or kwargs_str)
    return '{}()'.format(type_str)


def standard_auto_repr(obj, missing_value_marker='?', omit_missing_attributes=True):
    return object.__repr__(obj)


def standard_angle_repr(obj, *args, **kwargs):
    type_str = type(obj).__name__
    args_str = None
    if args:
        args_str = [str(i) for i in args]
        args_str = ' '.join(args_str)
    kwargs_str = None
    if kwargs:
        kwargs_str = ['{}={}'.format(k, v) for k, v in kwargs.items()]
        kwargs_str = ' '.join(sorted(kwargs_str))
    if args_str:
        if kwargs_str:
            return '<{}: {} {}>'.format(type_str, args_str, kwargs_str)
    if args_str or kwargs_str:
        return '<{}: {}>'.format(type_str, args_str or kwargs_str)
    return '<{} at {:#010x}>'.format(type_str, id(obj))


def standard_float_tuple_repr(*floats):
    return '(' + ', '.join(('{:0.3f}'.format(i) for i in floats)) + ')'


def standard_brief_id_repr(guid):
    return '{:#018x}'.format(guid)