# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\utils\notification.py
# Compiled at: 2014-12-05 12:36:12
# Size of source mod 2**32: 3286 bytes
from interactions import ParticipantType
from interactions.utils.interaction_elements import XevtTriggeredElement
from interactions.utils.tested_variant import TunableTestedVariant
from sims4.tuning.tunable import TunableEnumEntry, Tunable
from singletons import DEFAULT
from ui.ui_dialog_notification import TunableUiDialogNotificationSnippet
import services

class NotificationElement(XevtTriggeredElement):
    FACTORY_TUNABLES = {'description':"Show a notification to a Sim's player.", 
     'recipient_subject':TunableEnumEntry(description="\n            The Sim's whose player will be the recipient of this notification.\n            ",
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'limit_to_one_notification':Tunable(description='\n            If checked, this notification will only be displayed for the first\n            recipient subject. This is useful to prevent duplicates of the\n            notification from showing up when sending a notification to\n            LotOnwers or other Participant Types that have multiple Sims.\n            ',
       tunable_type=bool,
       default=False), 
     'dialog':TunableTestedVariant(tunable_type=TunableUiDialogNotificationSnippet()), 
     'allow_autonomous':Tunable(description='\n            If checked, then this notification will be displayed even if its\n            owning interaction was initiated by autonomy. If unchecked, then the\n            notification is suppressed if the interaction is autonomous.\n            ',
       tunable_type=bool,
       default=True)}

    def _do_behavior(self, *args, **kwargs):
        return (self.show_notification)(*args, **kwargs)

    def show_notification(self, recipients=DEFAULT, **kwargs):
        if not self.allow_autonomous:
            if self.interaction.is_autonomous:
                return
        if recipients is DEFAULT:
            if self.recipient_subject == ParticipantType.ActiveHousehold:
                recipients = (
                 services.active_sim_info(),)
            else:
                recipients = self.interaction.get_participants(self.recipient_subject)
        simless = self.interaction.simless
        for recipient in recipients:
            if not simless:
                if recipient.is_selectable:
                    pass
            resolver = self.interaction.get_resolver()
            dialog = self.dialog(recipient, resolver=resolver)
            if dialog is not None:
                (dialog.show_dialog)(**kwargs)
                if self.limit_to_one_notification:
                    break