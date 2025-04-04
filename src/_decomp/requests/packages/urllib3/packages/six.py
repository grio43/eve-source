#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\requests\packages\urllib3\packages\six.py
import operator
import sys
import types
__author__ = 'Benjamin Peterson <benjamin@python.org>'
__version__ = '1.2.0'
PY3 = sys.version_info[0] == 3
if PY3:
    string_types = (str,)
    integer_types = (int,)
    class_types = (type,)
    text_type = str
    binary_type = bytes
    MAXSIZE = sys.maxsize
else:
    string_types = (basestring,)
    integer_types = (int, long)
    class_types = (type, types.ClassType)
    text_type = unicode
    binary_type = str
    if sys.platform.startswith('java'):
        MAXSIZE = int(2147483647L)
    else:

        class X(object):

            def __len__(self):
                return 2147483648L


        try:
            len(X())
        except OverflowError:
            MAXSIZE = int(2147483647L)
        else:
            MAXSIZE = int(9223372036854775807L)
            del X

def _add_doc(func, doc):
    func.__doc__ = doc


def _import_module(name):
    __import__(name)
    return sys.modules[name]


class _LazyDescr(object):

    def __init__(self, name):
        self.name = name

    def __get__(self, obj, tp):
        result = self._resolve()
        setattr(obj, self.name, result)
        delattr(tp, self.name)
        return result


class MovedModule(_LazyDescr):

    def __init__(self, name, old, new = None):
        super(MovedModule, self).__init__(name)
        if PY3:
            if new is None:
                new = name
            self.mod = new
        else:
            self.mod = old

    def _resolve(self):
        return _import_module(self.mod)


class MovedAttribute(_LazyDescr):

    def __init__(self, name, old_mod, new_mod, old_attr = None, new_attr = None):
        super(MovedAttribute, self).__init__(name)
        if PY3:
            if new_mod is None:
                new_mod = name
            self.mod = new_mod
            if new_attr is None:
                if old_attr is None:
                    new_attr = name
                else:
                    new_attr = old_attr
            self.attr = new_attr
        else:
            self.mod = old_mod
            if old_attr is None:
                old_attr = name
            self.attr = old_attr

    def _resolve(self):
        module = _import_module(self.mod)
        return getattr(module, self.attr)


class _MovedItems(types.ModuleType):
    pass


_moved_attributes = [MovedAttribute('cStringIO', 'cStringIO', 'io', 'StringIO'),
 MovedAttribute('filter', 'itertools', 'builtins', 'ifilter', 'filter'),
 MovedAttribute('input', '__builtin__', 'builtins', 'raw_input', 'input'),
 MovedAttribute('map', 'itertools', 'builtins', 'imap', 'map'),
 MovedAttribute('reload_module', '__builtin__', 'imp', 'reload'),
 MovedAttribute('reduce', '__builtin__', 'functools'),
 MovedAttribute('StringIO', 'StringIO', 'io'),
 MovedAttribute('xrange', '__builtin__', 'builtins', 'xrange', 'range'),
 MovedAttribute('zip', 'itertools', 'builtins', 'izip', 'zip'),
 MovedModule('builtins', '__builtin__'),
 MovedModule('configparser', 'ConfigParser'),
 MovedModule('copyreg', 'copy_reg'),
 MovedModule('http_cookiejar', 'cookielib', 'http.cookiejar'),
 MovedModule('http_cookies', 'Cookie', 'http.cookies'),
 MovedModule('html_entities', 'htmlentitydefs', 'html.entities'),
 MovedModule('html_parser', 'HTMLParser', 'html.parser'),
 MovedModule('http_client', 'httplib', 'http.client'),
 MovedModule('BaseHTTPServer', 'BaseHTTPServer', 'http.server'),
 MovedModule('CGIHTTPServer', 'CGIHTTPServer', 'http.server'),
 MovedModule('SimpleHTTPServer', 'SimpleHTTPServer', 'http.server'),
 MovedModule('cPickle', 'cPickle', 'pickle'),
 MovedModule('queue', 'Queue'),
 MovedModule('reprlib', 'repr'),
 MovedModule('socketserver', 'SocketServer'),
 MovedModule('tkinter', 'Tkinter'),
 MovedModule('tkinter_dialog', 'Dialog', 'tkinter.dialog'),
 MovedModule('tkinter_filedialog', 'FileDialog', 'tkinter.filedialog'),
 MovedModule('tkinter_scrolledtext', 'ScrolledText', 'tkinter.scrolledtext'),
 MovedModule('tkinter_simpledialog', 'SimpleDialog', 'tkinter.simpledialog'),
 MovedModule('tkinter_tix', 'Tix', 'tkinter.tix'),
 MovedModule('tkinter_constants', 'Tkconstants', 'tkinter.constants'),
 MovedModule('tkinter_dnd', 'Tkdnd', 'tkinter.dnd'),
 MovedModule('tkinter_colorchooser', 'tkColorChooser', 'tkinter.colorchooser'),
 MovedModule('tkinter_commondialog', 'tkCommonDialog', 'tkinter.commondialog'),
 MovedModule('tkinter_tkfiledialog', 'tkFileDialog', 'tkinter.filedialog'),
 MovedModule('tkinter_font', 'tkFont', 'tkinter.font'),
 MovedModule('tkinter_messagebox', 'tkMessageBox', 'tkinter.messagebox'),
 MovedModule('tkinter_tksimpledialog', 'tkSimpleDialog', 'tkinter.simpledialog'),
 MovedModule('urllib_robotparser', 'robotparser', 'urllib.robotparser'),
 MovedModule('winreg', '_winreg')]
