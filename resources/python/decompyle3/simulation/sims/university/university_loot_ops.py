# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\university\university_loot_ops.py
# Compiled at: 2022-07-21 18:49:30
# Size of source mod 2**32: 37221 bytes
import random
from event_testing.tests import TunableTestSet
from protocolbuffers import UI_pb2
from protocolbuffers.DistributorOps_pb2 import Operation
from distributor.ops import GenericProtocolBufferOp
from distributor.rollback import ProtocolBufferRollback
from distributor.shared_messages import create_icon_info_msg, IconInfoData
from distributor.system import Distributor
from event_testing.test_events import TestEvent
from interactions import ParticipantType
from interactions.utils.loot_basic_op import BaseLootOperation
from interactions.utils.success_chance import SuccessChance
from interactions.utils.tunable_icon import TunableIcon, TunableIconAllPacks
from sims.university.university_enums import EnrollmentStatus, UniversityInfoType, HomeworkCheatingStatus
from sims.university.university_scholarship_enums import ScholarshipStatus
from sims4.localization import TunableLocalizedString, LocalizationHelperTuning, TunableLocalizedStringFactory
from sims4.tuning.tunable import Tunable, TunableReference, TunableVariant, HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry, TunablePackSafeReference, TunableResourceKey, TunableList, TunableTuple, TunableRange
from ui.ui_dialog_notification import UiDialogNotification
import date_and_time, services, sims4.log, sims4.resources
logger = sims4.log.Logger('UniversityLootOperations')

class UniversityCourseGradeNotification(BaseLootOperation):

    class _FromUniversityCourseReference(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'_course_slot': TunableReference(description='\n                Course slot from which to pull grade\n                ',
                           manager=(services.get_instance_manager(sims4.resources.Types.CAREER)),
                           class_restrictions=('UniversityCourseCareerSlot', ))}

        def get_career_uid(self, resolver):
            return self._course_slot.guid64

    class _FromCareerSuperInteraction(HasTunableSingletonFactory, AutoFactoryInit):

        def get_career_uid(self, resolver):
            interaction = resolver.interaction
            if interaction is None:
                logger.error('Attempting to give grade TNS via career super interaction where interaction is unavailable.')
                return
            career_uid = interaction.interaction_parameters.get('career_uid')
            if career_uid is None:
                logger.error("Attempting to give grade TNS via interaction {} via career super interaction, but it isn't one.")
            return career_uid

    class _FromParticipant(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'participant': TunableEnumEntry(description='\n                The id of the career upon which the op will be applied to. Typically \n                should be PickedItemId if this loot is being applied by the \n                continuation of a CareerPickerSuperInteraction.\n                ',
                          tunable_type=ParticipantType,
                          default=(ParticipantType.PickedItemId))}

        def get_career_uid(self, resolver):
            return resolver.get_participant(self.participant)

    FACTORY_TUNABLES = {'course':TunableVariant(description='\n            How to determine which course to display the grade for.\n            From career super interaction should only be used if the loot is given\n            via a career super interaction.\n            ',
       from_university_course_reference=_FromUniversityCourseReference.TunableFactory(),
       from_career_super_interaction=_FromCareerSuperInteraction.TunableFactory(),
       from_participant=_FromParticipant.TunableFactory(),
       default='from_university_course_reference'), 
     'update_known_grade':Tunable(description='\n            If True, it will update the known grade.\n            ',
       tunable_type=bool,
       default=True)}

    def __init__(self, course, update_known_grade, **kwargs):
        (super().__init__)(**kwargs)
        self.course = course
        self.update_known_grade = update_known_grade

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if not (subject is None or subject.is_sim):
            return
        sim_info = subject.sim_info
        degree_tracker = sim_info.degree_tracker
        if degree_tracker is None:
            logger.error('Attempting to give grade TNS for sim {} who has no degree tracker', sim_info)
            return
        career_uid = self.course.get_career_uid(resolver)
        if career_uid is None or career_uid not in degree_tracker.course_infos:
            return
        degree_tracker.get_grade_report(career_uid)


