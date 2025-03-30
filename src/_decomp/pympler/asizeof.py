#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\pympler\asizeof.py
from inspect import isbuiltin, isclass, iscode, isframe, isfunction, ismethod, ismodule, stack
from math import log
from os import curdir, linesep
from struct import calcsize
import sys
import types as Types
import warnings
import weakref as Weakref
__all__ = ['adict',
 'asized',
 'asizeof',
 'asizesof',
 'Asized',
 'Asizer',
 'basicsize',
 'flatsize',
 'itemsize',
 'leng',
 'refs']
if __name__ == '__main__':
    _builtin_modules = (int.__module__, 'types', Exception.__module__)
else:
    _builtin_modules = (int.__module__,
     'types',
     Exception.__module__,
     __name__)
_sizeof_Cbyte = calcsize('c')
_sizeof_Clong = calcsize('l')
_sizeof_Cvoidp = calcsize('P')

def _calcsize(fmt):
    if _sizeof_Clong < _sizeof_Cvoidp:
        z = 'P'
    else:
        z = 'L'
    return calcsize(fmt.replace('z', z))


_sizeof_CPyCodeObject = _calcsize('Pz10P5i0P')
_sizeof_CPyFrameObject = _calcsize('Pzz13P63i0P')
_sizeof_CPyModuleObject = _calcsize('PzP0P')
_sizeof_CPyDictEntry = _calcsize('z2P')
_sizeof_Csetentry = _calcsize('lP')
try:
    _sizeof_Cdigit = long.__itemsize__
except NameError:
    _sizeof_Cdigit = int.__itemsize__

if _sizeof_Cdigit < 2:
    raise AssertionError('sizeof(%s) bad: %d' % ('digit', _sizeof_Cdigit))
try:
    u = unicode('\x00')
except NameError:
    u = '\x00'

u = u.encode('unicode-internal')
_sizeof_Cunicode = len(u)
del u
try:
    import _testcapi as t
    _sizeof_CPyGC_Head = t.SIZEOF_PYGC_HEAD
except (ImportError, AttributeError):
    t = calcsize('2d') - 1
    _sizeof_CPyGC_Head = _calcsize('2Pz') + t & ~t

del t
if hasattr(sys, 'gettotalrefcount'):
    _sizeof_Crefcounts = _calcsize('2z')
else:
    _sizeof_Crefcounts = 0
try:
    from abc import ABCMeta
except ImportError:

    class ABCMeta(type):
        pass


_Py_TPFLAGS_HEAPTYPE = 1 << 9
_Py_TPFLAGS_HAVE_GC = 1 << 14
_Type_type = type(type)

def _items(obj):
    return getattr(obj, 'iteritems', obj.items)()


def _keys(obj):
    return getattr(obj, 'iterkeys', obj.keys)()


def _values(obj):
    return getattr(obj, 'itervalues', obj.values)()


try:
    _callable = callable
except NameError:

    def _callable(obj):
        return hasattr(obj, '__call__')


try:
    from gc import get_referents as _getreferents
except ImportError:

    def _getreferents(unused):
        return ()


_getsizeof = getattr(sys, 'getsizeof', None)
version = sys.version_info
_getsizeof_bugs = getattr(sys, 'getsizeof', None) and (version[0] == 2 and version < (2, 7, 4) or version[0] == 3 and version < (3, 2, 4))

def _getsizeof_exclude(getsizeof, exclude):

    def _getsizeof_wrapper(obj, default):
        if isinstance(obj, exclude):
            return default
        else:
            return getsizeof(obj, default)

    return _getsizeof_wrapper


try:
    _intern = intern
except NameError:

    def _intern(val):
        return val


def _basicsize(t, base = 0, heap = False, obj = None):
    s = max(getattr(t, '__basicsize__', 0), base)
    if t != _Type_type:
        h = getattr(t, '__flags__', 0) & _Py_TPFLAGS_HAVE_GC
    elif heap:
        h = True
    else:
        h = getattr(obj, '__flags__', 0) & _Py_TPFLAGS_HEAPTYPE
    if h:
        s += _sizeof_CPyGC_Head
    return s + _sizeof_Crefcounts


def _derive_typedef(typ):
    v = [ v for v in _values(_typedefs) if _issubclass(typ, v.type) ]
    if len(v) == 1:
        return v[0]


def _dir2(obj, pref = '', excl = (), slots = None, itor = ''):
    if slots:
        if hasattr(obj, slots):
            s = {}
            for c in type(obj).mro():
                for a in getattr(c, slots, ()):
                    if a.startswith('__'):
                        a = '_' + c.__name__ + a
                    if hasattr(obj, a):
                        s.setdefault(a, getattr(obj, a))

            yield (slots, _Slots(s))
            for t in _items(s):
                yield t

    elif itor:
        for o in obj:
            yield (itor, o)

    else:
        for a in dir(obj):
            if a.startswith(pref) and a not in excl and hasattr(obj, a):
                yield (a, getattr(obj, a))


def _infer_dict(obj):
    for ats in (('__len__', 'get', 'has_key', 'items', 'keys', 'values'), ('__len__', 'get', 'has_key', 'iteritems', 'iterkeys', 'itervalues')):
        if all((_callable(getattr(obj, a, None)) for a in ats)):
            return True

    return False


def _isdictclass(obj):
    c = getattr(obj, '__class__', None)
    return c and c.__name__ in _dict_classes.get(c.__module__, ())


def _issubclass(sub, sup):
    if sup is not object:
        try:
            return issubclass(sub, sup)
        except TypeError:
            pass

    return False


