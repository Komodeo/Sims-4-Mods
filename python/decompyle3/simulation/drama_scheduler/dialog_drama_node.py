# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\drama_scheduler\dialog_drama_node.py
# Compiled at: 2021-11-22 18:29:05
# Size of source mod 2**32: 16660 bytes
from live_events.live_event_service import LiveEventName
from live_events.live_event_telemetry import LiveEventTelemetry
from drama_scheduler.drama_node import BaseDramaNode, CooldownOption, DramaNodeRunOutcome
from drama_scheduler.drama_node_types import DramaNodeType
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.tunable import TunableVariant, TunableList, TunableReference, HasTunableSingletonFactory, AutoFactoryInit, TunableTuple, Tunable, OptionalTunable, TunableEnumEntry
from sims4.utils import classproperty
from tunable_utils.tested_list import TunableTestedList
from ui.ui_dialog import UiDialogOk, UiDialogOkCancel, ButtonType, UiDialog, UiDialogResponse
from ui.ui_dialog_notification import UiDialogNotification
import services, sims4.resources

class _dialog_and_loot(HasTunableSingletonFactory, AutoFactoryInit):

    def on_node_run(self, drama_node):
        raise NotImplementedError


class _notification_and_loot(_dialog_and_loot):
    FACTORY_TUNABLES = {'notification':UiDialogNotification.TunableFactory(description='\n            The notification that will display to the drama node.\n            '), 
     'loot_list':TunableList(description='\n            A list of loot operations to apply when this notification is given.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       class_restrictions=('LootActions', 'RandomWeightedLoot'),
       pack_safe=True))}

    def on_node_run(self, drama_node):
        resolver = drama_node._get_resolver()
        target_sim_id = drama_node._sender_sim_info.id if drama_node._sender_sim_info is not None else None
        dialog = self.notification((drama_node._receiver_sim_info), target_sim_id=target_sim_id,
          resolver=resolver)
        dialog.show_dialog()
        for loot_action in self.loot_list:
            loot_action.apply_to_resolver(resolver)


class _dialog_ok_and_loot(_dialog_and_loot):
    FACTORY_TUNABLES = {'dialog':UiDialogOk.TunableFactory(description='\n            The dialog with an ok button that we will display to the user.\n            '), 
     'on_dialog_complete_loot_list':TunableList(description='\n            A list of loot that will be applied when the player responds to the\n            dialog or, if the dialog is a phone ring or text message, when the\n            dialog times out due to the player ignoring it for too long.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       class_restrictions=('LootActions', 'RandomWeightedLoot'),
       pack_safe=True)), 
     'on_dialog_seen_loot_list':TunableList(description='\n            A list of loot that will be applied when player responds to the\n            message.  If the dialog is a phone ring or text message then this\n            loot will not be triggered when the dialog times out due to the\n            player ignoring it for too long.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       class_restrictions=('LootActions', ),
       pack_safe=True))}

    def on_node_run(self, drama_node):
        resolver = drama_node._get_resolver()
        target_sim_id = drama_node._sender_sim_info.id if drama_node._sender_sim_info is not None else None
        dialog = self.dialog((drama_node._receiver_sim_info), target_sim_id=target_sim_id,
          resolver=resolver)

        def response(dialog):
            for loot_action in self.on_dialog_complete_loot_list:
                loot_action.apply_to_resolver(resolver)

            if dialog.response is not None:
                if dialog.response != ButtonType.DIALOG_RESPONSE_NO_RESPONSE:
                    for loot_action in self.on_dialog_seen_loot_list:
                        loot_action.apply_to_resolver(resolver)

            DialogDramaNode.apply_cooldown_on_response(drama_node)
            DialogDramaNode.send_dialog_telemetry(drama_node, dialog)

        dialog.show_dialog(on_response=response)


class _loot_only(_dialog_and_loot):
    FACTORY_TUNABLES = {'on_drama_node_run_loot': TunableList(description='\n            A list of loot operations to apply when the drama node runs.\n            ',
                                 tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
                                 class_restrictions=('LootActions', 'RandomWeightedLoot'),
                                 pack_safe=True))}

    def on_node_run(self, drama_node):
        resolver = drama_node._get_resolver()
        for loot_action in self.on_drama_node_run_loot:
            loot_action.apply_to_resolver(resolver)


class _dialog_ok_cancel_and_loot(_dialog_and_loot):
    FACTORY_TUNABLES = {'dialog':UiDialogOkCancel.TunableFactory(description='\n            The ok cancel dialog that will display to the user.\n            '), 
     'on_dialog_complete_loot_list':TunableList(description='\n            A list of loot that will be applied when the player responds to the\n            dialog or, if the dialog is a phone ring or text message, when the\n            dialog times out due to the player ignoring it for too long.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       class_restrictions=('LootActions', 'RandomWeightedLoot'),
       pack_safe=True)), 
     'on_dialog_accetped_loot_list':TunableList(description='\n            A list of loot operations to apply when the player chooses ok.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       class_restrictions=('LootActions', 'RandomWeightedLoot'),
       pack_safe=True)), 
     'on_dialog_canceled_loot_list':TunableList(description='\n            A list of loot operations to apply when the player chooses cancel.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       class_restrictions=('LootActions', 'RandomWeightedLoot'),
       pack_safe=True)), 
     'on_dialog_no_response_loot_list':TunableList(description="\n            A list of loot operations to apply when the player ignores and doesn't respond, timing out the dialog.\n            ",
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       class_restrictions=('LootActions', 'RandomWeightedLoot'),
       pack_safe=True))}

    def on_node_run(self, drama_node):
        resolver = drama_node._get_resolver()
        target_sim_id = drama_node._sender_sim_info.id if drama_node._sender_sim_info is not None else None
        dialog = self.dialog((drama_node._receiver_sim_info), target_sim_id=target_sim_id,
          resolver=resolver)

        def response(dialog):
            for loot_action in self.on_dialog_complete_loot_list:
                loot_action.apply_to_resolver(resolver)

            if dialog.response is not None:
                if dialog.response == ButtonType.DIALOG_RESPONSE_OK:
                    for loot_action in self.on_dialog_accetped_loot_list:
                        loot_action.apply_to_resolver(resolver)

                else:
                    if dialog.response == ButtonType.DIALOG_RESPONSE_CANCEL:
                        for loot_action in self.on_dialog_canceled_loot_list:
                            loot_action.apply_to_resolver(resolver)

                    else:
                        if dialog.response == ButtonType.DIALOG_RESPONSE_NO_RESPONSE:
                            for loot_action in self.on_dialog_no_response_loot_list:
                                loot_action.apply_to_resolver(resolver)

            DialogDramaNode.apply_cooldown_on_response(drama_node)
            DialogDramaNode.send_dialog_telemetry(drama_node, dialog)

        dialog.show_dialog(on_response=response)


