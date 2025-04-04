#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sentry_sdk\utils.py
import os
import sys
import linecache
import logging
from contextlib import contextmanager
from datetime import datetime
from sentry_sdk._compat import urlparse, text_type, implements_str, int_types, PY2
if False:
    from typing import Any
    from typing import Dict
    from typing import Union
    from typing import Iterator
    from typing import Tuple
    from typing import Optional
    from typing import List
    from typing import Set
    from typing import Type
    from sentry_sdk.consts import ClientOptions
    ExcInfo = Tuple[Optional[Type[BaseException]], Optional[BaseException], Optional[Any]]
epoch = datetime(1970, 1, 1)
logger = logging.getLogger('sentry_sdk.errors')
MAX_STRING_LENGTH = 512
MAX_FORMAT_PARAM_LENGTH = 128

def _get_debug_hub():
    pass


@contextmanager
def capture_internal_exceptions():
    try:
        yield
    except Exception:
        hub = _get_debug_hub()
        if hub is not None:
            hub._capture_internal_exception(sys.exc_info())


def to_timestamp(value):
    return (value - epoch).total_seconds()


def event_hint_with_exc_info(exc_info = None):
    if exc_info is None:
        exc_info = sys.exc_info()
    else:
        exc_info = exc_info_from_error(exc_info)
    if exc_info[0] is None:
        exc_info = None
    return {'exc_info': exc_info}


class BadDsn(ValueError):
    pass


@implements_str

class Dsn(object):

    def __init__(self, value):
        if isinstance(value, Dsn):
            self.__dict__ = dict(value.__dict__)
            return
        parts = urlparse.urlsplit(text_type(value))
        if parts.scheme not in (u'http', u'https'):
            raise BadDsn('Unsupported scheme %r' % parts.scheme)
        self.scheme = parts.scheme
        self.host = parts.hostname
        self.port = parts.port
        if self.port is None:
            self.port = self.scheme == 'https' and 443 or 80
        self.public_key = parts.username
        if not self.public_key:
            raise BadDsn('Missing public key')
        self.secret_key = parts.password
        path = parts.path.rsplit('/', 1)
        try:
            self.project_id = text_type(int(path.pop()))
        except (ValueError, TypeError):
            raise BadDsn('Invalid project in DSN (%r)' % (parts.path or '')[1:])

        self.path = '/'.join(path) + '/'

    @property
    def netloc(self):
        rv = self.host
        if (self.scheme, self.port) not in (('http', 80), ('https', 443)):
            rv = '%s:%s' % (rv, self.port)
        return rv

    def to_auth(self, client = None):
        return Auth(scheme=self.scheme, host=self.netloc, path=self.path, project_id=self.project_id, public_key=self.public_key, secret_key=self.secret_key, client=client)

    def __str__(self):
        return '%s://%s%s@%s%s%s' % (self.scheme,
         self.public_key,
         self.secret_key and '@' + self.secret_key or '',
         self.netloc,
         self.path,
         self.project_id)


class Auth(object):

    def __init__(self, scheme, host, project_id, public_key, secret_key = None, version = 7, client = None, path = '/'):
        self.scheme = scheme
        self.host = host
        self.path = path
        self.project_id = project_id
        self.public_key = public_key
        self.secret_key = secret_key
        self.version = version
        self.client = client

    @property
    def store_api_url(self):
        return '%s://%s%sapi/%s/store/' % (self.scheme,
         self.host,
         self.path,
         self.project_id)

    def to_header(self, timestamp = None):
        rv = [('sentry_key', self.public_key), ('sentry_version', self.version)]
        if timestamp is not None:
            rv.append(('sentry_timestamp', str(to_timestamp(timestamp))))
        if self.client is not None:
            rv.append(('sentry_client', self.client))
        if self.secret_key is not None:
            rv.append(('sentry_secret', self.secret_key))
        return u'Sentry ' + u', '.join(('%s=%s' % (key, value) for key, value in rv))


