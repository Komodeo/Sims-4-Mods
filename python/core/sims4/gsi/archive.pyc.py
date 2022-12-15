# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\sims4\gsi\archive.py
# Compiled at: 2022-06-13 15:18:17
# Size of source mod 2**32: 17443 bytes
import json, time, zlib
from sims4.gsi.schema import GsiSchema, CLIENT_GSI_ARCHIVE_UID_FIX
from sims4.utils import create_csv
from uid import UniqueIdGenerator
import sims4.gsi.dispatcher, sims4.log, sims4.reload, sims4.zone_utils
logger = sims4.log.Logger('GSI')
with sims4.reload.protected(globals()):
    archive_data = {}
    archive_schemas = {}
    all_archivers = {}
    archive_id = UniqueIdGenerator()
ARCHIVE_DEFAULT_RECORDS = 50
ARCHIVE_MAX_RECORDS = ARCHIVE_DEFAULT_RECORDS

def set_max_archive_records(max_records):
    global ARCHIVE_MAX_RECORDS
    ARCHIVE_MAX_RECORDS = max_records


def set_max_archive_records_default():
    set_max_archive_records(ARCHIVE_DEFAULT_RECORDS)


def set_archive_enabled(archive_type, enable=True):
    if archive_type in all_archivers:
        all_archivers[archive_type].archive_enable_fn(enableLog=enable)
    else:
        logger.error('Tried to enable {} which is not a valid archive name'.format(archive_type))


def is_archive_enabled(archive_type):
    if archive_type in all_archivers:
        return all_archivers[archive_type].enabled
    logger.error("Tried to determine if {} is enabled but doesn't exist".format(archive_type))
    return False


def set_all_archivers_enabled(enable=True):
    for archiver in all_archivers.values():
        if archiver.enabled != enable:
            if enable:
                if archiver._enable_on_all_enable:
                    pass
                archiver.archive_enable_fn(enableLog=enable)


def clear_archive_records(archive_type, sim_id=None):
    if archive_type in all_archivers:
        all_archivers[archive_type].clear_archive(sim_id=sim_id)
    else:
        logger.error('Trying to clear all archive entries from {} which is not a valid archive type.'.format(archive_type))


class BaseArchiver:
    __slots__ = ('_type_name', '_custom_enable_fn', '_archive_enabled', '_enable_on_all_enable',
                 '__weakref__')

    def __init__(self, type_name=None, enable_archive_by_default=False, add_to_archive_enable_functions=False, custom_enable_fn=None):
        self._type_name = type_name
        self._custom_enable_fn = custom_enable_fn
        self._enable_on_all_enable = add_to_archive_enable_functions
        self._archive_enabled = False
        all_archivers[type_name] = self

    @property
    def enabled(self):
        return self._archive_enabled

    def archive_enable_fn(self, *args, enableLog=False, **kwargs):
        self._archive_enabled = enableLog
        if self._custom_enable_fn is not None:
            (self._custom_enable_fn)(args, enableLog=enableLog, **kwargs)
        return '{{"log_enabled":{}}}'.format('true' if enableLog else 'false')

    def clear_archive(self, sim_id=None):
        pass