class UniversityLootOp(BaseLootOperation):

    class _AcceptanceResult(HasTunableSingletonFactory):

        def perform(self, subject, target, resolver):
            if subject is None:
                logger.error('Trying to perform AcceptanceResult op but subject is None. Resolver {}.', resolver)
                return
            if not subject.is_sim:
                logger.error('Trying to perform AcceptanceResult op but subject {} is not Sim. Resolver {}.', subject, resolver)
                return
            degree_tracker = subject.sim_info.degree_tracker
            if degree_tracker is None:
                logger.error('Trying to perform AcceptanceResult op on sim {} with no degree tracker. Resolver {}.', subject, resolver)
                return
            degree_tracker.process_acceptance()

    class _CheatedOnHomework(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'course_career_slot':TunablePackSafeReference(description='\n                The course career slot we will get the course from to update the \n                cheating status of.\n                ',
           manager=services.get_instance_manager(sims4.resources.Types.CAREER),
           class_restrictions='UniversityCourseCareerSlot'), 
         'success_chance':SuccessChance.TunableFactory(description='\n                Chance that the sim will be caught cheating.\n                ')}

        def perform(self, subject, target, resolver):
            if not (subject is None or subject.is_sim):
                return
            if not subject.is_sim:
                return
            sim_info = subject.sim_info
            if self.course_career_slot is None:
                logger.error('Attempting to update the final project completion status for sim {}, but the specified course career slot is None.Possibly due to PackSafeness.', sim_info)
                return
            degree_tracker = sim_info.degree_tracker
            if degree_tracker is None:
                logger.error('Attempting to mark that sim {} cheated on their homework but they have no degree tracker', sim_info)
                return
            if random.random() > self.success_chance.get_chance(resolver):
                degree_tracker.update_homework_cheating_status(self.course_career_slot, HomeworkCheatingStatus.CHEATING_FAIL)
                return
            degree_tracker.update_homework_cheating_status(self.course_career_slot, HomeworkCheatingStatus.CHEATING_SUCCESS)

    class _EnrollmentStatusChange(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'enrollment_status':TunableEnumEntry(description='\n                The enrollment status to give to the sim. \n                ',
           tunable_type=EnrollmentStatus,
           default=EnrollmentStatus.NOT_ENROLLED), 
         'show_confirmation_dialog':Tunable(description='\n                If checked, a confirmation dialog will appear so the\n                player can confirm before the enrollment status is\n                changed.\n                \n                Currently, this behavior is only supported for \n                DROPOUT.\n                ',
           tunable_type=bool,
           default=False)}

        def perform(self, subject, target, resolver):
            if subject is None:
                return
            if not subject.is_sim:
                return
            sim_info = subject.sim_info
            degree_tracker = sim_info.degree_tracker
            if degree_tracker is None:
                logger.error('Attempting to change enrollment status for sim {} who has no degree tracker', sim_info)
                return
            degree_tracker.set_enrollment_status(self.enrollment_status, self.show_confirmation_dialog)

    class _UniversityDynamicSignView(HasTunableSingletonFactory, AutoFactoryInit):

        class _LiteralString(HasTunableSingletonFactory, AutoFactoryInit):
            FACTORY_TUNABLES = {'text': TunableLocalizedStringFactory(description='\n                    The text to be shown.\n                    \n                    * Token 0: Sim\n                    ')}

            def get_string(self, sim_info):
                return self.text(sim_info)

        class _FromSimInfo(HasTunableSingletonFactory, AutoFactoryInit):
            FACTORY_TUNABLES = {'university':TunableReference(description='\n                    The university to get the data from.\n                    ',
               manager=services.get_instance_manager(sims4.resources.Types.UNIVERSITY)), 
             'info_type':TunableEnumEntry(description='\n                    The type of the university info.\n                    ',
               tunable_type=UniversityInfoType,
               default=UniversityInfoType.INVALID,
               invalid_enums=(
              UniversityInfoType.INVALID, UniversityInfoType.ORGANIZATIONS)), 
             'fallback_string':TunableLocalizedStringFactory(description='\n                    The string to be shown when failing to find string from\n                    the tuned sim degree info.\n                    \n                    * Token 0: Sim\n                    ')}

            def get_string(self, sim_info):
                degree_tracker = sim_info.degree_tracker
                if degree_tracker is None:
                    logger.error('Trying to perform UniversityDynamicSignView op on sim {} with no degree tracker.', sim_info)
                    return
                uni = self.university
                manager = services.get_instance_manager(sims4.resources.Types.UNIVERSITY_MAJOR)
                available_degrees = degree_tracker.get_available_degrees_to_enroll()
                if available_degrees:
                    if uni.guid64 not in available_degrees or available_degrees[uni.guid64]:
                        return self.fallback_string(sim_info)
                    degree_ids = available_degrees[uni.guid64]
                    bullet_points = ()
                    if self.info_type == UniversityInfoType.PRESTIGE_DEGREES:
                        bullet_points = (manager.get(i).display_name for i in degree_ids if i in uni.prestige_degree_ids)
                    else:
                        if self.info_type == UniversityInfoType.NON_PRESTIGE_DEGREES:
                            bullet_points = (manager.get(i).display_name for i in degree_ids if i in uni.non_prestige_degree_ids)
                    final_string = (LocalizationHelperTuning.get_bulleted_list)(*(None, ), *bullet_points)
                    if final_string is None:
                        final_string = self.fallback_string(sim_info)
                    return final_string

        class _FromUniversityInfo(HasTunableSingletonFactory, AutoFactoryInit):
            FACTORY_TUNABLES = {'university':TunableReference(description='\n                    The university to get the data from.\n                    ',
               manager=services.get_instance_manager(sims4.resources.Types.UNIVERSITY)), 
             'info_type':TunableEnumEntry(description='\n                    The type of the university info.\n                    ',
               tunable_type=UniversityInfoType,
               default=UniversityInfoType.INVALID,
               invalid_enums=(
              UniversityInfoType.INVALID,))}

            def get_string(self, _):
                bullet_points = ()
                if self.info_type == UniversityInfoType.PRESTIGE_DEGREES:
                    bullet_points = (d.display_name for d in self.university.prestige_degrees)
                else:
                    if self.info_type == UniversityInfoType.NON_PRESTIGE_DEGREES:
                        bullet_points = (d.display_name for d in self.university.non_prestige_degrees)
                    else:
                        if self.info_type == UniversityInfoType.ORGANIZATIONS:
                            bullet_points = (o.display_name() for o in self.university.organizations if not o.hidden if  if not o.hidden)
                return (LocalizationHelperTuning.get_bulleted_list)(*(None, ), *bullet_points)

        class _FromUniversityAcceptance(HasTunableSingletonFactory, AutoFactoryInit):
            FACTORY_TUNABLES = {'university':TunableReference(description='\n                    The university to get the data from.\n                    ',
               manager=services.get_instance_manager(sims4.resources.Types.UNIVERSITY)), 
             'accepted_text':TunableLocalizedStringFactory(description='\n                    The string to show when the Sim has been accepted to the university specified.\n\n                    * Token 0: Sim\n                    '), 
             'denied_text':TunableLocalizedStringFactory(description='\n                    The string to show when the Sim has been denied from attending the university specified.\n\n                    * Token 0: Sim\n                    ')}

            def get_string(self, sim_info):
                degree_tracker = sim_info.degree_tracker
                if degree_tracker is None:
                    logger.error('Trying to perform UniversityDynamicSignView op on sim {} with no degree tracker.', sim_info)
                    return
                uni = self.university
                available_degrees = degree_tracker.get_available_degrees_to_enroll()
                if available_degrees:
                    if uni.guid64 not in available_degrees or available_degrees[uni.guid64]:
                        return self.denied_text(sim_info)
                    return self.accepted_text(sim_info)

        FACTORY_TUNABLES = {'title':TunableLocalizedString(description='\n                The title to be shown on top of view.\n                '), 
         'display_image':TunableResourceKey(description='\n                 The image for this view display.\n                 ',
           resource_types=sims4.resources.CompoundTypes.IMAGE), 
         'background_image':TunableResourceKey(description='\n                 The background image for this view display.\n                 ',
           resource_types=sims4.resources.CompoundTypes.IMAGE), 
         'sub_infos':TunableList(description='\n                The sub info to be shown on the bottom of the view.\n                ',
           tunable=TunableTuple(description='\n                    A single info.\n                    ',
           name=TunableLocalizedString(description='\n                        The name of this info.\n                        '),
           desc=TunableVariant(description='\n                        The description of this info.\n                        ',
           literal=(_LiteralString.TunableFactory()),
           from_sim_info=(_FromSimInfo.TunableFactory()),
           from_university_info=(_FromUniversityInfo.TunableFactory()),
           from_university_acceptance=(_FromUniversityAcceptance.TunableFactory()),
           default='literal'),
           icon=TunableIcon(description='\n                        The Icon that represents this info.\n                        ')))}

        def perform(self, subject, target, resolver):
            if subject is None:
                logger.error('Trying to perform UniversityDynamicSignView op but subject is None. Resolver {}.', resolver)
                return
            if not subject.is_sim:
                logger.error('Trying to perform UniversityDynamicSignView op but subject {} is not Sim. Resolver {}.', subject, resolver)
                return
            sign_info = UI_pb2.DynamicSignView()
            sign_info.name = self.title
            sign_info.image = sims4.resources.get_protobuff_for_key(self.display_image)
            sign_info.background_image = sims4.resources.get_protobuff_for_key(self.background_image)
            for sub_info in self.sub_infos:
                with ProtocolBufferRollback(sign_info.activities) as activity_msg:
                    activity_msg.name = sub_info.name
                    activity_msg.description = sub_info.desc.get_string(subject.sim_info)
                    activity_msg.icon = create_icon_info_msg(IconInfoData(sub_info.icon))

            distributor = Distributor.instance()
            distributor.add_op(subject.sim_info, GenericProtocolBufferOp(Operation.DYNAMIC_SIGN_VIEW, sign_info))

    class _UpdateFinalRequirementCompletion(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'course_career_slot':TunablePackSafeReference(description='\n                The course career slot we will get the course from to update the \n                final requirement completion status of.\n                ',
           manager=services.get_instance_manager(sims4.resources.Types.CAREER),
           class_restrictions='UniversityCourseCareerSlot'), 
         'final_project_completed':Tunable(description='\n                The updated completion status of the final project.\n                ',
           tunable_type=bool,
           default=True)}

        def perform(self, subject, target, resolver):
            if subject is None:
                return
            if not subject.is_sim:
                return
            sim_info = subject.sim_info
            if self.course_career_slot is None:
                logger.error('Attempting to update the final project completion status for sim {}, but the specified course career slot is None.                               Possibly due to PackSafeness.', sim_info)
                return
            degree_tracker = sim_info.degree_tracker
            if degree_tracker is None:
                logger.error('Attempting to update the final project completion status for sim {} who has no degree tracker', sim_info)
                return
            degree_tracker.update_final_requirement_completion(self.course_career_slot, self.final_project_completed)

    FACTORY_TUNABLES = {'operation': TunableVariant(description='\n            University operation to perform.\n            ',
                    acceptance_result=(_AcceptanceResult.TunableFactory()),
                    cheated_on_homework=(_CheatedOnHomework.TunableFactory()),
                    dynamic_sign_view=(_UniversityDynamicSignView.TunableFactory()),
                    enrollment_status_change=(_EnrollmentStatusChange.TunableFactory()),
                    update_final_requirement_completion=(_UpdateFinalRequirementCompletion.TunableFactory()),
                    default='acceptance_result')}

    def __init__(self, operation, **kwargs):
        (super().__init__)(**kwargs)
        self.operation = operation

    def _apply_to_subject_and_target(self, subject, target, resolver):
        self.operation.perform(subject, target, resolver)