closure = (lambda x: lambda : x)(None)
try:
    cell_type = type(closure.__closure__[0])
except AttributeError:
    cell_type = type(closure.func_closure[0])

def _iscell(obj):
    return isinstance(obj, cell_type)


def _isnamedtuple(obj):
    return isinstance(obj, tuple) and hasattr(obj, '_fields')


def _itemsize(t, item = 0):
    return getattr(t, '__itemsize__', 0) or item


def _kwdstr(**kwds):
    return ', '.join(sorted(('%s=%r' % kv for kv in _items(kwds))))


def _lengstr(obj):
    n = leng(obj)
    if n is None:
        r = ''
    elif n > _len(obj):
        r = ' leng %d!' % n
    else:
        r = ' leng %d' % n
    return r


def _nameof(obj, dflt = ''):
    return getattr(obj, '__name__', dflt)


def _objs_opts(objs, all = None, **opts):
    if objs:
        t = objs
    elif all in (False, None):
        t = ()
    elif all is True:
        t = tuple(_values(sys.modules)) + (globals(), stack(sys.getrecursionlimit())[2:])
    else:
        raise ValueError('invalid option: %s=%r' % ('all', all))
    return (t, opts)


def _p100(part, total, prec = 1):
    r = float(total)
    if r:
        r = part * 100.0 / r
        return '%.*f%%' % (prec, r)
    return 'n/a'


def _plural(num):
    if num == 1:
        s = ''
    else:
        s = 's'
    return s


def _power2(n):
    p2 = 16
    while n > p2:
        p2 += p2

    return p2


def _prepr(obj, clip = 0):
    return _repr(obj, clip=clip).strip('<>').replace("'", '')


def _printf(fmt, *args, **print3opts):
    if print3opts:
        f = print3opts.get('file', None) or sys.stdout
        if args:
            f.write(fmt % args)
        else:
            f.write(fmt)
        f.write(print3opts.get('end', linesep))
    elif args:
        print fmt % args
    else:
        print fmt


def _refs(obj, named, *ats, **kwds):
    if named:
        for a in ats:
            if hasattr(obj, a):
                yield _NamedRef(a, getattr(obj, a))

        if kwds:
            for a, o in _dir2(obj, **kwds):
                yield _NamedRef(a, o)

    else:
        for a in ats:
            if hasattr(obj, a):
                yield getattr(obj, a)

        if kwds:
            for _, o in _dir2(obj, **kwds):
                yield o


def _repr(obj, clip = 80):
    try:
        r = repr(obj)
    except Exception:
        r = 'N/A'

    if 0 < clip < len(r):
        h = clip // 2 - 2
        if h > 0:
            r = r[:h] + '....' + r[-h:]
    return r


def _SI(size, K = 1024, i = 'i'):
    if 1 < K < size:
        f = float(size)
        for si in iter('KMGPTE'):
            f /= K
            if f < K:
                return ' or %.1f %s%sB' % (f, si, i)

    return ''


def _SI2(size, **kwds):
    return str(size) + _SI(size, **kwds)


def _class_refs(obj, named):
    return _refs(obj, named, '__class__', '__dict__', '__doc__', '__mro__', '__name__', '__slots__', '__weakref__')


def _co_refs(obj, named):
    return _refs(obj, named, pref='co_')


def _dict_refs(obj, named):
    if named:
        for k, v in _items(obj):
            s = str(k)
            yield _NamedRef('[K] ' + s, k)
            yield _NamedRef('[V] ' + s + ': ' + _repr(v), v)

    else:
        try:
            for k, v in _items(obj):
                yield k
                yield v

        except ReferenceError:
            warnings.warn("Reference error while iterating over '%s'" % str(obj.__class__))


def _enum_refs(obj, named):
    return _refs(obj, named, '__doc__')


def _exc_refs(obj, named):
    return _refs(obj, named, 'args', 'filename', 'lineno', 'msg', 'text')


def _file_refs(obj, named):
    return _refs(obj, named, 'mode', 'name')


def _frame_refs(obj, named):
    return _refs(obj, named, pref='f_')


def _func_refs(obj, named):
    return _refs(obj, named, '__doc__', '__name__', '__code__', '__closure__', pref='func_', excl=('func_globals',))


def _cell_refs(obj, named):
    return _refs(obj, named, 'cell_contents')


def _namedtuple_refs(obj, named):
    return _refs(obj, named, '__class__', slots='__slots__')


def _gen_refs(obj, named):
    f = getattr(obj, 'gi_frame', None)
    return _refs(f, named, 'f_locals', 'f_code')


def _im_refs(obj, named):
    return _refs(obj, named, '__doc__', '__name__', '__code__', pref='im_')


def _inst_refs(obj, named):
    return _refs(obj, named, '__dict__', '__class__', slots='__slots__')


def _iter_refs(obj, named):
    r = _getreferents(obj)
    return _refs(r, named, itor=_nameof(obj) or 'iteref')


def _module_refs(obj, named):
    if obj.__name__ == __name__:
        return ()
    return _dict_refs(obj.__dict__, named)


def _prop_refs(obj, named):
    return _refs(obj, named, '__doc__', pref='f')


def _seq_refs(obj, unused):
    return obj


def _stat_refs(obj, named):
    return _refs(obj, named, pref='st_')


def _statvfs_refs(obj, named):
    return _refs(obj, named, pref='f_')


def _tb_refs(obj, named):
    return _refs(obj, named, pref='tb_')


def _type_refs(obj, named):
    return _refs(obj, named, '__dict__', '__doc__', '__mro__', '__name__', '__slots__', '__weakref__')