class AnnotatedValue(object):

    def __init__(self, value, metadata):
        self.value = value
        self.metadata = metadata


def get_type_name(cls):
    return getattr(cls, '__qualname__', None) or getattr(cls, '__name__', None)


def get_type_module(cls):
    mod = getattr(cls, '__module__', None)
    if mod not in (None, 'builtins', '__builtins__'):
        return mod


def should_hide_frame(frame):
    try:
        mod = frame.f_globals['__name__']
        return mod.startswith('sentry_sdk.')
    except (AttributeError, KeyError):
        pass

    for flag_name in ('__traceback_hide__', '__tracebackhide__'):
        try:
            if frame.f_locals[flag_name]:
                return True
        except Exception:
            pass

    return False


def iter_stacks(tb):
    while tb is not None:
        if not should_hide_frame(tb.tb_frame):
            yield tb
        tb = tb.tb_next


def slim_string(value, length = MAX_STRING_LENGTH):
    if not value:
        return value
    if len(value) > length:
        return value[:length - 3] + '...'
    return value[:length]


def get_lines_from_file(filename, lineno, loader = None, module = None):
    context_lines = 5
    source = None
    if loader is not None and hasattr(loader, 'get_source'):
        try:
            source_str = loader.get_source(module)
        except (ImportError, IOError):
            source_str = None

        if source_str is not None:
            source = source_str.splitlines()
    if source is None:
        try:
            source = linecache.getlines(filename)
        except (OSError, IOError):
            return ([], None, [])

    if not source:
        return ([], None, [])
    lower_bound = max(0, lineno - context_lines)
    upper_bound = min(lineno + 1 + context_lines, len(source))
    try:
        pre_context = [ slim_string(line.strip('\r\n')) for line in source[lower_bound:lineno] ]
        context_line = slim_string(source[lineno].strip('\r\n'))
        post_context = [ slim_string(line.strip('\r\n')) for line in source[lineno + 1:upper_bound] ]
        return (pre_context, context_line, post_context)
    except IndexError:
        return ([], None, [])


def get_source_context(frame, tb_lineno):
    try:
        abs_path = frame.f_code.co_filename
    except Exception:
        abs_path = None

    try:
        module = frame.f_globals['__name__']
    except Exception:
        return ([], None, [])

    try:
        loader = frame.f_globals['__loader__']
    except Exception:
        loader = None

    lineno = tb_lineno - 1
    if lineno is not None and abs_path:
        return get_lines_from_file(abs_path, lineno, loader, module)
    return ([], None, [])


def safe_str(value):
    try:
        return text_type(value)
    except Exception:
        return safe_repr(value)


def safe_repr(value):
    try:
        rv = repr(value)
        if isinstance(rv, bytes):
            rv = rv.decode('utf-8', 'replace')
        try:
            return rv.encode('latin1').decode('unicode-escape')
        except Exception:
            return rv

    except Exception:
        return u'<broken repr>'


def filename_for_module(module, abs_path):
    try:
        if abs_path.endswith('.pyc'):
            abs_path = abs_path[:-1]
        base_module = module.split('.', 1)[0]
        if base_module == module:
            return os.path.basename(abs_path)
        base_module_path = sys.modules[base_module].__file__
        return abs_path.split(base_module_path.rsplit(os.sep, 2)[0], 1)[-1].lstrip(os.sep)
    except Exception:
        return abs_path


def serialize_frame(frame, tb_lineno = None, with_locals = True):
    f_code = getattr(frame, 'f_code', None)
    if f_code:
        abs_path = frame.f_code.co_filename
        function = frame.f_code.co_name
    else:
        abs_path = None
        function = None
    try:
        module = frame.f_globals['__name__']
    except Exception:
        module = None

    if tb_lineno is None:
        tb_lineno = frame.f_lineno
    pre_context, context_line, post_context = get_source_context(frame, tb_lineno)
    rv = {'filename': filename_for_module(module, abs_path) or None,
     'abs_path': os.path.abspath(abs_path) if abs_path else None,
     'function': function or '<unknown>',
     'module': module,
     'lineno': tb_lineno,
     'pre_context': pre_context,
     'context_line': context_line,
     'post_context': post_context}
    if with_locals:
        rv['vars'] = frame.f_locals
    return rv


