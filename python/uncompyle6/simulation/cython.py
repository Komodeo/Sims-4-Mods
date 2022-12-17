# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\cython.py
# Compiled at: 2020-02-05 19:30:39
# Size of source mod 2**32: 544 bytes
if __name__ == '__main__':
    import os, sys
    cythonpath, _ = os.path.split(os.path.realpath(__file__))
    sys.path.insert(0, cythonpath)
    from Cython.Compiler.Main import main
    main(command_line=1)
else:
    from Cython.Shadow import *
    from Cython import __version__
    from Cython import load_ipython_extension