def _weak_refs(obj, unused):
    try:
        return (obj(),)
    except:
        return ()


_all_refs = (None,
 _cell_refs,
 _class_refs,
 _co_refs,
 _dict_refs,
 _enum_refs,
 _exc_refs,
 _file_refs,
 _frame_refs,
 _func_refs,
 _gen_refs,
 _im_refs,
 _inst_refs,
 _iter_refs,
 _module_refs,
 _namedtuple_refs,
 _prop_refs,
 _seq_refs,
 _stat_refs,
 _statvfs_refs,
 _tb_refs,
 _type_refs,
 _weak_refs)

def _len(obj):
    try:
        return len(obj)
    except TypeError:
        return 0


def _len_array(obj):
    return len(obj) * obj.itemsize


def _len_bytearray(obj):
    return obj.__alloc__()


def _len_code(obj):
    return obj.co_stacksize + obj.co_nlocals + _len(obj.co_freevars) + _len(obj.co_cellvars) - 1


def _len_dict(obj):
    n = len(obj)
    if n < 6:
        n = 0
    else:
        n = _power2(n + 1)
    return n


def _len_frame(obj):
    c = getattr(obj, 'f_code', None)
    if c:
        n = _len_code(c)
    else:
        n = 0
    return n


_digit2p2 = 1 << (_sizeof_Cdigit << 3)
_digitmax = _digit2p2 - 1
_digitlog = 1.0 / log(_digit2p2)

def _len_int(obj):
    if obj:
        n, i = 1, abs(obj)
        if i > _digitmax:
            n += int(log(i) * _digitlog)
    else:
        n = 0
    return n


def _len_iter(obj):
    n = getattr(obj, '__length_hint__', None)
    if n:
        n = n()
    else:
        n = _len(obj)
    return n


def _len_list(obj):
    n = len(obj)
    if n > 8:
        n += 6 + (n >> 3)
    elif n:
        n += 4
    return n


def _len_module(obj):
    return _len(obj.__dict__)


def _len_set(obj):
    n = len(obj)
    if n > 8:
        n = _power2(n + n - 2)
    elif n:
        n = 8
    return n


def _len_slice(obj):
    try:
        return (obj.stop - obj.start + 1) // obj.step
    except (AttributeError, TypeError):
        return 0


def _len_slots(obj):
    return len(obj) - 1


def _len_struct(obj):
    try:
        return obj.size
    except AttributeError:
        return 0


def _len_unicode(obj):
    return len(obj) + 1


_all_lengs = (None,
 _len,
 _len_array,
 _len_bytearray,
 _len_code,
 _len_dict,
 _len_frame,
 _len_int,
 _len_iter,
 _len_list,
 _len_module,
 _len_set,
 _len_slice,
 _len_slots,
 _len_struct,
 _len_unicode)
_old_style = '*'
_new_style = ''

class _Claskey(object):
    __slots__ = ('_obj', '_sty')

    def __init__(self, obj, style):
        self._obj = obj
        self._sty = style

    def __str__(self):
        r = str(self._obj)
        if r.endswith('>'):
            r = '%s%s def>' % (r[:-1], self._sty)
        elif self._sty is _old_style and not r.startswith('class '):
            r = 'class %s%s def' % (r, self._sty)
        else:
            r = '%s%s def' % (r, self._sty)
        return r

    __repr__ = __str__


_claskeys = {}

def _claskey(obj, style):
    i = id(obj)
    k = _claskeys.get(i, None)
    if not k:
        _claskeys[i] = k = _Claskey(obj, style)
    return k


try:
    _Types_ClassType = Types.ClassType
    _Types_InstanceType = Types.InstanceType

    class _Instkey(object):
        __slots__ = ('_obj',)

        def __init__(self, obj):
            self._obj = obj

        def __str__(self):
            return '<class %s.%s%s>' % (self._obj.__module__, self._obj.__name__, _old_style)

        __repr__ = __str__


    _instkeys = {}

    def _instkey(obj):
        i = id(obj)
        k = _instkeys.get(i, None)
        if not k:
            _instkeys[i] = k = _Instkey(obj)
        return k


    def _keytuple(obj):
        t = type(obj)
        if t is _Types_InstanceType:
            t = obj.__class__
            return (_claskey(t, _old_style), _instkey(t))
        if t is _Types_ClassType:
            return (_claskey(obj, _old_style), _instkey(obj))
        if t is _Type_type:
            return (_claskey(obj, _new_style), obj)
        return (None, None)


    def _objkey(obj):
        k = type(obj)
        if k is _Types_InstanceType:
            k = _instkey(obj.__class__)
        elif k is _Types_ClassType:
            k = _claskey(obj, _old_style)
        elif k is _Type_type:
            k = _claskey(obj, _new_style)
        return k


except AttributeError:

    def _keytuple(obj):
        if type(obj) is _Type_type:
            return (_claskey(obj, _new_style), obj)
        return (None, None)


    def _objkey(obj):
        k = type(obj)
        if k is _Type_type:
            k = _claskey(obj, _new_style)
        return k


class _NamedRef(object):
    __slots__ = ('name', 'ref')

    def __init__(self, name, ref):
        self.name = name
        self.ref = ref


class _Slots(tuple):
    pass


_i = _intern
_all_kinds = _kind_static, _kind_dynamic, _kind_derived, _kind_ignored, _kind_inferred = (_i('static'),
 _i('dynamic'),
 _i('derived'),
 _i('ignored'),
 _i('inferred'))
del _i

