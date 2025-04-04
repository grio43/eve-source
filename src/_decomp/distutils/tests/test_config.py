#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\distutils\tests\test_config.py
import sys
import os
import unittest
import tempfile
import shutil
from distutils.core import PyPIRCCommand
from distutils.core import Distribution
from distutils.log import set_threshold
from distutils.log import WARN
from distutils.tests import support
PYPIRC = '[distutils]\n\nindex-servers =\n    server1\n    server2\n\n[server1]\nusername:me\npassword:secret\n\n[server2]\nusername:meagain\npassword: secret\nrealm:acme\nrepository:http://another.pypi/\n'
PYPIRC_OLD = '[server-login]\nusername:tarek\npassword:secret\n'
WANTED = '[distutils]\nindex-servers =\n    pypi\n\n[pypi]\nusername:tarek\npassword:xxx\n'

class PyPIRCCommandTestCase(support.TempdirManager, support.LoggingSilencer, support.EnvironGuard, unittest.TestCase):

    def setUp(self):
        super(PyPIRCCommandTestCase, self).setUp()
        self.tmp_dir = self.mkdtemp()
        os.environ['HOME'] = self.tmp_dir
        self.rc = os.path.join(self.tmp_dir, '.pypirc')
        self.dist = Distribution()

        class command(PyPIRCCommand):

            def __init__(self, dist):
                PyPIRCCommand.__init__(self, dist)

            def initialize_options(self):
                pass

            finalize_options = initialize_options

        self._cmd = command
        self.old_threshold = set_threshold(WARN)

    def tearDown(self):
        set_threshold(self.old_threshold)
        super(PyPIRCCommandTestCase, self).tearDown()

    def test_server_registration(self):
        self.write_file(self.rc, PYPIRC)
        cmd = self._cmd(self.dist)
        config = cmd._read_pypirc()
        config = config.items()
        config.sort()
        waited = [('password', 'secret'),
         ('realm', 'pypi'),
         ('repository', 'http://pypi.python.org/pypi'),
         ('server', 'server1'),
         ('username', 'me')]
        self.assertEqual(config, waited)
        self.write_file(self.rc, PYPIRC_OLD)
        config = cmd._read_pypirc()
        config = config.items()
        config.sort()
        waited = [('password', 'secret'),
         ('realm', 'pypi'),
         ('repository', 'http://pypi.python.org/pypi'),
         ('server', 'server-login'),
         ('username', 'tarek')]
        self.assertEqual(config, waited)

    def test_server_empty_registration(self):
        cmd = self._cmd(self.dist)
        rc = cmd._get_rc_file()
        self.assertTrue(not os.path.exists(rc))
        cmd._store_pypirc('tarek', 'xxx')
        self.assertTrue(os.path.exists(rc))
        f = open(rc)
        try:
            content = f.read()
            self.assertEqual(content, WANTED)
        finally:
            f.close()


def test_suite():
    return unittest.makeSuite(PyPIRCCommandTestCase)


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
