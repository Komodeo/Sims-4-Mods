# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\ui\tested_ui_dialog_notification.py
# Compiled at: 2019-10-02 00:11:52
# Size of source mod 2**32: 1076 bytes
from event_testing.tests import TunableTestSet
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit
from snippets import define_snippet
from ui.ui_dialog_notification import UiDialogNotification

class TestedUiDialogNotification(UiDialogNotification):
    FACTORY_TUNABLES = {'tests': TunableTestSet(description='\n            The test(s) to decide whether the notification is to be shown.\n            ')}

    def show_dialog(self, **kwargs):
        if self.tests:
            test_result = self.tests.run_tests(self._resolver)
            if not test_result:
                return
            return (super().show_dialog)(**kwargs)


TunableTestedUiDialogNotificationReference, TunableTestedUiDialogNotificationSnippet = define_snippet('tested_notification', TestedUiDialogNotification.TunableFactory())