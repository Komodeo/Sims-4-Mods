# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\ui\screen_slam.py
# Compiled at: 2022-02-09 10:21:47
# Size of source mod 2**32: 5868 bytes
import itertools, protocolbuffers
from audio.primitive import TunablePlayAudio, play_tunable_audio
from interactions.utils.tunable_icon import TunableIcon
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.tunable import OptionalTunable, Tunable, TunableEnumEntry, AutoFactoryInit, HasTunableSingletonFactory, TunableVariant
from snippets import define_snippet, SCREEN_SLAM
import distributor, enum

class ScreenSlamType(enum.Int, export=False):
    LEGACY = 0
    CUSTOM = 1


class ScreenSlamSizeEnum(enum.Int):
    SMALL = 0
    MEDIUM = 1
    LARGE = 2
    EXTRA_LARGE = 3


class ScreenSlamSizeBased(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'screen_slam_size': TunableEnumEntry(description='\n            Screen slam size.\n            ',
                           tunable_type=ScreenSlamSizeEnum,
                           default=(ScreenSlamSizeEnum.MEDIUM))}

    def populate_screenslam_message(self, msg):
        msg.type = ScreenSlamType.LEGACY
        msg.size = self.screen_slam_size


class ScreenSlamKeyBased(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'key': Tunable(description='\n            Key to use for the screenslam. This will be typically tied\n            to what animation will play. Verify with your UI partner\n            what the correct value to use will be.\n        ',
              tunable_type=str,
              default='medium')}

    def populate_screenslam_message(self, msg):
        msg.type = ScreenSlamType.CUSTOM
        msg.ui_key = self.key


class ScreenSlamDisplayVariant(TunableVariant):

    def __init__(self, **kwargs):
        (super().__init__)(size_based=ScreenSlamSizeBased.TunableFactory(), 
         key_based=ScreenSlamKeyBased.TunableFactory(), 
         default='size_based', **kwargs)