class ShowScholarshipDynamicSignLoot(BaseLootOperation):
    SCHOLARSHIP_INFORMATION_SIGN = TunableTuple(title=TunableLocalizedString(description='\n            The title to be shown on top of view.\n            '),
      display_image=TunableIconAllPacks(description='\n             The image for this view display.\n             '),
      background_image=TunableIconAllPacks(description='\n             The background image for this view display.\n             '),
      sub_infos=TunableList(description='\n            The sub info to be shown on the bottom of the view.\n            ',
      tunable=TunableTuple(description='\n                A single info.\n                ',
      name=TunableLocalizedString(description='\n                    The name of this info.\n                    '),
      desc=TunableLocalizedString(description='\n                    The description of this info.\n                    '),
      icon=TunableIconAllPacks(description='\n                    The Icon that represents this info.\n                    '))))

    def display_scholarship_info--- This code section failed: ---

 L. 574         0  LOAD_FAST                'self'
                2  LOAD_ATTR                SCHOLARSHIP_INFORMATION_SIGN
                4  LOAD_ATTR                display_image
                6  LOAD_CONST               None
                8  COMPARE_OP               is
               10  POP_JUMP_IF_TRUE     24  'to 24'
               12  LOAD_FAST                'self'
               14  LOAD_ATTR                SCHOLARSHIP_INFORMATION_SIGN
               16  LOAD_ATTR                background_image
               18  LOAD_CONST               None
               20  COMPARE_OP               is
               22  POP_JUMP_IF_FALSE    40  'to 40'
             24_0  COME_FROM            10  '10'

 L. 575        24  LOAD_GLOBAL              logger
               26  LOAD_METHOD              error
               28  LOAD_STR                 'Attempting to show scholarship sign to ({}) when content is None.'

 L. 576        30  LOAD_FAST                'subject'
               32  CALL_METHOD_2         2  '2 positional arguments'
               34  POP_TOP          

 L. 577        36  LOAD_CONST               None
               38  RETURN_VALUE     
             40_0  COME_FROM            22  '22'

 L. 580        40  LOAD_GLOBAL              UI_pb2
               42  LOAD_METHOD              DynamicSignView
               44  CALL_METHOD_0         0  '0 positional arguments'
               46  STORE_FAST               'sign_info'

 L. 581        48  LOAD_FAST                'self'
               50  LOAD_ATTR                SCHOLARSHIP_INFORMATION_SIGN
               52  LOAD_ATTR                title
               54  LOAD_FAST                'sign_info'
               56  STORE_ATTR               name

 L. 582        58  LOAD_GLOBAL              sims4
               60  LOAD_ATTR                resources
               62  LOAD_METHOD              get_protobuff_for_key
               64  LOAD_FAST                'self'
               66  LOAD_ATTR                SCHOLARSHIP_INFORMATION_SIGN
               68  LOAD_ATTR                display_image
               70  CALL_METHOD_1         1  '1 positional argument'
               72  LOAD_FAST                'sign_info'
               74  STORE_ATTR               image

 L. 583        76  LOAD_GLOBAL              sims4
               78  LOAD_ATTR                resources
               80  LOAD_METHOD              get_protobuff_for_key
               82  LOAD_FAST                'self'
               84  LOAD_ATTR                SCHOLARSHIP_INFORMATION_SIGN
               86  LOAD_ATTR                background_image
               88  CALL_METHOD_1         1  '1 positional argument'
               90  LOAD_FAST                'sign_info'
               92  STORE_ATTR               background_image

 L. 585        94  SETUP_LOOP          190  'to 190'
               96  LOAD_FAST                'self'
               98  LOAD_ATTR                SCHOLARSHIP_INFORMATION_SIGN
              100  LOAD_ATTR                sub_infos
              102  GET_ITER         
            104_0  COME_FROM           186  '186'
            104_1  COME_FROM           142  '142'
              104  FOR_ITER            188  'to 188'
              106  STORE_FAST               'sub_info'

 L. 586       108  LOAD_GLOBAL              ProtocolBufferRollback
              110  LOAD_FAST                'sign_info'
              112  LOAD_ATTR                activities
              114  CALL_FUNCTION_1       1  '1 positional argument'
              116  SETUP_WITH          180  'to 180'
              118  STORE_FAST               'activity_msg'

 L. 587       120  LOAD_FAST                'sub_info'
              122  LOAD_ATTR                icon
              124  LOAD_CONST               None
              126  COMPARE_OP               is
              128  POP_JUMP_IF_FALSE   144  'to 144'

 L. 588       130  LOAD_GLOBAL              logger
              132  LOAD_METHOD              error
              134  LOAD_STR                 'Attempting to show scholarship sign to ({}) when sub_info icon is None.'

 L. 589       136  LOAD_FAST                'subject'
              138  CALL_METHOD_2         2  '2 positional arguments'
              140  POP_TOP          

 L. 590       142  CONTINUE_LOOP       104  'to 104'
            144_0  COME_FROM           128  '128'

 L. 591       144  LOAD_FAST                'sub_info'
              146  LOAD_ATTR                name
              148  LOAD_FAST                'activity_msg'
              150  STORE_ATTR               name

 L. 592       152  LOAD_FAST                'sub_info'
              154  LOAD_ATTR                desc
              156  LOAD_FAST                'activity_msg'
              158  STORE_ATTR               description

 L. 593       160  LOAD_GLOBAL              create_icon_info_msg
              162  LOAD_GLOBAL              IconInfoData
              164  LOAD_FAST                'sub_info'
              166  LOAD_ATTR                icon
              168  CALL_FUNCTION_1       1  '1 positional argument'
              170  CALL_FUNCTION_1       1  '1 positional argument'
              172  LOAD_FAST                'activity_msg'
              174  STORE_ATTR               icon
              176  POP_BLOCK        
              178  LOAD_CONST               None
            180_0  COME_FROM_WITH      116  '116'
              180  WITH_CLEANUP_START
              182  WITH_CLEANUP_FINISH
              184  END_FINALLY      
              186  JUMP_LOOP           104  'to 104'
              188  POP_BLOCK        
            190_0  COME_FROM_LOOP       94  '94'

 L. 595       190  LOAD_GLOBAL              Distributor
              192  LOAD_METHOD              instance
              194  CALL_METHOD_0         0  '0 positional arguments'
              196  STORE_FAST               'distributor'

 L. 596       198  LOAD_FAST                'distributor'
              200  LOAD_METHOD              add_op
              202  LOAD_FAST                'subject'
              204  LOAD_ATTR                sim_info
              206  LOAD_GLOBAL              GenericProtocolBufferOp
              208  LOAD_GLOBAL              Operation
              210  LOAD_ATTR                DYNAMIC_SIGN_VIEW
              212  LOAD_FAST                'sign_info'
              214  CALL_FUNCTION_2       2  '2 positional arguments'
              216  CALL_METHOD_2         2  '2 positional arguments'
              218  POP_TOP          

 L. 597       220  LOAD_GLOBAL              services
              222  LOAD_METHOD              get_event_manager
              224  CALL_METHOD_0         0  '0 positional arguments'
              226  LOAD_ATTR                process_event
              228  LOAD_GLOBAL              TestEvent
              230  LOAD_ATTR                ScholarshipInfoSignShown
              232  LOAD_FAST                'subject'
              234  LOAD_CONST               ('sim_info',)
              236  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              238  POP_TOP          