class _dialog_multi_tested_response(_dialog_and_loot):
    FACTORY_TUNABLES = {'dialog':UiDialog.TunableFactory(description='\n            The dialog that will display to the user.\n            '), 
     'on_dialog_complete_loot_list':TunableList(description='\n            A list of loot that will be applied when the player responds to the\n            dialog or, if the dialog is a phone ring or text message, when the\n            dialog times out due to the player ignoring it for too long.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       class_restrictions=('LootActions', 'RandomWeightedLoot'),
       pack_safe=True)), 
     'possible_responses':TunableTestedList(description='\n            A tunable tested list of the possible responses to this dialog.\n            ',
       tunable_type=TunableTuple(description='\n                A possible response for this dialog.\n                ',
       text=TunableLocalizedStringFactory(description='\n                    The text of the response field.\n                    '),
       loot=TunableList(description='\n                    A list of loot that will be applied when the player selects this response.\n                    ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       class_restrictions=('LootActions', 'RandomWeightedLoot'),
       pack_safe=True))))}

    def on_node_run(self, drama_node):
        resolver = drama_node._get_resolver()
        responses = []
        for index, possible_response in self.possible_responses(resolver=resolver, yield_index=True):
            responses.append(UiDialogResponse(dialog_response_id=index, text=(possible_response.text),
              ui_request=(UiDialogResponse.UiDialogUiRequest.NO_REQUEST)))

        target_sim_id = drama_node._sender_sim_info.id if drama_node._sender_sim_info is not None else None
        dialog = self.dialog((drama_node._receiver_sim_info), target_sim_id=target_sim_id,
          resolver=resolver)
        dialog.set_responses(responses)

        def response(dialog):
            for loot_action in self.on_dialog_complete_loot_list:
                loot_action.apply_to_resolver(resolver)

            if 0<= dialog.response < len(self.possible_responses):
                for loot_action in self.possible_responses[dialog.response].item.loot:
                    loot_action.apply_to_resolver(resolver)

            DialogDramaNode.apply_cooldown_on_response(drama_node)
            DialogDramaNode.send_dialog_telemetry(drama_node, dialog)

        dialog.show_dialog(on_response=response)


class DialogDramaNode(BaseDramaNode):
    INSTANCE_TUNABLES = {'dialog_and_loot':TunableVariant(description='\n            The type of dialog and loot that will be applied.\n            ',
       notification=_notification_and_loot.TunableFactory(),
       dialog_ok=_dialog_ok_and_loot.TunableFactory(),
       dialog_ok_cancel=_dialog_ok_cancel_and_loot.TunableFactory(),
       dialog_multi_response=_dialog_multi_tested_response.TunableFactory(),
       loot_only=_loot_only.TunableFactory(),
       default='notification'), 
     'is_simless':Tunable(description='\n            If checked, this drama node will not be linked to any specific sim. \n            ',
       tunable_type=bool,
       default=False), 
     'live_event_telemetry_name':OptionalTunable(description='\n            If tuned, the dialog shown by this drama node will send telemetry about the live event that opened it.\n            ',
       tunable=TunableEnumEntry(description='\n                Name of the live event that triggered this drama node.\n                ',
       tunable_type=LiveEventName,
       default=(LiveEventName.DEFAULT),
       invalid_enums=(
      LiveEventName.DEFAULT,)))}

    @classproperty
    def drama_node_type(cls):
        return DramaNodeType.DIALOG

    @classproperty
    def simless(cls):
        return cls.is_simless

    def run(self):
        if self.simless:
            self._receiver_sim_info = services.active_sim_info()
        return super().run()

    def _run(self):
        self.dialog_and_loot.on_node_run(self)
        return DramaNodeRunOutcome.SUCCESS_NODE_COMPLETE

    @classmethod
    def apply_cooldown_on_response(cls, drama_node):
        if drama_node.cooldown is not None:
            if drama_node.cooldown.cooldown_option == CooldownOption.ON_DIALOG_RESPONSE:
                services.drama_scheduler_service().start_cooldown(drama_node)

    @classmethod
    def send_dialog_telemetry(cls, drama_node, dialog):
        if drama_node.live_event_telemetry_name is not None:
            LiveEventTelemetry.send_live_event_dialog_telemetry(drama_node.live_event_telemetry_name, dialog.owner, dialog.response)