class Archiver(BaseArchiver):
    __slots__ = ('_sim_specific', '_max_records')

    def __init__(self, type_name=None, schema=None, max_records=None, enable_archive_by_default=False, add_to_archive_enable_functions=False, custom_enable_fn=None):
        super().__init__(type_name=type_name, enable_archive_by_default=enable_archive_by_default,
          add_to_archive_enable_functions=add_to_archive_enable_functions,
          custom_enable_fn=custom_enable_fn)
        self._sim_specific = schema.is_sim_specific
        self._max_records = max_records
        sims4.gsi.dispatcher.add_handler('{}{}'.format(type_name, sims4.gsi.dispatcher.ARCHIVE_TOGGLE_SUFFIX), None, lambda *args, **kwargs: (self.archive_enable_fn)(*args, **kwargs)
)
        register_archive_type(type_name, schema,
          partition_by_obj=(self._sim_specific))

    def clear_archive(self, sim_id=None):
        if self._sim_specific:
            if sim_id is not None:
                del archive_data[self._type_name][sim_id]
                archive_data[self._type_name][sim_id] = []
            else:
                logger.error('No Sim Id provided when trying to clear a sim specific archive.')
        else:
            del archive_data[self._type_name]
            archive_data[self._type_name] = []

    def dump_to_csv(self, name: str, connection=None):
        if self._sim_specific:
            logger.error('CSV dump for Sim-specific archives is not yet supported.')
            return
        records = archive_data[self._type_name]
        raw_json = '[{}]'.format(','.join((zlib.decompress(record.compressed_json).decode('utf-8') for record in records)))
        data = json.loads(raw_json)

        def callback(file):
            header = True
            for record in data:
                if header:
                    for key in record.keys():
                        file.write(key + ',')

                    file.write('\n')
                    header = False
                else:
                    for value in record.values():
                        file.write(str(value) + ',')

                    file.write('\n')

        create_csv(name, callback, connection)

    def archive(self, data=None, object_id=None, game_time=None, zone_override=None):
        if zone_override is not None:
            zone_id = zone_override
        else:
            zone_id = sims4.zone_utils.zone_id
            if not zone_id:
                logger.error('Archiving data to zone 0. This data will be inaccessible to the GSI.')
                zone_id = 0
        now = int(time.time())
        record = ArchiveRecord(zone_id=zone_id, object_id=object_id, timestamp=now, game_time=game_time, data=data)
        if self._sim_specific:
            if object_id is None:
                logger.error('Archiving data to a sim_specific archive with no object ID. This data will be inaccessible to the GSI.')
            archive_list = archive_data[self._type_name].get(object_id)
            if archive_list is None:
                archive_list = []
                archive_data[self._type_name][object_id] = archive_list
        else:
            archive_list = archive_data[self._type_name]
        archive_list.append(record)
        num_max_records = ARCHIVE_MAX_RECORDS
        if self._max_records is not None:
            if num_max_records < self._max_records:
                num_max_records = self._max_records
        num_records = len(archive_list)
        if num_records > num_max_records:
            diff = num_records - num_max_records
            while diff > 0:
                del archive_list[0]
                diff -= 1


class ArchiveRecord:
    __slots__ = ('zone_id', 'object_id', 'timestamp', 'uid', 'compressed_json')

    def __init__(self, zone_id=None, object_id=None, timestamp=None, game_time=None, data=None):
        self.zone_id = zone_id
        self.object_id = object_id
        self.timestamp = timestamp
        self.uid = archive_id()
        full_dict = {'zone_id':hex(zone_id), 
         'object_id':hex(object_id) if object_id is not None else 'None', 
         'timestamp':timestamp, 
         'game_time':game_time, 
         'uid':self.uid}
        for key, field in data.items():
            full_dict[key] = field

        uncompressed_json = json.dumps(full_dict)
        self.compressed_json = zlib.compress(uncompressed_json.encode())


