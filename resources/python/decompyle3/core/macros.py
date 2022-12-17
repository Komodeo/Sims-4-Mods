# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\macros.py
# Compiled at: 2014-12-19 15:21:36
# Size of source mod 2**32: 56237 bytes
import ast, collections, contextlib, copy, imp, os, sys, types, graph_algos
__all__ = [
 'macro', 'load_module']
__unittest__ = ['test.macros_test']
MACRO_SYMBOL = 'macro'

def macro(obj):
    if isinstance(obj, types.FunctionType):
        return obj
    if isinstance(obj, type):
        return obj
    raise RuntimeError('Macros can only be applied to functions and classes.')


def _expand_attribute(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Call):
        return '{}()'.format(_expand_attribute(node.func))
    if isinstance(node, ast.Attribute):
        return '{}.{}'.format(_expand_attribute(node.value), node.attr)
    if isinstance(node, ast.Str):
        return 'str'
    return '<other>'


def _is_macro(node, macros):
    if node.decorator_list:
        if len(node.decorator_list) == 1:
            name = node.decorator_list[0]
            if isinstance(name, ast.Call):
                name = name.func
            name_str = _expand_attribute(name)
            symbol = macros.get(name_str)
            return symbol == MACRO_SYMBOL
    return False


def _get_body(node):
    if len(node.body) >= 1:
        doc = node.body[0]
        if isinstance(doc, ast.Expr):
            if isinstance(doc.value, ast.Str):
                return (
                 doc.value.s, node.body[1:])
    return (
     None, node.body)


def _ast_dump_pp(tree, annotate_fields=True, include_attributes=False):
    if isinstance(tree, list):
        result = '[{}]'.format(', '.join([_ast_dump_pp(node, annotate_fields=annotate_fields, include_attributes=include_attributes) for node in tree]))
        return result
    s = ast.dump(tree, annotate_fields=annotate_fields, include_attributes=include_attributes)
    result = ''
    indent = 0
    for c in s:
        result += c
        if c in '([':
            indent = indent + 1
            result += '\n' + '    ' * indent
        if c in ')]':
            indent = indent - 1
            result += '\n' + '    ' * indent

    return result


def _fix_all_locations(node, lineno, col_offset):
    if 'lineno' in node._attributes:
        node.lineno = lineno
    if 'col_offset' in node._attributes:
        node.col_offset = col_offset
    for child in ast.iter_child_nodes(node):
        _fix_all_locations(child, lineno, col_offset)

    return node


def _get_parameter_mapping(macro_name, parameters, call, skip=()):
    for i, expected in enumerate(skip):
        if parameters.args[i].arg != expected:
            raise TypeError("Expected argument '{}' rather than '{}'".format(expected, parameters.args[i].arg))

    num_skip = len(skip)
    num_defaults = len(parameters.defaults)
    allowed = {param.arg for param in parameters.args[num_skip:]}
    required = {param.arg for param in parameters.args[num_skip:-num_defaults]}
    given = set()
    mapping = {name.arg: value for name, value in zip(parameters.args[-num_defaults:], parameters.defaults)}
    for kw, value in zip(parameters.kwonlyargs, parameters.kw_defaults):
        if value is not None:
            mapping[kw.arg] = value
        else:
            required.add(kw.arg)
        allowed.add(kw.arg)

    for i, arg in enumerate(call.args, num_skip):
        param = parameters.args[i]
        _add_arg(param.arg, arg, macro_name, mapping, given, required, allowed)

    for kwarg in call.keywords:
        _add_arg(kwarg.arg, kwarg.value, macro_name, mapping, given, required, allowed)

    if len(required) > 0:
        raise TypeError("Macro '{}' missing required arguments: {}".format(macro_name, required))
    return mapping


def _add_arg(name, value, macro_name, mapping, given, required, allowed):
    if name in given:
        raise TypeError("Macro '{}' got multiple values for argument '{}'".format(macro_name, name))
    if name not in allowed:
        raise TypeError("Macro '{}' got an unexpected keyword argument '{}'".format(macro_name, name))
    given.add(name)
    required.discard(name)
    mapping[name] = value


class MacroBase:

    def __init__(self, node, from_module):
        self.name = sys.intern(node.name)
        self.node = node
        self.from_module = from_module
        self.__doc__, self.body = _get_body(node)

    def full_name(self):
        return self.name

    def __repr__(self):
        return "<{}('{}'>)".format(type(self).__name__, self.full_name())

    def __str__(self):
        if self.__doc__ is not None:
            return '<{}(\'{}\', """{}""")>'.format(type(self).__name__, self.full_name(), self.__doc__)
        return "<{}('{}')>".format(type(self).__name__, self.full_name())


