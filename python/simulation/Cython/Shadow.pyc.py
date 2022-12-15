# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\Cython\Shadow.py
# Compiled at: 2020-02-21 17:47:46
# Size of source mod 2**32: 13551 bytes
from __future__ import absolute_import
__version__ = '0.29.15'
try:
    from __builtin__ import basestring
except ImportError:
    basestring = str

class _ArrayType(object):
    is_array = True
    subtypes = ['dtype']

    def __init__(self, dtype, ndim, is_c_contig=False, is_f_contig=False, inner_contig=False, broadcasting=None):
        self.dtype = dtype
        self.ndim = ndim
        self.is_c_contig = is_c_contig
        self.is_f_contig = is_f_contig
        self.inner_contig = inner_contig or is_c_contig or is_f_contig
        self.broadcasting = broadcasting

    def __repr__(self):
        axes = [
         ':'] * self.ndim
        if self.is_c_contig:
            axes[-1] = '::1'
        else:
            if self.is_f_contig:
                axes[0] = '::1'
        return '%s[%s]' % (self.dtype, ', '.join(axes))


def index_type(base_type, item):

    class InvalidTypeSpecification(Exception):
        pass

    def verify_slice(s):
        if s.start or s.stop or s.step not in (None, 1):
            raise InvalidTypeSpecification('Only a step of 1 may be provided to indicate C or Fortran contiguity')

    if isinstance(item, tuple):
        step_idx = None
        for idx, s in enumerate(item):
            verify_slice(s)
            if s.step:
                if step_idx or idx not in (0, len(item) - 1):
                    raise InvalidTypeSpecification('Step may only be provided once, and only in the first or last dimension.')
                if s.step == 1:
                    step_idx = idx

        return _ArrayType(base_type, (len(item)), is_c_contig=(step_idx == len(item) - 1),
          is_f_contig=(step_idx == 0))
    if isinstance(item, slice):
        verify_slice(item)
        return _ArrayType(base_type, 1, is_c_contig=(bool(item.step)))
    array(base_type, item)


compiled = False
_Unspecified = object()

def _empty_decorator(x):
    return x


def locals(**arg_types):
    return _empty_decorator


def test_assert_path_exists(*paths):
    return _empty_decorator


def test_fail_if_path_exists(*paths):
    return _empty_decorator


class _EmptyDecoratorAndManager(object):

    def __call__(self, x):
        return x

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class _Optimization(object):
    pass


cclass = ccall = cfunc = _EmptyDecoratorAndManager()
returns = wraparound = boundscheck = initializedcheck = nonecheck = embedsignature = cdivision = cdivision_warnings = always_allows_keywords = profile = linetrace = infer_types = unraisable_tracebacks = freelist = lambda _: _EmptyDecoratorAndManager()
exceptval = lambda _=None, check=True: _EmptyDecoratorAndManager()
overflowcheck = lambda _: _EmptyDecoratorAndManager()
optimization = _Optimization()
overflowcheck.fold = optimization.use_switch = optimization.unpack_method_calls = lambda arg: _EmptyDecoratorAndManager()
final = internal = type_version_tag = no_gc_clear = no_gc = _empty_decorator
_cython_inline = None

def inline(f, *args, **kwds):
    global _cython_inline
    if isinstance(f, basestring):
        if _cython_inline is None:
            from Cython.Build.Inline import cython_inline as _cython_inline
        return _cython_inline(f, *args, **kwds)
    return f


def compile(f):
    from Cython.Build.Inline import RuntimeCompiledFunction
    return RuntimeCompiledFunction(f)


def cdiv(a, b):
    q = a / b
    if q < 0:
        q += 1
    return q


def cmod(a, b):
    r = a % b
    if a * b < 0:
        r -= b
    return r


def cast(t, *args, **kwargs):
    kwargs.pop('typecheck', None)
    if hasattr(t, '__call__'):
        if isinstance(t, type) and not len(args) != 1:
            if not (args[0] is not None and isinstance(args[0], t)):
                return t(*args)
    return args[0]


def sizeof(arg):
    return 1


def typeof(arg):
    return arg.__class__.__name__


def address(arg):
    return pointer(type(arg))([arg])


def declare(t=None, value=_Unspecified, **kwds):
    if value is not _Unspecified:
        return cast(t, value)
    if isinstance(t, type) and issubclass(t, (StructType, UnionType)) or isinstance(t, typedef):
        return t()
    return


class _nogil(object):

    def __call__(self, x):
        if callable(x):
            return x
        return self

    def __enter__(self):
        pass

    def __exit__(self, exc_class, exc, tb):
        return exc_class is None


nogil = _nogil()
gil = _nogil()
del _nogil

class CythonMetaType(type):

    def __getitem__(type, ix):
        return array(type, ix)


CythonTypeObject = CythonMetaType('CythonTypeObject', (object,), {})

class CythonType(CythonTypeObject):

    def _pointer(self, n=1):
        for i in range(n):
            self = pointer(self)

        return self


class PointerType(CythonType):

    def __init__(self, value=None):
        if isinstance(value, (ArrayType, PointerType)):
            self._items = [cast(self._basetype, a) for a in value._items]
        else:
            if isinstance(value, list):
                self._items = [cast(self._basetype, a) for a in value]
            else:
                if value is None or value == 0:
                    self._items = []
                else:
                    raise ValueError

    def __getitem__(self, ix):
        if ix < 0:
            raise IndexError('negative indexing not allowed in C')
        return self._items[ix]

    def __setitem__(self, ix, value):
        if ix < 0:
            raise IndexError('negative indexing not allowed in C')
        self._items[ix] = cast(self._basetype, value)

    def __eq__(self, value):
        if value is None:
            if not self._items:
                return True
            if type(self) != type(value):
                return False
            return not self._items and not value._items

    def __repr__(self):
        return '%s *' % (self._basetype,)