Parse error at or near `CONTINUE_LOOP' instruction at offset 142

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if subject is None:
            logger.error('Trying to perform ScholarshipDynamicSignView op but subject is None. Resolver ({}).', resolver)
            return
        self.display_scholarship_info(subject)


class ShowHighChanceScholarshipsLoot(BaseLootOperation):
    SCHOLARSHIP_AMOUNT_DISPLAYED = TunableRange(description="\n        The number of scholarships to display to the Sim in a notification\n        after running 'Get_Guidance_Counselor_Advice' loot action.\n        ",
      tunable_type=int,
      default=3,
      minimum=1)
    HIGH_CHANCE_SCHOLARSHIP_NOTIFICATION = UiDialogNotification.TunableFactory(description='\n        Message when a Sim requests to show scholarships they have the best chance\n        to win.\n        ')

    def _apply_to_subject_and_target(self, subject, target, resolver):
        dialog = self.HIGH_CHANCE_SCHOLARSHIP_NOTIFICATION(subject, None)
        degree_tracker = subject.degree_tracker
        if degree_tracker is None:
            return
        high_chance_scholarships = degree_tracker.get_best_scored_scholarship_list(self.SCHOLARSHIP_AMOUNT_DISPLAYED, resolver, subject)
        dialog.show_dialog(secondary_icon_override=IconInfoData(obj_instance=subject), additional_tokens=(
         subject, high_chance_scholarships))


class ScholarshipActionLoot(BaseLootOperation):

    class _LoseScholarship(HasTunableSingletonFactory, AutoFactoryInit):

        def perform(self, degree_tracker, scholarship):
            degree_tracker.lose_scholarship(scholarship)

    class _GrantScholarship(HasTunableSingletonFactory, AutoFactoryInit):

        def perform(self, degree_tracker, scholarship):
            degree_tracker.grant_scholarship(scholarship)

    FACTORY_TUNABLES = {'scholarship_action':TunableVariant(description='\n            University operation to perform.\n            ',
       lose_scholarship=_LoseScholarship.TunableFactory(description="\n                Cause the Sim to lose an earned scholarship. If it is not already earned,\n                it will still be added to the sim's rejected scholarship list, which\n                will prohibit the Sim from applying to that scholarship until a new\n                semester begins.\n                "),
       grant_scholarship=_GrantScholarship.TunableFactory(description="\n                Cause the Sim to gain a scholarship as if it was earned. This bypasses\n                the 'application' step.\n                "),
       default='lose_scholarship'), 
     'scholarship':TunablePackSafeReference(description='\n            The scholarship to apply the scholarship action.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.SNIPPET),
       class_restrictions='Scholarship')}

    def __init__(self, scholarship_action, scholarship, **kwargs):
        (super().__init__)(**kwargs)
        self.scholarship_action = scholarship_action
        self.scholarship = scholarship

    def _apply_to_subject_and_target(self, subject, target, resolver):
        degree_tracker = subject.degree_tracker
        if degree_tracker is None:
            logger.error('Cannot perform scholarship action loot for Sim ({}) because the degree tracker is None.', subject)
            return
        if self.scholarship is None:
            logger.error('Cannot perform scholarship action loot for Sim ({}) because the scholarship is None.')
            return
        self.scholarship_action.perform(degree_tracker, self.scholarship)


class ApplyForScholarshipLoot(BaseLootOperation):
    APPLICATION_RESULT_DELAY_TIME = TunableRange(description="\n        The tunable number of Sim hours to wait before resolving a scholarship\n        applicant's status. \n        \n        At the point the delay ends, 1) the Sim will be able to check their application\n        status on a computer and 2) an application response letter will be scheduled\n        for delivery to the home lot.\n        ",
      tunable_type=int,
      default=1440,
      minimum=1)
    FACTORY_TUNABLES = {'scholarship': TunableReference(description='\n            The organization for which this drama node is scheduling venue events.\n            ',
                      manager=(services.get_instance_manager(sims4.resources.Types.SNIPPET)),
                      class_restrictions='Scholarship')}
    MAX_SCORE = 100

    def __init__(self, *args, scholarship, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._scholarship = scholarship

    def _apply_to_subject_and_target(self, subject, target, resolver):
        degree_tracker = subject.degree_tracker
        if degree_tracker is None:
            logger.error("({}) is applying for a scholarship, but ({})'s degree tracker is None. Application failed.", str(subject))
            return
        degree_tracker.process_scholarship_application(self._scholarship, date_and_time.create_time_span(hours=(self.APPLICATION_RESULT_DELAY_TIME)))


class GetScholarshipStatusLoot(BaseLootOperation):
    SCHOLARSHIP_STATUS_NOTIFICATION = UiDialogNotification.TunableFactory(description="\n        Notification displayed when a Sim requests to show the current status of scholarships\n        they've applied this term.\n        ")
    SCHOLARSHIP_STATUS_NO_SCHOLARSHIPS_NOTIFICATION = UiDialogNotification.TunableFactory(description='\n        Notification displayed when there are no scholarships to report.\n        ')
    SCHOLARSHIP_STATUS_HEADER_ENTRY_ACTIVE = TunableLocalizedString(description='\n        The header string to use for scholarships with an active status.\n        ')
    SCHOLARSHIP_STATUS_HEADER_ENTRY_ACCEPTED = TunableLocalizedString(description='\n        The header string to use for scholarships with an accepted status.\n        ')
    SCHOLARSHIP_STATUS_HEADER_ENTRY_REJECTED = TunableLocalizedString(description='\n        The header string to use for scholarships with a rejected status.\n        ')
    SCHOLARSHIP_STATUS_HEADER_ENTRY_PENDING = TunableLocalizedString(description='\n        The header string to use for scholarships with a pending status.\n        ')
    SCHOLARSHIP_VALUE_ENTRY_POINT = TunableLocalizedString(description='\n        The format of the line in the notification description in which to embed scholarship value.\n        ')
    SCHOLARSHIP_STATUS_CATEGORIES_AMOUNT = 4

    def _apply_to_subject_and_target(self, subject, target, resolver):
        degree_tracker = subject.degree_tracker
        if degree_tracker is None:
            return
        empty_list_counter = 0
        first_list_entry = True
        active_scholarship_list = degree_tracker.get_scholarships_list_by_status(ScholarshipStatus.ACTIVE, subject, first_list_entry)
        if active_scholarship_list is None:
            active_scholarship_list = LocalizationHelperTuning.get_raw_text('')
            empty_list_counter += 1
        else:
            first_list_entry = False
        pending_scholarships_list = degree_tracker.get_scholarships_list_by_status(ScholarshipStatus.PENDING, subject, first_list_entry)
        if pending_scholarships_list is None:
            pending_scholarships_list = LocalizationHelperTuning.get_raw_text('')
            empty_list_counter += 1
        else:
            first_list_entry = False
        accepted_scholarships_list = degree_tracker.get_scholarships_list_by_status(ScholarshipStatus.ACCEPTED, subject, first_list_entry)
        if accepted_scholarships_list is None:
            accepted_scholarships_list = LocalizationHelperTuning.get_raw_text('')
            empty_list_counter += 1
        else:
            first_list_entry = False
        rejected_scholarships_list = degree_tracker.get_scholarships_list_by_status(ScholarshipStatus.REJECTED, subject, first_list_entry)
        if rejected_scholarships_list is None:
            rejected_scholarships_list = LocalizationHelperTuning.get_raw_text('')
            empty_list_counter += 1
        else:
            first_list_entry = False
        if empty_list_counter >= self.SCHOLARSHIP_STATUS_CATEGORIES_AMOUNT:
            dialog = self.SCHOLARSHIP_STATUS_NO_SCHOLARSHIPS_NOTIFICATION(subject, None)
            dialog.show_dialog(secondary_icon_override=IconInfoData(obj_instance=subject), additional_tokens=(
             subject,))
            return
        dialog = self.SCHOLARSHIP_STATUS_NOTIFICATION(subject, None)
        dialog.show_dialog(secondary_icon_override=IconInfoData(obj_instance=subject), additional_tokens=(
         subject, active_scholarship_list, pending_scholarships_list, accepted_scholarships_list, rejected_scholarships_list))