class FunctionMacro(MacroBase):

    def __init__(self, node, from_module):
        MacroBase.__init__(self, node, from_module)
        if len(self.body) == 1 and isinstance(self.body[0], ast.Return):
            self.body = self.body[0].value
            self.is_expr = True
        else:
            self.is_expr = False

    def get_base_mapping(self):
        return {}

    def get_skip_args(self):
        return ()

    def apply(self, call, statement_context):
        if not statement_context:
            if not self.is_expr:
                raise RuntimeError('Attempting to apply non-expression macro {} in an expression context'.format(self.full_name()))
            mapping = self.get_base_mapping()
            argument_mapping = _get_parameter_mapping((self.name), (self.node.args), call, skip=(self.get_skip_args()))
            mapping.update(argument_mapping)
            new_tree = copy.deepcopy(self.body)
            transformer = MacroTransformer(mapping)
            if isinstance(new_tree, list):
                new_tree = ast.Expression(new_tree)
                extract_body = True
            else:
                extract_body = False
            transformer.visit(new_tree)
            if statement_context:
                if self.is_expr:
                    new_tree = ast.Expr(new_tree)
            result = _fix_all_locations(new_tree, call.lineno, call.col_offset)
            if extract_body:
                result = result.body
            return result


class InstanceMacro(FunctionMacro):

    def __init__(self, node, from_module, base, base_mapping):
        FunctionMacro.__init__(self, node, from_module)
        self.base = base
        self.base_mapping = base_mapping

    def full_name(self):
        return '{}.{}'.format(self.base, self.name)

    def get_base_mapping(self):
        return dict(self.base_mapping)

    def get_skip_args(self):
        return ('self', )


class ClassMacro(MacroBase):

    def __init__(self, node, from_module):
        MacroBase.__init__(self, node, from_module)
        self._macros = collections.ChainMap()
        for child in self.body:
            if isinstance(child, ast.FunctionDef):
                self._macros[child.name] = FunctionMacro(child, self.from_module)
            else:
                raise RuntimeError('Class macro {} contains non-function statement {}'.format(node.name, child))

        if '__init__' not in self._macros:
            raise RuntimeError('Class macro {} does not have an __init__ method'.format(node.name))
        self._init = self._macros.pop('__init__')

    def get_init_mapping(self, node):
        init_args = self._init.node.args.args
        argument_mapping = _get_parameter_mapping((self.name), (self._init.node.args), (node.value), skip=('self', ))
        mapping = {}
        for statement in self._init.body:
            if isinstance(statement, ast.Pass):
                continue
            else:
                if not isinstance(statement, ast.Assign):
                    raise TypeError('Class macro __init__ must only contain assignments, not {}'.format(type(statement)))
                if len(statement.targets) != 1:
                    raise TypeError('Class macro __init__ assignments may only have one target, not {}'.format(len(statement.targets)))
                target = statement.targets[0]
            if isinstance(target, ast.Attribute):
                if not isinstance(target.value, ast.Name) or target.value.id != 'self':
                    raise TypeError('Class macro __init__ body may only assign to self')
                else:
                    dest = '{}.{}'.format(target.value.id, target.attr)
                    if not isinstance(statement.value, ast.Name):
                        raise TypeError('Class macro __init__ body may only assign from arguments')
                    source = statement.value.id
                    if source not in argument_mapping:
                        raise TypeError("Class macro __init__ assignment source '{}' not found in arguments".format(source))
                    mapping[dest] = argument_mapping[source]

        return mapping

    def instantiate(self, node, from_module):
        name_str = _expand_attribute(node.targets[0])
        mapping = self.get_init_mapping(node)
        instance_macros = [InstanceMacro(m.node, from_module, name_str, mapping) for m in self._macros.values()]
        return {m.full_name(): m for m in instance_macros}


class MacroTransformer(ast.NodeTransformer):

    def __init__(self, mapping):
        self.mapping = mapping

    def visit_Name(self, node):
        return self._visit_symbol(node.id, node)

    def visit_Attribute(self, node):
        name = _expand_attribute(node)
        return self._visit_symbol(name, node)

    def _visit_symbol(self, name, node):
        replacement = self.mapping.get(name)
        if replacement is None:
            return node
        return copy.deepcopy(replacement)