class ArrayType(PointerType):

    def __init__(self):
        self._items = [
         None] * self._n


class StructType(CythonType):

    def __init__(self, cast_from=_Unspecified, **data):
        if cast_from is not _Unspecified:
            if len(data) > 0:
                raise ValueError('Cannot accept keyword arguments when casting.')
            if type(cast_from) is not type(self):
                raise ValueError('Cannot cast from %s' % cast_from)
            for key, value in cast_from.__dict__.items():
                setattr(self, key, value)

        else:
            for key, value in data.items():
                setattr(self, key, value)

    def __setattr__(self, key, value):
        if key in self._members:
            self.__dict__[key] = cast(self._members[key], value)
        else:
            raise AttributeError("Struct has no member '%s'" % key)


class UnionType(CythonType):

    def __init__(self, cast_from=_Unspecified, **data):
        if cast_from is not _Unspecified:
            if len(data) > 0:
                raise ValueError('Cannot accept keyword arguments when casting.')
            if isinstance(cast_from, dict):
                datadict = cast_from
            else:
                if type(cast_from) is type(self):
                    datadict = cast_from.__dict__
                else:
                    raise ValueError('Cannot cast from %s' % cast_from)
        else:
            datadict = data
        if len(datadict) > 1:
            raise AttributeError('Union can only store one field at a time.')
        for key, value in datadict.items():
            setattr(self, key, value)

    def __setattr__(self, key, value):
        if key in '__dict__':
            CythonType.__setattr__(self, key, value)
        else:
            if key in self._members:
                self.__dict__ = {key: cast(self._members[key], value)}
            else:
                raise AttributeError("Union has no member '%s'" % key)


def pointer(basetype):

    class PointerInstance(PointerType):
        _basetype = basetype

    return PointerInstance


def array(basetype, n):

    class ArrayInstance(ArrayType):
        _basetype = basetype
        _n = n

    return ArrayInstance


def struct(**members):

    class StructInstance(StructType):
        _members = members

    for key in members:
        setattr(StructInstance, key, None)

    return StructInstance


def union(**members):

    class UnionInstance(UnionType):
        _members = members

    for key in members:
        setattr(UnionInstance, key, None)

    return UnionInstance


class typedef(CythonType):

    def __init__(self, type, name=None):
        self._basetype = type
        self.name = name

    def __call__(self, *arg):
        value = cast(self._basetype, *arg)
        return value

    def __repr__(self):
        return self.name or str(self._basetype)

    __getitem__ = index_type


class _FusedType(CythonType):
    pass


def fused_type(*args):
    if not args:
        raise TypeError('Expected at least one type as argument')
    rank = -1
    for type in args:
        if type not in (py_int, py_long, py_float, py_complex):
            break
        if type_ordering.index(type) > rank:
            result_type = type
    else:
        return result_type
    return _FusedType()


def _specialized_from_args(signatures, args, kwargs):
    raise Exception('yet to be implemented')


py_int = typedef(int, 'int')
try:
    py_long = typedef(long, 'long')
except NameError:
    py_long = typedef(int, 'long')

py_float = typedef(float, 'float')
py_complex = typedef(complex, 'double complex')
int_types = [
 'char','short','Py_UNICODE','int','Py_UCS4','long','longlong','Py_ssize_t','size_t']
float_types = ['longdouble', 'double', 'float']
complex_types = ['longdoublecomplex', 'doublecomplex', 'floatcomplex', 'complex']
other_types = ['bint', 'void', 'Py_tss_t']
to_repr = {
  'longlong': 'long long',
  'longdouble': 'long double',
  'longdoublecomplex': 'long double complex',
  'doublecomplex': 'double complex',
  'floatcomplex': 'float complex'}.get
gs = globals()
try:
    import __builtin__ as builtins
except ImportError:
    import builtins

gs['unicode'] = typedef(getattr(builtins, 'unicode', str), 'unicode')
del builtins
for name in int_types:
    reprname = to_repr(name, name)
    gs[name] = typedef(py_int, reprname)
    if name not in ('Py_UNICODE', 'Py_UCS4'):
        if not name.endswith('size_t'):
            gs['u' + name] = typedef(py_int, 'unsigned ' + reprname)
            gs['s' + name] = typedef(py_int, 'signed ' + reprname)

for name in float_types:
    gs[name] = typedef(py_float, to_repr(name, name))

for name in complex_types:
    gs[name] = typedef(py_complex, to_repr(name, name))

bint = typedef(bool, 'bint')
void = typedef(None, 'void')
Py_tss_t = typedef(None, 'Py_tss_t')
for t in int_types + float_types + complex_types + other_types:
    for i in range(1, 4):
        gs['%s_%s' % ('p' * i, t)] = gs[t]._pointer(i)

NULL = gs['p_void'](0)
integral = floating = numeric = _FusedType()
type_ordering = [
 py_int, py_long, py_float, py_complex]

class CythonDotParallel(object):
    __all__ = [
     'parallel', 'prange', 'threadid']

    def parallel(self, num_threads=None):
        return nogil

    def prange(self, start=0, stop=None, step=1, nogil=False, schedule=None, chunksize=None, num_threads=None):
        if stop is None:
            stop = start
            start = 0
        return range(start, stop, step)

    def threadid(self):
        return 0


import sys
sys.modules['cython.parallel'] = CythonDotParallel()
del sys