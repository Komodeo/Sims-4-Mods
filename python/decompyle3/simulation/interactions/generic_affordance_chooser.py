# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\generic_affordance_chooser.py
# Compiled at: 2022-07-21 18:49:30
# Size of source mod 2**32: 3770 bytes
from event_testing.resolver import SingleSimResolver
from event_testing.results import TestResult
from interactions.base.immediate_interaction import ImmediateSuperInteraction
from interactions.base.super_interaction import SuperInteraction
from ui.ui_dialog import UiDialogOkCancel
import interactions

class GenericChooseBetweenTwoAffordancesSuperInteraction(ImmediateSuperInteraction):
    INSTANCE_TUNABLES = {'choice_dialog':UiDialogOkCancel.TunableFactory(description='\n            A Dialog that prompts the user with a two button dialog. The\n            chosen button will result in one of two affordances being chosen.\n            '), 
     'accept_affordance':SuperInteraction.TunablePackSafeReference(description='\n            The affordance to push on the sim if the user clicks on the \n            accept/ok button.\n            '), 
     'reject_affordance':SuperInteraction.TunablePackSafeReference(description='\n            The affordance to push on the Sim if the user chooses to click\n            on the reject/cancel button.\n            ')}

    @classmethod
    def _test(cls, target, context, **interaction_parameters):
        if cls.accept_affordance is None:
            if cls.reject_affordance is None:
                return TestResult(False, 'The accept and reject affordances are unavailable with the currently installed packs.')
        return (super()._test)(target, context, **interaction_parameters)

    def _run_interaction_gen(self, timeline):
        context = self.context.clone_for_sim((self.sim), insert_strategy=(interactions.context.QueueInsertStrategy.LAST))
        if self.accept_affordance is None or self.reject_affordance is None:
            affordance = self.accept_affordance or self.reject_affordance
            self.sim.push_super_affordance(affordance, target=(self.target), context=context)
            return

        def _on_response(dialog):
            affordance = self.accept_affordance if dialog.accepted else self.reject_affordance
            self.sim.push_super_affordance(affordance, target=(self.target),
              context=context)

        dialog = self.choice_dialog((self.sim), resolver=(self.get_resolver()))
        dialog.show_dialog(on_response=_on_response)
        if False:
            yield None