def stacktrace_from_traceback(tb = None, with_locals = True):
    return {'frames': [ serialize_frame(tb.tb_frame, tb_lineno=tb.tb_lineno, with_locals=with_locals) for tb in iter_stacks(tb) ]}


def current_stacktrace(with_locals = True):
    __tracebackhide__ = True
    frames = []
    f = sys._getframe()
    while f is not None:
        if not should_hide_frame(f):
            frames.append(serialize_frame(f, with_locals=with_locals))
        f = f.f_back

    frames.reverse()
    return {'frames': frames}


def get_errno(exc_value):
    return getattr(exc_value, 'errno', None)


def single_exception_from_error_tuple(exc_type, exc_value, tb, client_options = None, mechanism = None):
    if exc_value is not None:
        errno = get_errno(exc_value)
    else:
        errno = None
    if errno is not None:
        mechanism = mechanism or {}
        mechanism.setdefault('meta', {}).setdefault('errno', {}).setdefault('number', errno)
    if client_options is None:
        with_locals = True
    else:
        with_locals = client_options['with_locals']
    return {'module': get_type_module(exc_type),
     'type': get_type_name(exc_type),
     'value': safe_str(exc_value),
     'mechanism': mechanism,
     'stacktrace': stacktrace_from_traceback(tb, with_locals)}


HAS_CHAINED_EXCEPTIONS = hasattr(Exception, '__suppress_context__')
if HAS_CHAINED_EXCEPTIONS:

    def walk_exception_chain(exc_info):
        exc_type, exc_value, tb = exc_info
        seen_exceptions = []
        seen_exception_ids = set()
        while exc_type is not None and exc_value is not None and id(exc_value) not in seen_exception_ids:
            yield (exc_type, exc_value, tb)
            seen_exceptions.append(exc_value)
            seen_exception_ids.add(id(exc_value))
            if exc_value.__suppress_context__:
                cause = exc_value.__cause__
            else:
                cause = exc_value.__context__
            if cause is None:
                break
            exc_type = type(cause)
            exc_value = cause
            tb = getattr(cause, '__traceback__', None)


else:

    def walk_exception_chain(exc_info):
        yield exc_info


def exceptions_from_error_tuple(exc_info, client_options = None, mechanism = None):
    exc_type, exc_value, tb = exc_info
    rv = []
    for exc_type, exc_value, tb in walk_exception_chain(exc_info):
        rv.append(single_exception_from_error_tuple(exc_type, exc_value, tb, client_options, mechanism))

    rv.reverse()
    return rv


def to_string(value):
    try:
        return text_type(value)
    except UnicodeDecodeError:
        return repr(value)[1:-1]


def iter_event_stacktraces(event):
    if 'stacktrace' in event:
        yield event['stacktrace']
    if 'threads' in event:
        for thread in event['threads'].get('values') or ():
            if 'stacktrace' in thread:
                yield thread['stacktrace']

    if 'exception' in event:
        for exception in event['exception'].get('values') or ():
            if 'stacktrace' in exception:
                yield exception['stacktrace']


def iter_event_frames(event):
    for stacktrace in iter_event_stacktraces(event):
        for frame in stacktrace.get('frames') or ():
            yield frame


def handle_in_app(event, in_app_exclude = None, in_app_include = None):
    for stacktrace in iter_event_stacktraces(event):
        handle_in_app_impl(stacktrace.get('frames'), in_app_exclude=in_app_exclude, in_app_include=in_app_include)

    return event