for attr in _moved_attributes:
    setattr(_MovedItems, attr.name, attr)

del attr
moves = sys.modules[__name__ + '.moves'] = _MovedItems('moves')

def add_move(move):
    setattr(_MovedItems, move.name, move)


def remove_move(name):
    try:
        delattr(_MovedItems, name)
    except AttributeError:
        try:
            del moves.__dict__[name]
        except KeyError:
            raise AttributeError('no such move, %r' % (name,))


if PY3:
    _meth_func = '__func__'
    _meth_self = '__self__'
    _func_code = '__code__'
    _func_defaults = '__defaults__'
    _iterkeys = 'keys'
    _itervalues = 'values'
    _iteritems = 'items'
else:
    _meth_func = 'im_func'
    _meth_self = 'im_self'
    _func_code = 'func_code'
    _func_defaults = 'func_defaults'
    _iterkeys = 'iterkeys'
    _itervalues = 'itervalues'
    _iteritems = 'iteritems'
try:
    advance_iterator = next
except NameError:

    def advance_iterator(it):
        return it.next()


next = advance_iterator
if PY3:

    def get_unbound_function(unbound):
        return unbound


    Iterator = object

    def callable(obj):
        return any(('__call__' in klass.__dict__ for klass in type(obj).__mro__))


else:

    def get_unbound_function(unbound):
        return unbound.im_func


    class Iterator(object):

        def next(self):
            return type(self).__next__(self)


    callable = callable
_add_doc(get_unbound_function, 'Get the function out of a possibly unbound function')
get_method_function = operator.attrgetter(_meth_func)
get_method_self = operator.attrgetter(_meth_self)
get_function_code = operator.attrgetter(_func_code)
get_function_defaults = operator.attrgetter(_func_defaults)

def iterkeys(d):
    return iter(getattr(d, _iterkeys)())


def itervalues(d):
    return iter(getattr(d, _itervalues)())


def iteritems(d):
    return iter(getattr(d, _iteritems)())


if PY3:

    def b(s):
        return s.encode('latin-1')


    def u(s):
        return s


    if sys.version_info[1] <= 1:

        def int2byte(i):
            return bytes((i,))


    else:
        int2byte = operator.methodcaller('to_bytes', 1, 'big')
    import io
    StringIO = io.StringIO
    BytesIO = io.BytesIO
else:

    def b(s):
        return s


    def u(s):
        return unicode(s, 'unicode_escape')


    int2byte = chr
    import StringIO
    StringIO = BytesIO = StringIO.StringIO
_add_doc(b, 'Byte literal')
_add_doc(u, 'Text literal')
if PY3:
    import builtins
    exec_ = getattr(builtins, 'exec')

    def reraise(tp, value, tb = None):
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value


    print_ = getattr(builtins, 'print')
    del builtins
else:

    def exec_(code, globs = None, locs = None):
        if globs is None:
            frame = sys._getframe(1)
            globs = frame.f_globals
            if locs is None:
                locs = frame.f_locals
            del frame
        elif locs is None:
            locs = globs
        exec 'exec code in globs, locs'


    exec_('def reraise(tp, value, tb=None):\n    raise tp, value, tb\n')

    def print_(*args, **kwargs):
        fp = kwargs.pop('file', sys.stdout)
        if fp is None:
            return

        def write(data):
            if not isinstance(data, basestring):
                data = str(data)
            fp.write(data)

        want_unicode = False
        sep = kwargs.pop('sep', None)
        if sep is not None:
            if isinstance(sep, unicode):
                want_unicode = True
            elif not isinstance(sep, str):
                raise TypeError('sep must be None or a string')
        end = kwargs.pop('end', None)
        if end is not None:
            if isinstance(end, unicode):
                want_unicode = True
            elif not isinstance(end, str):
                raise TypeError('end must be None or a string')
        if kwargs:
            raise TypeError('invalid keyword arguments to print()')
        if not want_unicode:
            for arg in args:
                if isinstance(arg, unicode):
                    want_unicode = True
                    break

        if want_unicode:
            newline = unicode('\n')
            space = unicode(' ')
        else:
            newline = '\n'
            space = ' '
        if sep is None:
            sep = space
        if end is None:
            end = newline
        for i, arg in enumerate(args):
            if i:
                write(sep)
            write(arg)

        write(end)


_add_doc(reraise, 'Reraise an exception.')

def with_metaclass(meta, base = object):
    return meta('NewBase', (base,), {})
