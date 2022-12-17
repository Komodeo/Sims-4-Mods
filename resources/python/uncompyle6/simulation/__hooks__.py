# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\__hooks__.py
# Compiled at: 2019-02-21 18:35:20
# Size of source mod 2**32: 1365 bytes
RELOADER_ENABLED = False
__enable_gc_callback = True
import gc
try:
    import _profile
except:
    __enable_gc_callback = False

def system_init(gameplay):
    import sims4.importer
    sims4.importer.enable()
    print('Server Startup')
    if __enable_gc_callback:
        gc.callbacks.append(_profile.notify_gc_function)


def system_shutdown():
    global RELOADER_ENABLED
    import sims4.importer
    sims4.importer.disable()
    RELOADER_ENABLED = False