class _Typedef(object):
    __slots__ = {'base': 0,
     'item': 0,
     'leng': None,
     'refs': None,
     'both': None,
     'kind': None,
     'type': None}

    def __init__(self, **kwds):
        self.reset(**kwds)

    def __lt__(self, unused):
        return True

    def __repr__(self):
        return repr(self.args())

    def __str__(self):
        t = [str(self.base), str(self.item)]
        for f in (self.leng, self.refs):
            if f:
                t.append(f.__name__)
            else:
                t.append('n/a')

        if not self.both:
            t.append('(code only)')
        return ', '.join(t)

    def args(self):
        return (self.base,
         self.item,
         self.leng,
         self.refs,
         self.both,
         self.kind,
         self.type)

    def dup(self, other = None, **kwds):
        if other is None:
            d = _dict_typedef.kwds()
        else:
            d = other.kwds()
        d.update(kwds)
        self.reset(**d)

    def flat(self, obj, mask = 0):
        s = self.base
        if self.leng and self.item > 0:
            s += self.leng(obj) * self.item
        if _getsizeof:
            s = _getsizeof(obj, s)
        if mask:
            s = s + mask & ~mask
        return s

    def format(self):
        c = n = ''
        if not self.both:
            c = ' (code only)'
        if self.leng:
            n = ' (%s)' % _nameof(self.leng)
        return dict(base=self.base, item=self.item, leng=n, code=c, kind=self.kind)

    def kwds(self):
        return dict(base=self.base, item=self.item, leng=self.leng, refs=self.refs, both=self.both, kind=self.kind, type=self.type)

    def save(self, t, base = 0, heap = False):
        c, k = _keytuple(t)
        if k and k not in _typedefs:
            _typedefs[k] = self
            if c and c not in _typedefs:
                if t.__module__ in _builtin_modules:
                    k = _kind_ignored
                else:
                    k = self.kind
                _typedefs[c] = _Typedef(base=_basicsize(type(t), base=base, heap=heap), refs=_type_refs, both=False, kind=k, type=t)
        elif isbuiltin(t) and t not in _typedefs:
            _typedefs[t] = _Typedef(base=_basicsize(t, base=base), both=False, kind=_kind_ignored, type=t)
        else:
            raise KeyError('asizeof typedef %r bad: %r %r' % (self, (c, k), self.both))

    def set(self, safe_len = False, **kwds):
        if kwds:
            d = self.kwds()
            d.update(kwds)
            self.reset(**d)
        if safe_len and self.item:
            self.leng = _len

    def reset(self, base = 0, item = 0, leng = None, refs = None, both = True, kind = None, type = None):
        if base < 0:
            raise ValueError('invalid option: %s=%r' % ('base', base))
        else:
            self.base = base
        if item < 0:
            raise ValueError('invalid option: %s=%r' % ('item', item))
        else:
            self.item = item
        if leng in _all_lengs:
            self.leng = leng
        else:
            raise ValueError('invalid option: %s=%r' % ('leng', leng))
        if refs in _all_refs:
            self.refs = refs
        else:
            raise ValueError('invalid option: %s=%r' % ('refs', refs))
        if both in (False, True):
            self.both = both
        else:
            raise ValueError('invalid option: %s=%r' % ('both', both))
        if kind in _all_kinds:
            self.kind = kind
        else:
            raise ValueError('invalid option: %s=%r' % ('kind', kind))
        self.type = type


_typedefs = {}

def _typedef_both(t, base = 0, item = 0, leng = None, refs = None, kind = _kind_static, heap = False):
    v = _Typedef(base=_basicsize(t, base=base), item=_itemsize(t, item), refs=refs, leng=leng, both=True, kind=kind, type=t)
    v.save(t, base=base, heap=heap)
    return v


def _typedef_code(t, base = 0, refs = None, kind = _kind_static, heap = False):
    v = _Typedef(base=_basicsize(t, base=base), refs=refs, both=False, kind=kind, type=t)
    v.save(t, base=base, heap=heap)
    return v


_typedef_both(complex)
_typedef_both(float)
_typedef_both(list, refs=_seq_refs, leng=_len_list, item=_sizeof_Cvoidp)
_typedef_both(tuple, refs=_seq_refs, leng=_len, item=_sizeof_Cvoidp)
_typedef_both(property, refs=_prop_refs)
_typedef_both(type(Ellipsis))
_typedef_both(type(None))
_typedef_both(_Slots, item=_sizeof_Cvoidp, leng=_len_slots, refs=None, heap=True)
_dict_typedef = _typedef_both(dict, item=_sizeof_CPyDictEntry, leng=_len_dict, refs=_dict_refs)
try:
    _typedef_both(Types.DictProxyType, item=_sizeof_CPyDictEntry, leng=_len_dict, refs=_dict_refs)
except AttributeError:
    _typedef_both(type(_Typedef.__dict__), item=_sizeof_CPyDictEntry, leng=_len_dict, refs=_dict_refs)

_dict_classes = {'UserDict': ('IterableUserDict', 'UserDict'),
 'weakref': ('WeakKeyDictionary', 'WeakValueDictionary')}
try:
    _typedef_both(Types.ModuleType, base=_dict_typedef.base, item=_dict_typedef.item + _sizeof_CPyModuleObject, leng=_len_module, refs=_module_refs)
except AttributeError:
    pass

try:
    from array import array
    _typedef_both(array, leng=_len_array, item=_sizeof_Cbyte)
    if _getsizeof_bugs:
        _getsizeof = _getsizeof_exclude(_getsizeof, array)
except ImportError:
    pass

