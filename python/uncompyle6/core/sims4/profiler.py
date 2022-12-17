# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\sims4\profiler.py
# Compiled at: 2014-06-12 14:56:15
# Size of source mod 2**32: 2818 bytes
import sims4.log
from contextlib import contextmanager
logger = sims4.log.Logger('Profiler')
if __profile__:
    import _profiler
    begin_scope = _profiler.begin_scope
    end_scope = _profiler.end_scope
    enable_profiler = _profiler.begin
    disable_profiler = _profiler.end
    flush = _profiler.flush
else:

    def enable_profiler(*args, **kwargs):
        logger.error('__profile__ is not set. Did you forget to pass in the command line argument?')


    def disable_profiler(*args, **kwargs):
        pass


    def begin_scope(*args, **kwargs):
        logger.error('__profile__ is not set. Did you forget to pass in the command line argument?')


    def begin_scope(*args, **kwargs):
        logger.error('__profile__ is not set. Did you forget to pass in the command line argument?')


@contextmanager
def scope(name):
    if __profile__:
        sims4.profiler.begin_scope(name)
    try:
        yield
    finally:
        if __profile__:
            sims4.profiler.end_scope()