def handle_in_app_impl(frames, in_app_exclude, in_app_include):
    if not frames:
        return
    any_in_app = False
    for frame in frames:
        in_app = frame.get('in_app')
        if in_app is not None:
            if in_app:
                any_in_app = True
            continue
        module = frame.get('module')
        if not module:
            continue
        elif _module_in_set(module, in_app_include):
            frame['in_app'] = True
            any_in_app = True
        elif _module_in_set(module, in_app_exclude):
            frame['in_app'] = False

    if not any_in_app:
        for frame in frames:
            if frame.get('in_app') is None:
                frame['in_app'] = True

    return frames


def exc_info_from_error(error):
    if isinstance(error, tuple) and len(error) == 3:
        exc_type, exc_value, tb = error
    elif isinstance(error, BaseException):
        tb = getattr(error, '__traceback__', None)
        if tb is not None:
            exc_type = type(error)
            exc_value = error
        else:
            exc_type, exc_value, tb = sys.exc_info()
            if exc_value is not error:
                tb = None
                exc_value = error
                exc_type = type(error)
    else:
        raise ValueError()
    return (exc_type, exc_value, tb)


def event_from_exception(exc_info, client_options = None, mechanism = None):
    exc_info = exc_info_from_error(exc_info)
    hint = event_hint_with_exc_info(exc_info)
    return ({'level': 'error',
      'exception': {'values': exceptions_from_error_tuple(exc_info, client_options, mechanism)}}, hint)


def _module_in_set(name, set):
    if not set:
        return False
    for item in set or ():
        if item == name or name.startswith(item + '.'):
            return True

    return False


def strip_string(value, max_length = 512):
    if not value:
        return value
    length = len(value)
    if length > max_length:
        return AnnotatedValue(value=value[:max_length - 3] + u'...', metadata={'len': length,
         'rem': [['!limit',
                  'x',
                  max_length - 3,
                  max_length]]})
    return value


def format_and_strip(template, params, strip_string = strip_string, max_length = MAX_FORMAT_PARAM_LENGTH):
    chunks = template.split(u'%s')
    if not chunks:
        raise ValueError('No formatting placeholders found')
    params = list(reversed(params))
    rv_remarks = []
    rv_original_length = 0
    rv_length = 0
    rv = []

    def realign_remark(remark):
        return [ (rv_length + x if isinstance(x, int_types) and i < 4 else x) for i, x in enumerate(remark) ]

    for chunk in chunks[:-1]:
        rv.append(chunk)
        rv_length += len(chunk)
        rv_original_length += len(chunk)
        if not params:
            raise ValueError('Not enough params.')
        param = params.pop()
        stripped_param = strip_string(param, max_length=max_length)
        if isinstance(stripped_param, AnnotatedValue):
            rv_remarks.extend((realign_remark(remark) for remark in stripped_param.metadata['rem']))
            stripped_param = stripped_param.value
        rv_original_length += len(param)
        rv_length += len(stripped_param)
        rv.append(stripped_param)

    rv.append(chunks[-1])
    rv_length += len(chunks[-1])
    rv_original_length += len(chunks[-1])
    rv = u''.join(rv)
    if not rv_remarks:
        return rv
    return AnnotatedValue(value=rv, metadata={'len': rv_original_length,
     'rem': rv_remarks})


HAS_REAL_CONTEXTVARS = True
try:
    from contextvars import ContextVar
    if not PY2 and sys.version_info < (3, 7):
        import aiocontextvars
except ImportError:
    HAS_REAL_CONTEXTVARS = False
    from threading import local

    class ContextVar(object):

        def __init__(self, name):
            self._name = name
            self._local = local()

        def get(self, default):
            return getattr(self._local, 'value', default)

        def set(self, value):
            setattr(self._local, 'value', value)


def transaction_from_function(func):
    try:
        return '%s.%s.%s' % (func.im_class.__module__, func.im_class.__name__, func.__name__)
    except Exception:
        pass

    func_qualname = getattr(func, '__qualname__', None) or getattr(func, '__name__', None) or None
    if not func_qualname:
        return
    try:
        return '%s.%s' % (func.__module__, func_qualname)
    except Exception:
        pass

    return func_qualname