class ScreenSlam(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'display_type':ScreenSlamDisplayVariant(), 
     'title':OptionalTunable(description='\n            Title of the screen slam.\n            ',
       tunable=TunableLocalizedStringFactory()), 
     'text':OptionalTunable(description='"\n            Text of the screen slam.\n            ',
       tunable=TunableLocalizedStringFactory()), 
     'icon':OptionalTunable(description=',\n            Icon to be displayed for the screen Slam.\n            ',
       tunable=TunableIcon()), 
     'audio_sting':OptionalTunable(description='\n            A sting to play at the same time as the screen slam.\n            ***Some screen slams may appear to play a sting, but the audio is\n            actually tuned on something else.  Example: On CareerLevel tuning\n            there already is a tunable, Promotion Audio Sting, to trigger a\n            sting, so one is not necessary on the screen slam.  Make sure to\n            avoid having multiple stings play simultaneously.***\n            ',
       tunable=TunablePlayAudio()), 
     'active_sim_only':Tunable(description='\n            If true, the screen slam will be only be shown if the active Sim\n            triggers it.\n            ',
       tunable_type=bool,
       default=True)}

    def send_screen_slam_message--- This code section failed: ---

 L. 135         0  LOAD_GLOBAL              protocolbuffers
                2  LOAD_ATTR                UI_pb2
                4  LOAD_METHOD              UiScreenSlam
                6  CALL_METHOD_0         0  '0 positional arguments'
                8  STORE_FAST               'msg'

 L. 136        10  LOAD_FAST                'self'
               12  LOAD_ATTR                display_type
               14  LOAD_METHOD              populate_screenslam_message
               16  LOAD_FAST                'msg'
               18  CALL_METHOD_1         1  '1 positional argument'
               20  POP_TOP          

 L. 137        22  LOAD_FAST                'self'
               24  LOAD_ATTR                text
               26  LOAD_CONST               None
               28  COMPARE_OP               is-not
               30  POP_JUMP_IF_FALSE    60  'to 60'

 L. 138        32  LOAD_FAST                'self'
               34  LOAD_ATTR                text
               36  LOAD_GENEXPR             '<code_object <genexpr>>'
               38  LOAD_STR                 'ScreenSlam.send_screen_slam_message.<locals>.<genexpr>'
               40  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
               42  LOAD_GLOBAL              itertools
               44  LOAD_METHOD              chain
               46  LOAD_FAST                'localization_tokens'
               48  CALL_METHOD_1         1  '1 positional argument'
               50  GET_ITER         
               52  CALL_FUNCTION_1       1  '1 positional argument'
               54  CALL_FUNCTION_EX      0  'positional arguments only'
               56  LOAD_FAST                'msg'
               58  STORE_ATTR               name
             60_0  COME_FROM            30  '30'

 L. 139        60  LOAD_FAST                'sim_info'
               62  LOAD_CONST               None
               64  COMPARE_OP               is-not
               66  POP_JUMP_IF_FALSE    76  'to 76'

 L. 140        68  LOAD_FAST                'sim_info'
               70  LOAD_ATTR                sim_id
               72  LOAD_FAST                'msg'
               74  STORE_ATTR               sim_id
             76_0  COME_FROM            66  '66'

 L. 141        76  LOAD_FAST                'self'
               78  LOAD_ATTR                icon
               80  LOAD_CONST               None
               82  COMPARE_OP               is-not
               84  POP_JUMP_IF_FALSE   122  'to 122'

 L. 142        86  LOAD_FAST                'self'
               88  LOAD_ATTR                icon
               90  LOAD_ATTR                group
               92  LOAD_FAST                'msg'
               94  LOAD_ATTR                icon
               96  STORE_ATTR               group

 L. 143        98  LOAD_FAST                'self'
              100  LOAD_ATTR                icon
              102  LOAD_ATTR                instance
              104  LOAD_FAST                'msg'
              106  LOAD_ATTR                icon
              108  STORE_ATTR               instance

 L. 144       110  LOAD_FAST                'self'
              112  LOAD_ATTR                icon
              114  LOAD_ATTR                type
              116  LOAD_FAST                'msg'
              118  LOAD_ATTR                icon
              120  STORE_ATTR               type
            122_0  COME_FROM            84  '84'

 L. 145       122  LOAD_FAST                'self'
              124  LOAD_ATTR                title
              126  LOAD_CONST               None
              128  COMPARE_OP               is-not
              130  POP_JUMP_IF_FALSE   160  'to 160'

 L. 146       132  LOAD_FAST                'self'
              134  LOAD_ATTR                title
              136  LOAD_GENEXPR             '<code_object <genexpr>>'
              138  LOAD_STR                 'ScreenSlam.send_screen_slam_message.<locals>.<genexpr>'
              140  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
              142  LOAD_GLOBAL              itertools
              144  LOAD_METHOD              chain
              146  LOAD_FAST                'localization_tokens'
              148  CALL_METHOD_1         1  '1 positional argument'
              150  GET_ITER         
              152  CALL_FUNCTION_1       1  '1 positional argument'
              154  CALL_FUNCTION_EX      0  'positional arguments only'
              156  LOAD_FAST                'msg'
              158  STORE_ATTR               title
            160_0  COME_FROM           130  '130'

 L. 147       160  LOAD_FAST                'self'
              162  LOAD_ATTR                audio_sting
              164  LOAD_CONST               None
              166  COMPARE_OP               is-not
              168  POP_JUMP_IF_FALSE   212  'to 212'

 L. 148       170  LOAD_FAST                'self'
              172  LOAD_ATTR                audio_sting
              174  LOAD_ATTR                audio
              176  LOAD_ATTR                group
              178  LOAD_FAST                'msg'
              180  LOAD_ATTR                audio_sting
              182  STORE_ATTR               group

 L. 149       184  LOAD_FAST                'self'
              186  LOAD_ATTR                audio_sting
              188  LOAD_ATTR                audio
              190  LOAD_ATTR                instance
              192  LOAD_FAST                'msg'
              194  LOAD_ATTR                audio_sting
              196  STORE_ATTR               instance

 L. 150       198  LOAD_FAST                'self'
              200  LOAD_ATTR                audio_sting
              202  LOAD_ATTR                audio
              204  LOAD_ATTR                type
              206  LOAD_FAST                'msg'
              208  LOAD_ATTR                audio_sting
              210  STORE_ATTR               type
            212_0  COME_FROM           168  '168'

 L. 151       212  LOAD_FAST                'self'
              214  LOAD_ATTR                active_sim_only
              216  POP_JUMP_IF_FALSE   232  'to 232'
              218  LOAD_FAST                'sim_info'
              220  LOAD_CONST               None
              222  COMPARE_OP               is-not
              224  POP_JUMP_IF_FALSE   232  'to 232'
              226  LOAD_FAST                'sim_info'
              228  LOAD_ATTR                is_selected
              230  POP_JUMP_IF_TRUE    240  'to 240'
            232_0  COME_FROM           224  '224'
            232_1  COME_FROM           216  '216'
              232  LOAD_FAST                'self'
              234  LOAD_ATTR                active_sim_only
          236_238  POP_JUMP_IF_TRUE    262  'to 262'
            240_0  COME_FROM           230  '230'

 L. 152       240  LOAD_GLOBAL              distributor
              242  LOAD_ATTR                shared_messages
              244  LOAD_METHOD              add_message_if_player_controlled_sim
              246  LOAD_FAST                'sim_info'
              248  LOAD_GLOBAL              protocolbuffers
              250  LOAD_ATTR                Consts_pb2
              252  LOAD_ATTR                MSG_UI_SCREEN_SLAM
              254  LOAD_FAST                'msg'
              256  LOAD_CONST               False
              258  CALL_METHOD_4         4  '4 positional arguments'
              260  POP_TOP          
            262_0  COME_FROM           236  '236'

Parse error at or near `POP_TOP' instruction at offset 260


TunableScreenSlamReference, TunableScreenSlamSnippet = define_snippet(SCREEN_SLAM, ScreenSlam.TunableFactory())