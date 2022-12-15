# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\shared_commands\unittestcmd.py
# Compiled at: 2013-05-08 22:53:35
# Size of source mod 2**32: 1521 bytes
from sims4.commands import Command

class ConsoleOutput:
    try:

        def write(self, message):
            import sims4.log
            text = message.strip('\n')
            if text:
                sims4.log.info('Console', text)

    except:

        def write(self, message):
            text = message.strip('\n')
            print(text)


@Command('test.module')
def run_module_test(module, verbose: bool=False, _connection=None):
    import sims4.testing.unit
    sims4.testing.unit.test_module_by_name(module, (set()), verbose=(bool(verbose)), file_=(ConsoleOutput()))


@Command('test.path')
def run_path_test(filename, verbose: bool=False, _connection=None):
    import sims4.testing.unit
    sims4.testing.unit.test_path(filename, (set()), verbose=(bool(verbose)), file_=(ConsoleOutput()))