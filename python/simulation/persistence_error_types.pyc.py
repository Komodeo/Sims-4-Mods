# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\persistence_error_types.py
# Compiled at: 2022-07-21 18:49:30
# Size of source mod 2**32: 6442 bytes
import traceback, enum, sims4.hash_util
TELEMETRY_FIELD_EXCEPTION_HASH = 'expt'
TELEMETRY_FIELD_EXCEPTION_HASH_CALLSTACK = 'estk'

class ErrorCodes(enum.Int, export=False):
    NO_ERROR = 0
    GENERIC_ERROR = 100
    STOP_CACHING_STATE_FAILED = 101
    LOAD_HOUSEHOLD_AND_SIM_INFO_STATE_FAILED = 102
    SET_OBJECT_OWNERSHIP_STATE_FAILED = 103
    SPAWN_SIM_STATE_FAILED = 104
    WAIT_FOR_SIM_READY_STATE_FAILED = 105
    CLEANUP_STATE_FAILED = 106
    AWAY_ACTION_STATE_FAILED = 107
    RESTORE_SI_STATE_FAILED = 108
    SITUATION_COMMON_STATE_FAILED = 109
    WAIT_FOR_BOUNCER_STATE_FAILED = 110
    FINALIZE_OBJECT_STATE_FAILED = 111
    RESTORE_CAREER_STATE_FAILED = 112
    WAIT_FOR_NAVMESH_STATE_FAILED = 113
    INITIALIZED_FRONT_DOOR_STATE_FAILED = 114
    PREROLL_STATE_FAILED = 115
    PUSH_SIMS_GO_HOME_STATE_FAILED = 116
    SET_ACTIVE_SIM_STATE_FAILED = 117
    START_UP_COMMANDS_STATE_FAILED = 118
    START_CACHING_STATE_FAILED = 119
    FINAL_PLAYABLE_STATE_FAILED = 120
    HITTING_THEIR_MARKS_STATE_FAILED = 121
    EDIT_MODE_STATE_FAILED = 122
    SELECT_ZONE_DIRECTOR_STATE_FAILED = 123
    DESTINATION_WORLD_CLEAN_UP_FAILED = 124
    PREMADE_SIM_FIXUP_STATE_FAILED = 125
    START_NO_WAITING_STATE_FAILED = 126
    END_NO_WAITING_STATE_FAILED = 127
    DETECT_AND_CLEANUP_INVALID_OBJECTS = 128
    SET_MAILBOX_OWNER_STATE_FAILED = 129
    FIXUP_INVENTORY_STATE_FAILED = 130
    RESTORE_MISSING_PETS_STATE_FAILED = 131
    SETUP_PORTALS_STATE_FAILED = 132
    SETUP_SURFACE_PORTALS_STATE_FAILED = 133
    RESTORE_RABBIT_HOLES_STATE_FAILED = 134
    SCHEDULE_STARTUP_DRAMA_NODES_STATE_FAILED = 135
    DESTROY_UNCLAIMED_OBJECTS_STATE_FAILED = 136
    ZONE_MODIFIER_SPIN_UP_STATE_FAILED = 137
    GLOBAL_LOT_TUNING_AND_CLEANUP_FAILED = 138
    SIM_INFO_FIXUP_STATE_FAILED = 139
    UPDATE_OBJECTIVES_STATE_FAILED = 140
    EDIT_MODE_WEATHER_SETUP_STATE_FAILED = 141
    RESTORE_QUEUED_SI_STATE_FAILED = 142
    CULL_PENDING_SIMS_FAILED = 143
    CREATE_FASHION_OUTFITS_FAILED = 144
    SETTING_SAVE_SLOT_DATA_FAILED = 300
    SAVE_TO_SLOT_FAILED = 301
    AUTOSAVE_TO_SLOT_FAILED = 302
    SAVE_CAMERA_DATA_FAILED = 303
    CORE_SERICES_SAVE_FAILED = 400
    SERVICE_SAVE_FAILED_ACCOUNT_SERVICE = 401
    SERVICE_SAVE_FAILED_BUSINESS_SERVICE = 402
    SERVICE_SAVE_FAILED_ZONE_MANAGER = 403
    SERVICE_SAVE_FAILED_CALL_TO_ACTION_SERVICE = 404
    SERVICE_SAVE_FAILED_CHEAT_SERVICE = 405
    SERVICE_SAVE_FAILED_WEATHER_SERVICE = 406
    SERVICE_SAVE_FAILED_LOT_DECORATION_SERVICE = 407
    SERVICE_SAVE_FAILED_HOLIDAY_SERVICE = 408
    SERVICE_SAVE_FAILED_STYLE_SERVICE = 409
    SERVICE_SAVE_FAILED_TREND_SERVICE = 410
    SERVICE_SAVE_FAILED_RABBIT_HOLE_SERVICE = 411
    SERVICE_SAVE_FAILED_NARRATIVE_SERVICE = 412
    SERVICE_SAVE_FAILED_GLOBAL_POLICY_SERVICE = 413
    SERVICE_SAVE_FAILED_ROOMMATE_SERVICE = 414
    SERVICE_SAVE_FAILED_STREET_CIVIC_POLICY_SERVICE = 415
    SERVICE_SAVE_FAILED_VENUE_GAME_SERVICE = 416
    SERVICE_SAVE_FAILED_REGION_SERVICE = 417
    SERVICE_SAVE_FAILED_LIFESTYLE_SERVICE = 417
    SERVICE_SAVE_FAILED_LIVE_EVENT_SERVICE = 418
    SERVICE_SAVE_FAILED_ANIMAL_SERVICE = 419
    SERVICE_SAVE_FAILED_PURCHASE_PICKER_SERVICE = 420
    ZONE_SERVICES_SAVE_FAILED = 500
    SERVICE_SAVE_FAILED_CLUB_SERVICE = 501
    SERVICE_SAVE_FAILED_CAREER_SERVICE = 502
    SERVICE_SAVE_FAILED_STORY_PROGRESSION_SERVICE = 503
    SERVICE_SAVE_FAILED_VENUE_SERVICE = 504
    SERVICE_SAVE_FAILED_DRAMA_SCHEDULE_SERVICE = 505
    SERVICE_SAVE_FAILED_UI_DIALOG_SERVICE = 506
    SERVICE_SAVE_FAILED_SITUATION_MANAGER = 507
    SERVICE_SAVE_FAILED_ENSEMBLE_SERVICE = 508
    SERVICE_SAVE_FAILED_TRAVEL_GROUP_MANAGER = 509
    SERVICE_SAVE_FAILED_SIM_INFO_MANAGER = 510
    SERVICE_SAVE_FAILED_DOOR_SERVICE = 511
    SERVICE_SAVE_FAILED_CONDITIONAL_LAYER_SERVICE = 512
    SERVICE_SAVE_FAILED_OBJECT_MANAGER = 513
    SERVICE_SAVE_FAILED_HOUSEHOLD_MANAGER = 514
    SERVICE_SAVE_FAILED_GAME_CLOCK = 515
    SERVICE_SAVE_FAILED_CURFEW_SERVICE = 516
    SERVICE_SAVE_FAILED_AMBIENT_SERVICE = 517
    SERVICE_SAVE_FAILED_ADOPTION_SERVICE = 518
    SERVICE_SAVE_FAILED_RELATIONSHIP_SERVICE = 519
    SERVICE_SAVE_FAILED_HIDDEN_SIM_SERVICE = 520
    SERVICE_SAVE_FAILED_SEASON_SERVICE = 521
    SERVICE_SAVE_FAILED_OBJECT_LOST_AND_FOUND_SERVICE = 522
    SERVICE_SAVE_FAILED_LANDLORD_SERVICE = 523
    SERVICE_SAVE_FAILED_ORGANIZATION_SERVICE = 524
    SERVICE_SAVE_FAILED_CULLING_SERVICE = 525
    SERVICE_SAVE_FAILED_CALENDAR_SERVICE = 526
    SERVICE_SAVE_FAILED_LUNAR_CYCLE_SERVICE = 527
    SERVICE_SAVE_FAILED_CLAN_SERVICE = 528
    SERVICE_SAVE_FAILED_SOCIAL_MEDIA_SERVICE = 529
    SERVICE_SAVE_FAILED_GRADUATION_SERVICE = 530
    SERVICE_SAVE_FAILED_PROM_SERVICE = 531
    SERVICE_SAVE_FAILED_FASHION_TREND_SERVICE = 532


def generate_exception_callstack(exception):
    return ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))


def generate_exception_and_call_stack_string(exception):
    exception_callstack = generate_exception_callstack(exception)
    return (
     f"{sims4.hash_util.hash32(str(exception)):x}", f"{sims4.hash_util.hash32(exception_callstack):x}")


def generate_exception_code_string(error_code, exception_string, exception_callstack_string):
    return '{}:{}:{}'.format(int(error_code), exception_string, exception_callstack_string)


def write_exception_info_to_hook(hook, exception_string, exception_callstack_string):
    hook.write_string(TELEMETRY_FIELD_EXCEPTION_HASH, exception_string)
    hook.write_string(TELEMETRY_FIELD_EXCEPTION_HASH_CALLSTACK, exception_callstack_string)