try:
    _typedef_both(bool)
except NameError:
    pass

try:
    _typedef_both(basestring, leng=None)
except NameError:
    pass

try:
    if isbuiltin(buffer):
        _typedef_both(type(buffer('')), item=_sizeof_Cbyte, leng=_len)
    else:
        _typedef_both(buffer, item=_sizeof_Cbyte, leng=_len)
except NameError:
    pass

try:
    _typedef_both(bytearray, item=_sizeof_Cbyte, leng=_len_bytearray)
except NameError:
    pass

try:
    if type(bytes) is not type(str):
        _typedef_both(bytes, item=_sizeof_Cbyte, leng=_len)
except NameError:
    pass

try:
    _typedef_both(str8, item=_sizeof_Cbyte, leng=_len)
except NameError:
    pass

try:
    _typedef_both(enumerate, refs=_enum_refs)
except NameError:
    pass

try:
    _typedef_both(Exception, refs=_exc_refs)
except:
    pass

try:
    _typedef_both(file, refs=_file_refs)
except NameError:
    pass

try:
    _typedef_both(frozenset, item=_sizeof_Csetentry, leng=_len_set, refs=_seq_refs)
except NameError:
    pass

try:
    _typedef_both(set, item=_sizeof_Csetentry, leng=_len_set, refs=_seq_refs)
except NameError:
    pass

try:
    _typedef_both(Types.GetSetDescriptorType)
except AttributeError:
    pass

try:
    _typedef_both(long, item=_sizeof_Cdigit, leng=_len_int)
    _typedef_both(int)
except NameError:
    _typedef_both(int, item=_sizeof_Cdigit, leng=_len_int)

try:
    _typedef_both(Types.MemberDescriptorType)
except AttributeError:
    pass

try:
    _typedef_both(type(NotImplemented))
except NameError:
    pass

try:
    _typedef_both(range)
except NameError:
    pass

try:
    _typedef_both(xrange)
except NameError:
    pass

try:
    _typedef_both(reversed, refs=_enum_refs)
except NameError:
    pass

try:
    _typedef_both(slice, item=_sizeof_Cvoidp, leng=_len_slice)
except NameError:
    pass

try:
    from os import stat
    _typedef_both(type(stat(curdir)), refs=_stat_refs)
except ImportError:
    pass

try:
    from os import statvfs
    _typedef_both(type(statvfs(curdir)), refs=_statvfs_refs, item=_sizeof_Cvoidp, leng=_len)
except ImportError:
    pass

try:
    from struct import Struct
    _typedef_both(Struct, item=_sizeof_Cbyte, leng=_len_struct)
except ImportError:
    pass

try:
    _typedef_both(Types.TracebackType, refs=_tb_refs)
except AttributeError:
    pass

try:
    _typedef_both(unicode, leng=_len_unicode, item=_sizeof_Cunicode)
    _typedef_both(str, leng=_len, item=_sizeof_Cbyte)
except NameError:
    _typedef_both(str, leng=_len_unicode, item=_sizeof_Cunicode)

try:
    _typedef_both(Weakref.KeyedRef, refs=_weak_refs, heap=True)
except AttributeError:
    pass

try:
    _typedef_both(Weakref.ProxyType)
except AttributeError:
    pass

try:
    _typedef_both(Weakref.ReferenceType, refs=_weak_refs)
except AttributeError:
    pass

_typedef_code(object, kind=_kind_ignored)
_typedef_code(super, kind=_kind_ignored)
_typedef_code(_Type_type, kind=_kind_ignored)
try:
    _typedef_code(classmethod, refs=_im_refs)
except NameError:
    pass

try:
    _typedef_code(staticmethod, refs=_im_refs)
except NameError:
    pass

try:
    _typedef_code(Types.MethodType, refs=_im_refs)
except NameError:
    pass

try:
    _typedef_code(Types.GeneratorType, refs=_gen_refs)
except AttributeError:
    pass

try:
    _typedef_code(Weakref.CallableProxyType, refs=_weak_refs)
except AttributeError:
    pass

s = [_items({}), _keys({}), _values({})]
try:
    s.extend([reversed([]), reversed(())])
except NameError:
    pass

try:
    s.append(xrange(1))
except NameError:
    pass

try:
    from re import finditer
    s.append(finditer('', ''))
except ImportError:
    pass

for t in _values(_typedefs):
    if t.type and t.leng:
        try:
            s.append(t.type())
        except TypeError:
            pass

for t in s:
    try:
        i = iter(t)
        _typedef_both(type(i), leng=_len_iter, refs=_iter_refs, item=0)
    except (KeyError, TypeError):
        pass

del i
del s
del t