class MacroVisitor(ast.NodeVisitor):

    def __init__(self, library, fullname, constants=None):
        self._library = library
        self._fullname = fullname
        self.constants = constants or {}
        self._macros = collections.ChainMap()

    def generic_visit(self, node):
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                if value and isinstance(value[0], ast.AST):
                    self._visit_block(value)
                else:
                    if isinstance(value, ast.AST):
                        new_node = self.visit(value)
                        if new_node is not node:
                            setattr(node, field, new_node)

        return node

    def get_macros(self):
        return dict(self._macros.items())

    def visit_Module(self, node):
        self._visit_block(node.body)
        return node

    def _visit_block(self, nodes):
        first_statement = nodes[0] if len(nodes) > 0 else None
        imports = {}
        n = len(nodes)
        i = 0
        while i < n:
            statement = nodes[i]
            if isinstance(statement, ast.FunctionDef):
                new_statement = self.visit_FunctionDef(statement)
            else:
                if isinstance(statement, ast.ClassDef):
                    new_statement = self.visit_ClassDef(statement)
                else:
                    if isinstance(statement, ast.Assign):
                        new_statement = self.visit_Assign(statement)
                    else:
                        if isinstance(statement, (ast.Import, ast.ImportFrom)):
                            if _append_node_imports(statement, imports):
                                new_statement = self._handle_import(statement, imports)
                                imports.clear()
                            else:
                                new_statement = statement
                        else:
                            new_statement = self.visit(statement)
            if new_statement is statement:
                i += 1
            else:
                if isinstance(new_statement, list):
                    nodes[i:i + 1] = new_statement
                    delta = len(new_statement)
                    i += delta
                    n += delta - 1
                else:
                    if new_statement is None:
                        del nodes[i]
                        n -= 1
                    else:
                        nodes[i] = new_statement
                        i += 1

        if not nodes:
            if first_statement is not None:
                pass_node = ast.copy_location(ast.Pass(), first_statement)
                nodes.append(pass_node)

    def _visit_block_wrapped(self, nodes):
        self._macros = self._macros.new_child()
        try:
            self._visit_block(nodes)
        finally:
            self._macros = self._macros.parents

    def visit_FunctionDef(self, node):
        if _is_macro(node, self._macros):
            macro_ = FunctionMacro(node, self._fullname)
            self._macros[macro_.name] = macro_
            replacement = ast.copy_location(ast.Pass(), node)
            return replacement
        self._visit_block_wrapped(node.body)
        return node

    def visit_ClassDef(self, node):
        if _is_macro(node, self._macros):
            macro_ = ClassMacro(node, self._fullname)
            self._macros[macro_.name] = macro_
            replacement = ast.copy_location(ast.Pass(), node)
            return replacement
        self._visit_block_wrapped(node.body)
        return node

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Call):
            self.generic_visit(node.value)
            return self._handle_possible_macro(node.value, node, True)
        return self.generic_visit(node)

    def visit_Call(self, node):
        self.generic_visit(node)
        return self._handle_possible_macro(node, node, False)

    def visit_Assign(self, node):
        call = node.value
        if isinstance(call, ast.Call):
            if isinstance(call.func, (ast.Name, ast.Attribute)):
                name_str = _expand_attribute(call.func)
                m = self._macros.get(name_str)
                if m is not None:
                    if m != MACRO_SYMBOL:
                        if isinstance(m, ClassMacro):
                            instance_macros = m.instantiate(node, self._fullname)
                            self._macros.update(instance_macros)
                            return
        return node

    def visit_If(self, node):
        if isinstance(node.test, ast.Name):
            if node.test.id in self.constants:
                value = self.constants[node.test.id]
                if value:
                    self._visit_block(node.body)
                    return node.body
                self._visit_block(node.orelse)
                return node.orelse
        return self.generic_visit(node)

    def _handle_possible_macro(self, call, node, statement_context: bool):
        if isinstance(call.func, (ast.Name, ast.Attribute)):
            name_str = _expand_attribute(call.func)
            m = self._macros.get(name_str)
            if m is not None:
                if m != MACRO_SYMBOL:
                    return m.apply(call, statement_context)
        return node

    def _handle_import--- This code section failed: ---

 L. 717       0_2  SETUP_LOOP          484  'to 484'
                4  LOAD_FAST                'imports'
                6  LOAD_METHOD              items
                8  CALL_METHOD_0         0  '0 positional arguments'
               10  GET_ITER         
             12_0  COME_FROM           480  '480'
             12_1  COME_FROM           474  '474'
             12_2  COME_FROM           390  '390'
             12_3  COME_FROM           120  '120'
             12_4  COME_FROM           104  '104'
             12_5  COME_FROM            32  '32'
            12_14  FOR_ITER            482  'to 482'
               16  UNPACK_SEQUENCE_2     2 
               18  UNPACK_SEQUENCE_2     2 
               20  STORE_FAST               'name'
               22  STORE_FAST               'level'
               24  STORE_FAST               'v'

 L. 719        26  LOAD_FAST                'level'
               28  LOAD_CONST               0
               30  COMPARE_OP               ==
               32  POP_JUMP_IF_FALSE_LOOP    12  'to 12'

 L. 720        34  LOAD_FAST                'name'
               36  LOAD_STR                 'macros'
               38  COMPARE_OP               ==
               40  POP_JUMP_IF_FALSE   106  'to 106'

 L. 722        42  SETUP_LOOP          104  'to 104'
               44  LOAD_FAST                'v'
               46  GET_ITER         
             48_0  COME_FROM           100  '100'
             48_1  COME_FROM            88  '88'
             48_2  COME_FROM            80  '80'
               48  FOR_ITER            102  'to 102'
               50  UNPACK_SEQUENCE_2     2 
               52  STORE_FAST               'symbol'
               54  STORE_FAST               'asname'

 L. 723        56  LOAD_FAST                'symbol'
               58  LOAD_STR                 '.'
               60  COMPARE_OP               ==
               62  POP_JUMP_IF_FALSE    82  'to 82'

 L. 724        64  LOAD_GLOBAL              MACRO_SYMBOL
               66  LOAD_FAST                'self'
               68  LOAD_ATTR                _macros
               70  LOAD_STR                 '{}.macro'
               72  LOAD_METHOD              format
               74  LOAD_FAST                'asname'
               76  CALL_METHOD_1         1  '1 positional argument'
               78  STORE_SUBSCR     
               80  JUMP_LOOP            48  'to 48'
             82_0  COME_FROM            62  '62'

 L. 725        82  LOAD_FAST                'symbol'
               84  LOAD_STR                 'macro'
               86  COMPARE_OP               ==
               88  POP_JUMP_IF_FALSE_LOOP    48  'to 48'

 L. 726        90  LOAD_GLOBAL              MACRO_SYMBOL
               92  LOAD_FAST                'self'
               94  LOAD_ATTR                _macros
               96  LOAD_FAST                'asname'
               98  STORE_SUBSCR     
              100  JUMP_LOOP            48  'to 48'
              102  POP_BLOCK        
            104_0  COME_FROM_LOOP       42  '42'
              104  JUMP_LOOP            12  'to 12'
            106_0  COME_FROM            40  '40'

 L. 729       106  LOAD_FAST                'self'
              108  LOAD_ATTR                _library
              110  LOAD_METHOD              get_macros
              112  LOAD_FAST                'name'
              114  CALL_METHOD_1         1  '1 positional argument'
              116  STORE_FAST               'import_macros'

 L. 731       118  LOAD_FAST                'import_macros'
              120  POP_JUMP_IF_FALSE_LOOP    12  'to 12'

 L. 733       122  LOAD_GLOBAL              set
              124  CALL_FUNCTION_0       0  '0 positional arguments'
              126  STORE_FAST               'to_delete'

 L. 734   128_130  SETUP_LOOP          388  'to 388'
              132  LOAD_FAST                'v'
              134  GET_ITER         
            136_0  COME_FROM           384  '384'
            136_1  COME_FROM           280  '280'
            136_2  COME_FROM           244  '244'
              136  FOR_ITER            386  'to 386'
              138  UNPACK_SEQUENCE_2     2 
              140  STORE_FAST               'symbol'
              142  STORE_FAST               'asname'

 L. 735       144  LOAD_FAST                'symbol'
              146  LOAD_STR                 '.'
              148  COMPARE_OP               ==
              150  POP_JUMP_IF_FALSE   246  'to 246'

 L. 738       152  SETUP_LOOP          384  'to 384'
              154  LOAD_FAST                'import_macros'
              156  LOAD_METHOD              items
              158  CALL_METHOD_0         0  '0 positional arguments'
              160  GET_ITER         
            162_0  COME_FROM           240  '240'
            162_1  COME_FROM           210  '210'
            162_2  COME_FROM           186  '186'
              162  FOR_ITER            242  'to 242'
              164  UNPACK_SEQUENCE_2     2 
              166  STORE_FAST               'macro_name'
              168  STORE_FAST               'macro_value'

 L. 745       170  LOAD_FAST                'macro_value'
              172  LOAD_GLOBAL              MACRO_SYMBOL
              174  COMPARE_OP               ==
              176  POP_JUMP_IF_FALSE   190  'to 190'

 L. 746       178  LOAD_FAST                'name'
              180  LOAD_STR                 'macro'
              182  COMPARE_OP               !=
              184  POP_JUMP_IF_FALSE   190  'to 190'

 L. 747       186  CONTINUE            162  'to 162'
              188  JUMP_FORWARD        212  'to 212'
            190_0  COME_FROM           184  '184'
            190_1  COME_FROM           176  '176'

 L. 748       190  LOAD_GLOBAL              isinstance
              192  LOAD_FAST                'macro_value'
              194  LOAD_GLOBAL              MacroBase
              196  CALL_FUNCTION_2       2  '2 positional arguments'
              198  POP_JUMP_IF_FALSE   212  'to 212'

 L. 749       200  LOAD_FAST                'name'
              202  LOAD_FAST                'macro_value'
              204  LOAD_ATTR                from_module
              206  COMPARE_OP               !=
              208  POP_JUMP_IF_FALSE   212  'to 212'

 L. 750       210  CONTINUE            162  'to 162'
            212_0  COME_FROM           208  '208'
            212_1  COME_FROM           198  '198'
            212_2  COME_FROM           188  '188'

 L. 752       212  LOAD_GLOBAL              sys
              214  LOAD_METHOD              intern
              216  LOAD_STR                 '{}.{}'
              218  LOAD_METHOD              format
              220  LOAD_FAST                'name'
              222  LOAD_FAST                'macro_name'
              224  CALL_METHOD_2         2  '2 positional arguments'
              226  CALL_METHOD_1         1  '1 positional argument'
              228  STORE_FAST               'full_name'

 L. 754       230  LOAD_FAST                'macro_value'
              232  LOAD_FAST                'self'
              234  LOAD_ATTR                _macros
              236  LOAD_FAST                'full_name'
              238  STORE_SUBSCR     
              240  JUMP_LOOP           162  'to 162'
              242  POP_BLOCK        
              244  JUMP_LOOP           136  'to 136'
            246_0  COME_FROM           150  '150'

 L. 758       246  LOAD_FAST                'symbol'
              248  LOAD_FAST                'import_macros'
              250  COMPARE_OP               in
          252_254  POP_JUMP_IF_FALSE   282  'to 282'

 L. 760       256  LOAD_FAST                'import_macros'
              258  LOAD_FAST                'symbol'
              260  BINARY_SUBSCR    
              262  LOAD_FAST                'self'
              264  LOAD_ATTR                _macros
              266  LOAD_FAST                'asname'
              268  STORE_SUBSCR     

 L. 761       270  LOAD_FAST                'to_delete'
              272  LOAD_METHOD              add
              274  LOAD_FAST                'symbol'
              276  CALL_METHOD_1         1  '1 positional argument'
              278  POP_TOP          
              280  JUMP_LOOP           136  'to 136'
            282_0  COME_FROM           252  '252'

 L. 765       282  LOAD_FAST                'symbol'
              284  LOAD_STR                 '.'
              286  BINARY_ADD       
              288  STORE_FAST               'prefix'

 L. 766       290  LOAD_GLOBAL              len
              292  LOAD_FAST                'prefix'
              294  CALL_FUNCTION_1       1  '1 positional argument'
              296  STORE_FAST               'prefix_len'

 L. 767       298  SETUP_LOOP          384  'to 384'
              300  LOAD_FAST                'import_macros'
              302  LOAD_METHOD              items
              304  CALL_METHOD_0         0  '0 positional arguments'
              306  GET_ITER         
            308_0  COME_FROM           378  '378'
            308_1  COME_FROM           324  '324'
              308  FOR_ITER            382  'to 382'
              310  UNPACK_SEQUENCE_2     2 
              312  STORE_FAST               'macro_name'
              314  STORE_FAST               'macro_value'

 L. 768       316  LOAD_FAST                'macro_name'
              318  LOAD_METHOD              startswith
              320  LOAD_FAST                'prefix'
              322  CALL_METHOD_1         1  '1 positional argument'
          324_326  POP_JUMP_IF_FALSE_LOOP   308  'to 308'

 L. 769       328  LOAD_FAST                'macro_name'
              330  LOAD_FAST                'prefix_len'
              332  LOAD_CONST               None
              334  BUILD_SLICE_2         2 
              336  BINARY_SUBSCR    
              338  STORE_FAST               'remainder'

 L. 770       340  LOAD_GLOBAL              sys
              342  LOAD_METHOD              intern
              344  LOAD_STR                 '{}.{}'
              346  LOAD_METHOD              format
              348  LOAD_FAST                'asname'
              350  LOAD_FAST                'remainder'
              352  CALL_METHOD_2         2  '2 positional arguments'
              354  CALL_METHOD_1         1  '1 positional argument'
              356  STORE_FAST               'new_symbol'

 L. 772       358  LOAD_FAST                'macro_value'
              360  LOAD_FAST                'self'
              362  LOAD_ATTR                _macros
              364  LOAD_FAST                'new_symbol'
              366  STORE_SUBSCR     

 L. 773       368  LOAD_FAST                'to_delete'
              370  LOAD_METHOD              add
              372  LOAD_FAST                'symbol'
              374  CALL_METHOD_1         1  '1 positional argument'
              376  POP_TOP          
          378_380  JUMP_LOOP           308  'to 308'
              382  POP_BLOCK        
            384_0  COME_FROM_LOOP      298  '298'
            384_1  COME_FROM_LOOP      152  '152'
              384  JUMP_LOOP           136  'to 136'
              386  POP_BLOCK        
            388_0  COME_FROM_LOOP      128  '128'

 L. 775       388  LOAD_FAST                'to_delete'
              390  POP_JUMP_IF_FALSE_LOOP    12  'to 12'

 L. 781       392  LOAD_FAST                'statement'
              394  LOAD_ATTR                names
              396  STORE_FAST               'names'

 L. 782       398  LOAD_CONST               0
              400  STORE_FAST               'i'

 L. 783       402  LOAD_GLOBAL              len
              404  LOAD_FAST                'names'
              406  CALL_FUNCTION_1       1  '1 positional argument'
              408  STORE_FAST               'n'

 L. 784       410  SETUP_LOOP          472  'to 472'
            412_0  COME_FROM           466  '466'
            412_1  COME_FROM           456  '456'
              412  LOAD_FAST                'i'
              414  LOAD_FAST                'n'
              416  COMPARE_OP               <
          418_420  POP_JUMP_IF_FALSE   470  'to 470'

 L. 785       422  LOAD_FAST                'names'
              424  LOAD_FAST                'i'
              426  BINARY_SUBSCR    
              428  STORE_FAST               'alias'

 L. 786       430  LOAD_FAST                'alias'
              432  LOAD_ATTR                name
              434  LOAD_FAST                'to_delete'
              436  COMPARE_OP               in
          438_440  POP_JUMP_IF_FALSE   458  'to 458'

 L. 787       442  LOAD_FAST                'names'
              444  LOAD_FAST                'i'
              446  DELETE_SUBSCR    

 L. 788       448  LOAD_FAST                'n'
              450  LOAD_CONST               1
              452  BINARY_SUBTRACT  
              454  STORE_FAST               'n'
              456  JUMP_LOOP           412  'to 412'
            458_0  COME_FROM           438  '438'

 L. 790       458  LOAD_FAST                'i'
              460  LOAD_CONST               1
              462  BINARY_ADD       
              464  STORE_FAST               'i'
          466_468  JUMP_LOOP           412  'to 412'
            470_0  COME_FROM           418  '418'
              470  POP_BLOCK        
            472_0  COME_FROM_LOOP      410  '410'

 L. 792       472  LOAD_FAST                'names'
              474  POP_JUMP_IF_TRUE_LOOP    12  'to 12'

 L. 793       476  LOAD_CONST               None
              478  RETURN_VALUE     
              480  JUMP_LOOP            12  'to 12'
              482  POP_BLOCK        
            484_0  COME_FROM_LOOP        0  '0'

 L. 794       484  LOAD_FAST                'statement'
              486  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `JUMP_LOOP' instruction at offset 240


def _append_node_imports(node, imports):
    if isinstance(node, ast.Import):
        for alias in node.names:
            key = (
             alias.name, 0)
            asname = alias.asname or alias.name
            value = ('.', asname)
            imports.setdefault(key, []).append(value)

        return True
    if isinstance(node, ast.ImportFrom):
        key = (
         node.module, node.level)
        for alias in node.names:
            asname = alias.asname or alias.name
            value = (alias.name, asname)
            imports.setdefault(key, []).append(value)

        return True
    return False


def _get_module_imports(tree):
    imports = {}
    for node in tree.body:
        _append_node_imports(node, imports)

    return imports


def _get_opt_level(opt):
    if isinstance(opt, int):
        return opt
    if opt is None:
        opt = True
    opt_level = 1 if opt else 0
    return opt_level


def _parse_module(name, source, opt_level):
    flags = ast.PyCF_ONLY_AST
    a = compile(source, name, 'exec', flags, 0, opt_level)
    return a


TreeVisitorPair = collections.namedtuple('TreeVisitorPair', ['tree', 'visitor'])
SubPackageRequest = collections.namedtuple('SubPackageRequest', ['path', 'children'])

class ModuleSuiteImporter:

    def __init__(self, opt=None, use_macros=True, private=False, constants=None):
        self.opt_level = _get_opt_level(opt)
        self.use_macros = use_macros
        self.private = private
        self.constants = constants
        self.meta_hook = 0
        self.new_modules = set()
        self.ast_cache = {}
        self.path_cache = {}

    def load(self, name, loader=None, path=None):
        if loader is None:
            loader = self.find_module(name, path=path)
            if loader is None:
                raise ImportError("Failed to find loader for module '{}'".format(name))
        module = self._get_cached_module(name)
        if module is not None:
            return module
        tree = self.load_ast(name, loader)
        module = self._exec_module(name, tree, loader)
        if module is None:
            raise ImportError("Failed to load module '{}'".format(name))
        if hasattr(loader, 'post_load'):
            loader.post_load(module)
        return module

    def load_ast(self, name, loader):
        if name in self.ast_cache:
            value = self.ast_cache[name]
            if value is None:
                raise RuntimeError("Partially loaded AST for '{}'".format(name))
            return value.tree
        self._do_load_ast(name, loader)
        if name in self.ast_cache:
            return self.ast_cache[name].tree
        raise ImportError("Failed to load AST for '{}'".format(name))

    def find_module(self, name, path=None):
        for hook in sys.meta_path:
            if isinstance(hook, ModuleSuiteImporter):
                continue
            else:
                loader = hook.find_module(name, path=path)
            if loader is not None:
                source = loader.get_source(name)
                if source is None:
                    return loader
                else:
                    return ModuleSuiteLoader(self, loader)

    def invalidate_caches(self):
        self.ast_cache.clear()
        self.path_cache.clear()

    def get_macros(self, name):
        m = self._get_cached_module(name)
        if m is not None:
            if hasattr(m, '__macros__'):
                return m.__macros__
            return
        if name in self.ast_cache:
            tvp = self.ast_cache[name]
            if tvp is not None:
                return tvp.visitor.get_macros()

    def _do_load_ast(self, fullname, loader):
        loaders = {fullname: loader}
        pending = list()
        while fullname:
            pending.append(fullname)
            fullname = fullname.rpartition('.')[0]

        imported = set()
        to_process = {}
        dependents = collections.defaultdict(set)
        order = ()
        try:
            while pending:
                fullname = pending.pop(-1)
                if fullname in imported:
                    continue
                else:
                    imported.add(fullname)
                if '.' in fullname:
                    parent = fullname.rpartition('.')[0]
                    parent_loader = loaders[parent]
                    if not hasattr(parent_loader, 'path'):
                        continue
                    else:
                        package_path = make_package_path(parent_loader.path)
                        module_loader = self.find_module(fullname, path=package_path)
                else:
                    module_loader = self.find_module(fullname)
                loaders[fullname] = module_loader
                if fullname in self.ast_cache:
                    continue
                else:
                    self.ast_cache[fullname] = None
                if module_loader is None:
                    continue
                else:
                    source = module_loader.get_source(fullname)
                if source is None:
                    continue
                else:
                    if hasattr(source, 'read'):
                        data = source.read()
                        source.close()
                    else:
                        data = source
                    tree = _parse_module(fullname, data, self.opt_level)
                    to_process[fullname] = tree
                    for imp_name, imp_level in _get_module_imports(tree):
                        import_name = self._resolve_relative(imp_name, fullname, imp_level)
                        while import_name:
                            if import_name not in imported:
                                pending.append(import_name)
                            else:
                                dependents[import_name].add(fullname)
                                import_name = import_name.rpartition('.')[0]

            relevant = set(to_process.keys())
            sccs = graph_algos.strongly_connected_components(relevant, dependents.get)
            order = []
            for scc in sccs:
                order.extend(sorted(scc))

            while order:
                fullname = order.pop()
                tree = to_process[fullname]
                visitor = MacroVisitor(self, fullname, constants=(self.constants))
                visitor.visit(tree)
                self.ast_cache[fullname] = TreeVisitorPair(tree, visitor)
                m = visitor.get_macros()
                if m:
                    existing = self._get_cached_module(fullname)
                    if existing is not None:
                        existing.__macros__ = m

        finally:
            for fullname in order:
                if fullname in self.ast_cache:
                    if self.ast_cache[fullname] is None:
                        del self.ast_cache[fullname]

    def _exec_module(self, name, tree, loader):
        module = self._get_cached_module(name)
        if module is None:
            is_reload = False
            module = imp.new_module(name)
            if loader.is_package(name):
                module.__path__ = make_package_path(loader.path)
                module.__package__ = name
            else:
                module.__package__ = name.rpartition('.')[0]
            module.__file__ = loader.get_filename(name)
            module.__loader__ = loader
        else:
            is_reload = True
        try:
            try:
                self._register_meta_path()
                if not is_reload:
                    self._cache_module(name, module)
                if self.constants:
                    vars(module).update(self.constants)
                visitor = self.ast_cache[name].visitor
                m = visitor.get_macros()
                if m:
                    module.__macros__ = m
                code = compile(tree, module.__file__, 'exec', 0, 0, self.opt_level)
                exec(code, vars(module))
            except:
                if not is_reload:
                    self._uncache_module(name)
                else:
                    raise

        finally:
            self._unregister_meta_path()

        return module

    def _resolve_relative(self, name, package=None, level=0):
        if package:
            if not hasattr(package, 'rindex'):
                raise ValueError('__package__ not set to a string')
            else:
                if package not in sys.modules:
                    if package not in self.ast_cache:
                        msg = 'Parent module {0!r} not loaded, cannot perform relative import'
                        raise SystemError(msg.format(package))
        if not name:
            if level == 0:
                raise ValueError('Empty module name')
        if level > 0:
            dot = len(package)
            for _ in range(level - 1):
                try:
                    dot = package.rindex('.', 0, dot)
                except ValueError:
                    raise ValueError('attempted relative import beyond top-level package')

            if name:
                name = '{0}.{1}'.format(package[:dot], name)
            else:
                name = package[:dot]
        return name

    def _cache_module(self, name, module):
        existing = sys.modules.get(name)
        if existing is not None:
module is not existingRuntimeError"Attempting to cache on top of an existing module '{}'".format(name)        else:
            self.new_modules.add(name)
            sys.modules[name] = module

    def _uncache_module(self, name):
        if name in self.new_modules:
            self.new_modules.remove(name)
            del sys.modules[name]

    def _is_module_cached(self, name):
        return name in sys.modules

    def _get_cached_module(self, name):
        return sys.modules.get(name)

    def _on_unregistered(self):
        if self.private:
            for name in self.new_modules:
                del sys.modules[name]

        self.new_modules.clear()

    def _register_meta_path(self):
        if self.meta_hook == 0:
            sys.meta_path.insert(0, self)
        self.meta_hook += 1

    def _unregister_meta_path(self):
        self.meta_hook -= 1
        if self.meta_hook == 0:
            sys.meta_path.remove(self)
            self._on_unregistered()

    @contextlib.contextmanager
    def installed(self):
        self._register_meta_path()
        try:
            yield
        finally:
            self._unregister_meta_path()


class ModuleSuiteLoader:

    def __init__(self, importer, loader):
        self.importer = importer
        self._loader = loader

    def load_module(self, name):
        return self.importer.load(name, self._loader)

    def post_load(self, module):
        if hasattr(self._loader, 'post_load'):
            self._loader.post_load(module)

    def is_package(self, fullname):
        return self._loader.is_package(fullname)

    def get_code(self, fullname):
        pass

    def get_source(self, fullname):
        return self._loader.get_source(fullname)

    def get_filename(self, fullname):
        return self._loader.get_filename(fullname)

    @property
    def path(self):
        return self._loader.path


def make_package_path(loader_path):
    loader_directory = os.path.dirname(loader_path)
    return [
     loader_directory]


def c_api_register_global_importer(opt=None, constants=None):
    importer = ModuleSuiteImporter(opt=opt, constants=constants)
    importer._register_meta_path()