def register_archive_type(type_name, schema, partition_by_obj=False):
    if isinstance(schema, GsiSchema):
        schema = schema.output
    if type_name in archive_schemas:
        logger.error('Replacing archive type for {}.', type_name)
        del archive_schemas[type_name]
    path = type_name.strip('/')
    new_archive = archive_data.get(type_name)
    if new_archive is None:
        if partition_by_obj:
            new_archive = {}
        else:
            new_archive = []
        archive_data[type_name] = new_archive
    actual_schema = {'archive':True, 
     'perf_toggle':True, 
     'unique_field':'uid', 
     'definition':[
      {
        'name': 'zone_id', 'type': 'string', 'label': 'Zone', 'hidden': True},
      {
        'name': 'object_id', 'type': 'string', 'label': 'Object ID', 'hidden': True},
      {
        'name': 'timestamp', 'type': 'int', 'label': 'Time', 'is_time': True, 'axis': 'xField', 'sort_field': 'uid'},
      {
        'name': 'game_time', 'type': 'string', 'label': 'Game Time', 'hidden': True},
      {
        'name': 'uid', 'type': 'int', 'label': 'UId', 'hidden': True}]}
    for key, entry in schema.items():
        if key == 'definition':
            for definition_entry in entry:
                actual_schema['definition'].append(definition_entry)

        else:
            actual_schema[key] = entry

    for key, value in schema.items():
        if key not in ('definition', 'associations'):
            actual_schema[key] = value

    archive_schemas[type_name] = actual_schema

    def archive_handler--- This code section failed: ---

 L. 353         0  LOAD_FAST                'object_id'
                2  LOAD_CONST               None
                4  COMPARE_OP               is
                6  POP_JUMP_IF_FALSE    20  'to 20'
                8  LOAD_FAST                'sim_id'
               10  LOAD_CONST               None
               12  COMPARE_OP               is-not
               14  POP_JUMP_IF_FALSE    20  'to 20'

 L. 354        16  LOAD_FAST                'sim_id'
               18  STORE_FAST               'object_id'
             20_0  COME_FROM            14  '14'
             20_1  COME_FROM             6  '6'

 L. 356        20  LOAD_DEREF               'partition_by_obj'
               22  POP_JUMP_IF_FALSE    52  'to 52'

 L. 358        24  LOAD_GLOBAL              archive_data
               26  LOAD_DEREF               'type_name'
               28  BINARY_SUBSCR    
               30  LOAD_METHOD              get
               32  LOAD_FAST                'object_id'
               34  CALL_METHOD_1         1  '1 positional argument'
               36  STORE_FAST               'archive_data_list'

 L. 359        38  LOAD_FAST                'archive_data_list'
               40  LOAD_CONST               None
               42  COMPARE_OP               is
               44  POP_JUMP_IF_FALSE    60  'to 60'

 L. 361        46  LOAD_STR                 '[]'
               48  RETURN_VALUE     
               50  JUMP_FORWARD         60  'to 60'
             52_0  COME_FROM            22  '22'

 L. 364        52  LOAD_GLOBAL              archive_data
               54  LOAD_DEREF               'type_name'
               56  BINARY_SUBSCR    
               58  STORE_FAST               'archive_data_list'
             60_0  COME_FROM            50  '50'
             60_1  COME_FROM            44  '44'

 L. 366        60  LOAD_STR                 '[]'
               62  STORE_FAST               'json_output'

 L. 367        64  SETUP_EXCEPT        232  'to 232'

 L. 368        66  BUILD_LIST_0          0 
               68  STORE_FAST               'record_data'

 L. 369        70  SETUP_LOOP          192  'to 192'
               72  LOAD_FAST                'archive_data_list'
               74  GET_ITER         
             76_0  COME_FROM           188  '188'
             76_1  COME_FROM           174  '174'
             76_2  COME_FROM           152  '152'
             76_3  COME_FROM           118  '118'
             76_4  COME_FROM            98  '98'
               76  FOR_ITER            190  'to 190'
               78  STORE_FAST               'record'

 L. 370        80  LOAD_FAST                'zone_id'
               82  LOAD_CONST               None
               84  COMPARE_OP               is-not
               86  POP_JUMP_IF_FALSE   100  'to 100'

 L. 371        88  LOAD_FAST                'zone_id'
               90  LOAD_FAST                'record'
               92  LOAD_ATTR                zone_id
               94  COMPARE_OP               !=
               96  POP_JUMP_IF_FALSE   100  'to 100'

 L. 372        98  CONTINUE             76  'to 76'
            100_0  COME_FROM            96  '96'
            100_1  COME_FROM            86  '86'

 L. 373       100  LOAD_FAST                'object_id'
              102  LOAD_CONST               None
              104  COMPARE_OP               is-not
              106  POP_JUMP_IF_FALSE   120  'to 120'

 L. 374       108  LOAD_FAST                'object_id'
              110  LOAD_FAST                'record'
              112  LOAD_ATTR                object_id
              114  COMPARE_OP               !=
              116  POP_JUMP_IF_FALSE   120  'to 120'

 L. 375       118  CONTINUE             76  'to 76'
            120_0  COME_FROM           116  '116'
            120_1  COME_FROM           106  '106'

 L. 376       120  LOAD_GLOBAL              sims4
              122  LOAD_ATTR                gsi
              124  LOAD_ATTR                dispatcher
              126  LOAD_ATTR                gsi_client_version
              128  LOAD_GLOBAL              CLIENT_GSI_ARCHIVE_UID_FIX
              130  COMPARE_OP               <
              132  POP_JUMP_IF_FALSE   156  'to 156'

 L. 377       134  LOAD_FAST                'timestamp'
              136  LOAD_CONST               None
              138  COMPARE_OP               is-not
              140  POP_JUMP_IF_FALSE   176  'to 176'

 L. 380       142  LOAD_FAST                'timestamp'
              144  LOAD_FAST                'record'
              146  LOAD_ATTR                timestamp
              148  COMPARE_OP               >=
              150  POP_JUMP_IF_FALSE   176  'to 176'

 L. 381       152  CONTINUE             76  'to 76'
              154  JUMP_FORWARD        176  'to 176'
            156_0  COME_FROM           132  '132'

 L. 383       156  LOAD_FAST                'uid'
              158  LOAD_CONST               None
              160  COMPARE_OP               is-not
              162  POP_JUMP_IF_FALSE   176  'to 176'

 L. 386       164  LOAD_FAST                'uid'
              166  LOAD_FAST                'record'
              168  LOAD_ATTR                uid
              170  COMPARE_OP               >=
              172  POP_JUMP_IF_FALSE   176  'to 176'

 L. 387       174  CONTINUE             76  'to 76'
            176_0  COME_FROM           172  '172'
            176_1  COME_FROM           162  '162'
            176_2  COME_FROM           154  '154'
            176_3  COME_FROM           150  '150'
            176_4  COME_FROM           140  '140'

 L. 389       176  LOAD_FAST                'record_data'
              178  LOAD_METHOD              append
              180  LOAD_FAST                'record'
              182  LOAD_ATTR                compressed_json
              184  CALL_METHOD_1         1  '1 positional argument'
              186  POP_TOP          
              188  JUMP_LOOP            76  'to 76'
              190  POP_BLOCK        
            192_0  COME_FROM_LOOP       70  '70'

 L. 391       192  LOAD_FAST                'uncompress'
              194  POP_JUMP_IF_FALSE   224  'to 224'

 L. 392       196  LOAD_STR                 '[{}]'
              198  LOAD_METHOD              format
              200  LOAD_STR                 ','
              202  LOAD_METHOD              join
              204  LOAD_GENEXPR             '<code_object <genexpr>>'
              206  LOAD_STR                 'register_archive_type.<locals>.archive_handler.<locals>.<genexpr>'
              208  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
              210  LOAD_FAST                'record_data'
              212  GET_ITER         
              214  CALL_FUNCTION_1       1  '1 positional argument'
              216  CALL_METHOD_1         1  '1 positional argument'
              218  CALL_METHOD_1         1  '1 positional argument'
              220  STORE_FAST               'json_output'
              222  JUMP_FORWARD        228  'to 228'
            224_0  COME_FROM           194  '194'

 L. 394       224  LOAD_FAST                'record_data'
              226  RETURN_VALUE     
            228_0  COME_FROM           222  '222'
              228  POP_BLOCK        
              230  JUMP_FORWARD        276  'to 276'
            232_0  COME_FROM_EXCEPT     64  '64'

 L. 396       232  DUP_TOP          
              234  LOAD_GLOBAL              MemoryError
              236  COMPARE_OP               exception-match
          238_240  POP_JUMP_IF_FALSE   274  'to 274'
              242  POP_TOP          
              244  POP_TOP          
              246  POP_TOP          

 L. 397       248  LOAD_GLOBAL              logger
              250  LOAD_METHOD              error
              252  LOAD_STR                 'Archive Data[{}] has too many entries: {}'
              254  LOAD_DEREF               'type_name'
              256  LOAD_GLOBAL              len
              258  LOAD_FAST                'archive_data_list'
              260  CALL_FUNCTION_1       1  '1 positional argument'
              262  CALL_METHOD_3         3  '3 positional arguments'
              264  POP_TOP          

 L. 398       266  LOAD_STR                 '[]'
              268  STORE_FAST               'json_output'
              270  POP_EXCEPT       
              272  JUMP_FORWARD        276  'to 276'
            274_0  COME_FROM           238  '238'
              274  END_FINALLY      
            276_0  COME_FROM           272  '272'
            276_1  COME_FROM           230  '230'

 L. 400       276  LOAD_FAST                'json_output'
              278  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `JUMP_LOOP' instruction at offset 188

    sims4.gsi.dispatcher.GsiHandler(path, actual_schema, suppress_json=True)(archive_handler)