def _typedef(obj, derive = False, infer = False):
    t = type(obj)
    v = _Typedef(base=_basicsize(t, obj=obj), kind=_kind_dynamic, type=t)
    if ismodule(obj):
        v.dup(item=_dict_typedef.item + _sizeof_CPyModuleObject, leng=_len_module, refs=_module_refs)
    elif isframe(obj):
        v.set(base=_basicsize(t, base=_sizeof_CPyFrameObject, obj=obj), item=_itemsize(t), leng=_len_frame, refs=_frame_refs)
    elif iscode(obj):
        v.set(base=_basicsize(t, base=_sizeof_CPyCodeObject, obj=obj), item=_sizeof_Cvoidp, leng=_len_code, refs=_co_refs, both=False)
    elif _callable(obj):
        if isclass(obj):
            v.set(refs=_class_refs, both=False)
            if getattr(obj, '__module__', None) in _builtin_modules:
                v.set(kind=_kind_ignored)
        elif isbuiltin(obj):
            v.set(both=False, kind=_kind_ignored)
        elif isfunction(obj):
            v.set(refs=_func_refs, both=False)
        elif ismethod(obj):
            v.set(refs=_im_refs, both=False)
        elif isclass(t):
            v.set(item=_itemsize(t), safe_len=True, refs=_inst_refs)
        else:
            v.set(both=False)
    elif _issubclass(t, dict):
        v.dup(kind=_kind_derived)
    elif _isdictclass(obj) or infer and _infer_dict(obj):
        v.dup(kind=_kind_inferred)
    elif _iscell(obj):
        v.set(item=_itemsize(t), refs=_cell_refs)
    elif _isnamedtuple(obj):
        v.set(refs=_namedtuple_refs)
    elif getattr(obj, '__module__', None) in _builtin_modules:
        v.set(kind=_kind_ignored)
    else:
        if derive:
            p = _derive_typedef(t)
            if p:
                v.dup(other=p, kind=_kind_derived)
                return v
        if _issubclass(t, Exception):
            v.set(item=_itemsize(t), safe_len=True, refs=_exc_refs, kind=_kind_derived)
        elif isinstance(obj, Exception):
            v.set(item=_itemsize(t), safe_len=True, refs=_exc_refs)
        else:
            v.set(item=_itemsize(t), safe_len=True, refs=_inst_refs)
    return v


class _Prof(object):
    total = 0
    high = 0
    number = 0
    objref = None
    weak = False

    def __cmp__(self, other):
        if self.total < other.total:
            return -1
        if self.total > other.total:
            return +1
        if self.number < other.number:
            return -1
        if self.number > other.number:
            return +1
        return 0

    def __lt__(self, other):
        return self.__cmp__(other) < 0

    def format(self, clip = 0, grand = None):
        if self.number > 1:
            a, p = int(self.total / self.number), 's'
        else:
            a, p = self.total, ''
        o = self.objref
        if self.weak:
            o = o()
        t = _SI2(self.total)
        if grand:
            t += ' (%s)' % _p100(self.total, grand, prec=0)
        return dict(avg=_SI2(a), high=_SI2(self.high), lengstr=_lengstr(o), obj=_repr(o, clip=clip), plural=p, total=t)

    def update(self, obj, size):
        self.number += 1
        self.total += size
        if self.high < size:
            self.high = size
            try:
                self.objref, self.weak = Weakref.ref(obj), True
            except TypeError:
                self.objref, self.weak = obj, False


class Asized(object):

    def __init__(self, size, flat, refs = (), name = None):
        self.size = size
        self.flat = flat
        self.name = name
        self.refs = tuple(refs)

    def __str__(self):
        return 'size %r, flat %r, refs[%d], name %r' % (self.size,
         self.flat,
         len(self.refs),
         self.name)

    def get(self, name):
        for ref in self.refs:
            if name == ref.name:
                return ref

    def format(self, format = '%(name)s size=%(size)d flat=%(flat)d', depth = -1, order_by = 'size', indent = ''):
        representation = indent + format % self.__dict__
        if depth != 0:
            indent = indent + '    '
            reverse = order_by in ('size', 'flat')
            refs = sorted(self.refs, key=lambda x: getattr(x, order_by), reverse=reverse)
            refs = [ ref.format(format, depth - 1, order_by, indent) for ref in refs ]
            representation = '\n'.join([representation] + refs)
        return representation


