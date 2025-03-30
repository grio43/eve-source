#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\distutils\tests\support.py
import os
import shutil
import tempfile
from copy import deepcopy
import warnings
from distutils import log
from distutils.log import DEBUG, INFO, WARN, ERROR, FATAL
from distutils.core import Distribution

def capture_warnings(func):

    def _capture_warnings(*args, **kw):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            return func(*args, **kw)

    return _capture_warnings


class LoggingSilencer(object):

    def setUp(self):
        super(LoggingSilencer, self).setUp()
        self.threshold = log.set_threshold(log.FATAL)
        self._old_log = log.Log._log
        log.Log._log = self._log
        self.logs = []

    def tearDown(self):
        log.set_threshold(self.threshold)
        log.Log._log = self._old_log
        super(LoggingSilencer, self).tearDown()

    def _log(self, level, msg, args):
        if level not in (DEBUG,
         INFO,
         WARN,
         ERROR,
         FATAL):
            raise ValueError('%s wrong log level' % str(level))
        self.logs.append((level, msg, args))

    def get_logs(self, *levels):

        def _format(msg, args):
            if len(args) == 0:
                return msg
            return msg % args

        return [ _format(msg, args) for level, msg, args in self.logs if level in levels ]

    def clear_logs(self):
        self.logs = []


class TempdirManager(object):

    def setUp(self):
        super(TempdirManager, self).setUp()
        self.tempdirs = []

    def tearDown(self):
        super(TempdirManager, self).tearDown()
        while self.tempdirs:
            d = self.tempdirs.pop()
            shutil.rmtree(d, os.name in ('nt', 'cygwin'))

    def mkdtemp(self):
        d = tempfile.mkdtemp()
        self.tempdirs.append(d)
        return d

    def write_file(self, path, content = 'xxx'):
        if isinstance(path, (list, tuple)):
            path = os.path.join(*path)
        f = open(path, 'w')
        try:
            f.write(content)
        finally:
            f.close()

    def create_dist(self, pkg_name = 'foo', **kw):
        tmp_dir = self.mkdtemp()
        pkg_dir = os.path.join(tmp_dir, pkg_name)
        os.mkdir(pkg_dir)
        dist = Distribution(attrs=kw)
        return (pkg_dir, dist)


class DummyCommand:

    def __init__(self, **kwargs):
        for kw, val in kwargs.items():
            setattr(self, kw, val)

    def ensure_finalized(self):
        pass


class EnvironGuard(object):

    def setUp(self):
        super(EnvironGuard, self).setUp()
        self.old_environ = deepcopy(os.environ)

    def tearDown(self):
        for key, value in self.old_environ.items():
            if os.environ.get(key) != value:
                os.environ[key] = value

        for key in os.environ.keys():
            if key not in self.old_environ:
                del os.environ[key]

        super(EnvironGuard, self).tearDown()