class Asizer(object):
    _align_ = 8
    _clip_ = 80
    _code_ = False
    _derive_ = False
    _detail_ = 0
    _infer_ = False
    _limit_ = 100
    _stats_ = 0
    _cutoff = 0
    _depth = 0
    _duplicate = 0
    _excl_d = None
    _ign_d = _kind_ignored
    _incl = ''
    _mask = 7
    _missed = 0
    _profile = False
    _profs = None
    _seen = None
    _total = 0
    _stream = None

    def __init__(self, **opts):
        self._excl_d = {}
        self.reset(**opts)

    def _printf(self, *args, **kwargs):
        if self._stream and not kwargs.get('file'):
            kwargs['file'] = self._stream
        _printf(*args, **kwargs)

    def _clear(self):
        self._depth = 0
        self._duplicate = 0
        self._incl = ''
        self._missed = 0
        self._profile = False
        self._profs = {}
        self._seen = {}
        self._total = 0
        for k in _keys(self._excl_d):
            self._excl_d[k] = 0

    def _nameof(self, obj):
        return _nameof(obj, '') or self._repr(obj)

    def _prepr(self, obj):
        return _prepr(obj, clip=self._clip_)

    def _prof(self, key):
        p = self._profs.get(key, None)
        if not p:
            self._profs[key] = p = _Prof()
        return p

    def _repr(self, obj):
        return _repr(obj, clip=self._clip_)

    def _sizer(self, obj, deep, sized):
        s, f, i = 0, 0, id(obj)
        if i in self._seen:
            if deep:
                self._seen[i] += 1
                if sized:
                    s = sized(s, f, name=self._nameof(obj))
                return s
        else:
            self._seen[i] = 0
        try:
            k, rs = _objkey(obj), []
            if k in self._excl_d:
                self._excl_d[k] += 1
            else:
                v = _typedefs.get(k, None)
                if not v:
                    _typedefs[k] = v = _typedef(obj, derive=self._derive_, infer=self._infer_)
                if (v.both or self._code_) and v.kind is not self._ign_d:
                    s = f = v.flat(obj, self._mask)
                    if self._profile:
                        self._prof(k).update(obj, s)
                    if v.refs and deep < self._limit_ and not (deep and ismodule(obj)):
                        r, z, d = v.refs, self._sizer, deep + 1
                        if sized and deep < self._detail_:
                            for o in r(obj, True):
                                if isinstance(o, _NamedRef):
                                    t = z(o.ref, d, sized)
                                    t.name = o.name
                                else:
                                    t = z(o, d, sized)
                                    t.name = self._nameof(o)
                                rs.append(t)
                                s += t.size

                        else:
                            for o in r(obj, False):
                                s += z(o, d, None)

                        if self._depth < d:
                            self._depth = d
            self._seen[i] += 1
        except RuntimeError:
            self._missed += 1

        if sized:
            s = sized(s, f, name=self._nameof(obj), refs=rs)
        return s

    def _sizes(self, objs, sized = None):
        self.exclude_refs(*objs)
        s, t = {}, []
        for o in objs:
            i = id(o)
            if i in s:
                self._seen[i] += 1
                self._duplicate += 1
            else:
                s[i] = self._sizer(o, 0, sized)
            t.append(s[i])

        if sized:
            s = sum((i.size for i in _values(s)))
        else:
            s = sum(_values(s))
        self._total += s
        return (s, tuple(t))

    def asized(self, *objs, **opts):
        if opts:
            self.set(**opts)
        _, t = self._sizes(objs, Asized)
        if len(t) == 1:
            t = t[0]
        return t

    def asizeof(self, *objs, **opts):
        if opts:
            self.set(**opts)
        s, _ = self._sizes(objs, None)
        return s

    def asizesof(self, *objs, **opts):
        if opts:
            self.set(**opts)
        _, t = self._sizes(objs, None)
        return t

    def exclude_refs(self, *objs):
        for o in objs:
            self._seen.setdefault(id(o), 0)

    def exclude_types(self, *objs):
        for o in objs:
            for t in _keytuple(o):
                if t and t not in self._excl_d:
                    self._excl_d[t] = 0

    def print_profiles(self, w = 0, cutoff = 0, **print3opts):
        t = [ (v, k) for k, v in _items(self._profs) if v.total > 0 or v.number > 1 ]
        if len(self._profs) - len(t) < 9:
            t = [ (v, k) for k, v in _items(self._profs) ]
        if t:
            s = ''
            if self._total:
                s = ' (% of grand total)'
                c = max(cutoff, self._cutoff)
                c = int(c * 0.01 * self._total)
            else:
                c = 0
            self._printf('%s%*d profile%s:  total%s, average, and largest flat size%s:  largest object', linesep, w, len(t), _plural(len(t)), s, self._incl, **print3opts)
            r = len(t)
            for v, k in sorted(t, reverse=True):
                s = 'object%(plural)s:  %(total)s, %(avg)s, %(high)s:  %(obj)s%(lengstr)s' % v.format(self._clip_, self._total)
                self._printf('%*d %s %s', w, v.number, self._prepr(k), s, **print3opts)
                r -= 1
                if r > 1 and v.total < c:
                    c = max(cutoff, self._cutoff)
                    self._printf('%+*d profiles below cutoff (%.0f%%)', w, r, c)
                    break

            z = len(self._profs) - len(t)
            if z > 0:
                self._printf('%+*d %r object%s', w, z, 'zero', _plural(z), **print3opts)

    def print_stats(self, objs = (), opts = {}, sized = (), sizes = (), stats = 3.0, **print3opts):
        s = min(opts.get('stats', stats) or 0, self._stats_)
        if s > 0:
            t = self._total + self._missed + sum(_values(self._seen))
            w = len(str(t)) + 1
            t = c = ''
            o = _kwdstr(**opts)
            if o and objs:
                c = ', '
            if sized and objs:
                n = len(objs)
                if n > 1:
                    self._printf('%sasized(...%s%s) ...', linesep, c, o, **print3opts)
                    for i in range(n):
                        self._printf('%*d: %s', (w - 1), i, sized[i], **print3opts)

                else:
                    self._printf('%sasized(%s): %s', linesep, o, sized, **print3opts)
            elif sizes and objs:
                self._printf('%sasizesof(...%s%s) ...', linesep, c, o, **print3opts)
                for z, o in zip(sizes, objs):
                    self._printf('%*d bytes%s%s:  %s', w, z, _SI(z), self._incl, self._repr(o), **print3opts)

            else:
                if objs:
                    t = self._repr(objs)
                self._printf('%sasizeof(%s%s%s) ...', linesep, t, c, o, **print3opts)
            self.print_summary(w=w, objs=objs, **print3opts)
            if s > 1:
                c = int(s - int(s)) * 100
                self.print_profiles(w=w, cutoff=c, **print3opts)
                if s > 2:
                    self.print_typedefs(w=w, **print3opts)

    def print_summary(self, w = 0, objs = (), **print3opts):
        self._printf('%*d bytes%s%s', w, self._total, _SI(self._total), self._incl, **print3opts)
        if self._mask:
            self._printf('%*d byte aligned', w, (self._mask + 1), **print3opts)
        self._printf('%*d byte sizeof(void*)', w, _sizeof_Cvoidp, **print3opts)
        n = len(objs or ())
        if n > 0:
            d = self._duplicate or ''
            if d:
                d = ', %d duplicate' % self._duplicate
            self._printf('%*d object%s given%s', w, n, _plural(n), d, **print3opts)
        t = sum((1 for t in _values(self._seen) if t != 0))
        self._printf('%*d object%s sized', w, t, _plural(t), **print3opts)
        if self._excl_d:
            t = sum(_values(self._excl_d))
            self._printf('%*d object%s excluded', w, t, _plural(t), **print3opts)
        t = sum(_values(self._seen))
        self._printf('%*d object%s seen', w, t, _plural(t), **print3opts)
        if self._missed > 0:
            self._printf('%*d object%s missed', w, self._missed, _plural(self._missed), **print3opts)
        if self._depth > 0:
            self._printf('%*d recursion depth', w, self._depth, **print3opts)

    def print_typedefs(self, w = 0, **print3opts):
        for k in _all_kinds:
            t = [ (self._prepr(a), v) for a, v in _items(_typedefs) if v.kind == k and (v.both or self._code_) ]
            if t:
                self._printf('%s%*d %s type%s:  basicsize, itemsize, _len_(), _refs()', linesep, w, len(t), k, _plural(len(t)), **print3opts)
                for a, v in sorted(t):
                    self._printf('%*s %s:  %s', w, '', a, v, **print3opts)

        t = sum((len(v) for v in _values(_dict_classes)))
        if t:
            self._printf('%s%*d dict/-like classes:', linesep, w, t, **print3opts)
            for m, v in _items(_dict_classes):
                self._printf('%*s %s:  %s', w, '', m, self._prepr(v), **print3opts)

    def set(self, align = None, code = None, detail = None, limit = None, stats = None):
        if align is not None:
            self._align_ = align
            if align > 1:
                self._mask = align - 1
                if self._mask & align != 0:
                    raise ValueError('invalid option: %s=%r' % ('align', align))
            else:
                self._mask = 0
        if code is not None:
            self._code_ = code
            if code:
                self._incl = ' (incl. code)'
        if detail is not None:
            self._detail_ = detail
        if limit is not None:
            self._limit_ = limit
        if stats is not None:
            self._stats_ = s = int(stats)
            self._cutoff = (stats - s) * 100
            if s > 1:
                self._profile = True
            else:
                self._profile = False

    def _get_duplicate(self):
        return self._duplicate

    duplicate = property(_get_duplicate, doc=_get_duplicate.__doc__)

    def _get_missed(self):
        return self._missed

    missed = property(_get_missed, doc=_get_missed.__doc__)

    def _get_total(self):
        return self._total

    total = property(_get_total, doc=_get_total.__doc__)

    def reset(self, align = 8, clip = 80, code = False, derive = False, detail = 0, ignored = True, infer = False, limit = 100, stats = 0, stream = None):
        self._align_ = align
        self._clip_ = clip
        self._code_ = code
        self._derive_ = derive
        self._detail_ = detail
        self._infer_ = infer
        self._limit_ = limit
        self._stats_ = stats
        self._stream = stream
        if ignored:
            self._ign_d = _kind_ignored
        else:
            self._ign_d = None
        self._clear()
        self.set(align=align, code=code, stats=stats)


def adict(*classes):
    a = True
    for c in classes:
        if isclass(c) and _infer_dict(c):
            t = _dict_classes.get(c.__module__, ())
            if c.__name__ not in t:
                _dict_classes[c.__module__] = t + (c.__name__,)
        else:
            a = False

    return a


_asizer = Asizer()

def asized(*objs, **opts):
    if 'all' in opts:
        raise KeyError('invalid option: %s=%r' % ('all', opts['all']))
    if objs:
        _asizer.reset(**opts)
        t = _asizer.asized(*objs)
        _asizer.print_stats(objs, opts=opts, sized=t)
        _asizer._clear()
    else:
        t = ()
    return t


def asizeof(*objs, **opts):
    t, p = _objs_opts(objs, **opts)
    if t:
        _asizer.reset(**p)
        s = _asizer.asizeof(*t)
        _asizer.print_stats(objs=t, opts=opts)
        _asizer._clear()
    else:
        s = 0
    return s


def asizesof(*objs, **opts):
    if 'all' in opts:
        raise KeyError('invalid option: %s=%r' % ('all', opts['all']))
    if objs:
        _asizer.reset(**opts)
        t = _asizer.asizesof(*objs)
        _asizer.print_stats(objs, opts=opts, sizes=t)
        _asizer._clear()
    else:
        t = ()
    return t


def _typedefof(obj, save = False, **opts):
    k = _objkey(obj)
    v = _typedefs.get(k, None)
    if not v:
        v = _typedef(obj, **opts)
        if save:
            _typedefs[k] = v
    return v


def basicsize(obj, **opts):
    v = _typedefof(obj, **opts)
    if v:
        v = v.base
    return v


def flatsize(obj, align = 0, **opts):
    v = _typedefof(obj, **opts)
    if v:
        if align > 1:
            m = align - 1
            if align & m != 0:
                raise ValueError('invalid option: %s=%r' % ('align', align))
        else:
            m = 0
        v = v.flat(obj, m)
    return v


def itemsize(obj, **opts):
    v = _typedefof(obj, **opts)
    if v:
        v = v.item
    return v


def leng(obj, **opts):
    v = _typedefof(obj, **opts)
    if v:
        v = v.leng
        if v and _callable(v):
            v = v(obj)
    return v


def refs(obj, **opts):
    v = _typedefof(obj, **opts)
    if v:
        v = v.refs
        if v and _callable(v):
            v = v(obj, False)
    return v


def named_refs(obj):
    refs = []
    v = _typedefof(obj)
    if v:
        v = v.refs
        if v and _callable(v):
            for ref in v(obj, True):
                try:
                    refs.append((ref.name, ref.ref))
                except AttributeError:
                    pass

    return refs
