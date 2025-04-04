#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\distutils\tests\test_register.py
import sys
import os
import unittest
import getpass
import urllib2
import warnings
from test.test_support import check_warnings
from distutils.command import register as register_module
from distutils.command.register import register
from distutils.core import Distribution
from distutils.errors import DistutilsSetupError
from distutils.tests import support
from distutils.tests.test_config import PYPIRC, PyPIRCCommandTestCase
PYPIRC_NOPASSWORD = '[distutils]\n\nindex-servers =\n    server1\n\n[server1]\nusername:me\n'
WANTED_PYPIRC = '[distutils]\nindex-servers =\n    pypi\n\n[pypi]\nusername:tarek\npassword:password\n'

class RawInputs(object):

    def __init__(self, *answers):
        self.answers = answers
        self.index = 0

    def __call__(self, prompt = ''):
        try:
            return self.answers[self.index]
        finally:
            self.index += 1


class FakeOpener(object):

    def __init__(self):
        self.reqs = []

    def __call__(self, *args):
        return self

    def open(self, req):
        self.reqs.append(req)
        return self

    def read(self):
        return 'xxx'


class RegisterTestCase(PyPIRCCommandTestCase):

    def setUp(self):
        super(RegisterTestCase, self).setUp()
        self._old_getpass = getpass.getpass

        def _getpass(prompt):
            return 'password'

        getpass.getpass = _getpass
        self.old_opener = urllib2.build_opener
        self.conn = urllib2.build_opener = FakeOpener()

    def tearDown(self):
        getpass.getpass = self._old_getpass
        urllib2.build_opener = self.old_opener
        super(RegisterTestCase, self).tearDown()

    def _get_cmd(self, metadata = None):
        if metadata is None:
            metadata = {'url': 'xxx',
             'author': 'xxx',
             'author_email': 'xxx',
             'name': 'xxx',
             'version': 'xxx'}
        pkg_info, dist = self.create_dist(**metadata)
        return register(dist)

    def test_create_pypirc(self):
        cmd = self._get_cmd()
        self.assertTrue(not os.path.exists(self.rc))
        inputs = RawInputs('1', 'tarek', 'y')
        register_module.raw_input = inputs.__call__
        try:
            cmd.run()
        finally:
            del register_module.raw_input

        self.assertTrue(os.path.exists(self.rc))
        f = open(self.rc)
        try:
            content = f.read()
            self.assertEqual(content, WANTED_PYPIRC)
        finally:
            f.close()

        def _no_way(prompt = ''):
            raise AssertionError(prompt)

        register_module.raw_input = _no_way
        cmd.show_response = 1
        cmd.run()
        self.assertTrue(self.conn.reqs, 2)
        req1 = dict(self.conn.reqs[0].headers)
        req2 = dict(self.conn.reqs[1].headers)
        self.assertEqual(req2['Content-length'], req1['Content-length'])
        self.assertTrue('xxx' in self.conn.reqs[1].data)

    def test_password_not_in_file(self):
        self.write_file(self.rc, PYPIRC_NOPASSWORD)
        cmd = self._get_cmd()
        cmd._set_config()
        cmd.finalize_options()
        cmd.send_metadata()
        self.assertEqual(cmd.distribution.password, 'password')

    def test_registering(self):
        cmd = self._get_cmd()
        inputs = RawInputs('2', 'tarek', 'tarek@ziade.org')
        register_module.raw_input = inputs.__call__
        try:
            cmd.run()
        finally:
            del register_module.raw_input

        self.assertTrue(self.conn.reqs, 1)
        req = self.conn.reqs[0]
        headers = dict(req.headers)
        self.assertEqual(headers['Content-length'], '608')
        self.assertTrue('tarek' in req.data)

    def test_password_reset(self):
        cmd = self._get_cmd()
        inputs = RawInputs('3', 'tarek@ziade.org')
        register_module.raw_input = inputs.__call__
        try:
            cmd.run()
        finally:
            del register_module.raw_input

        self.assertTrue(self.conn.reqs, 1)
        req = self.conn.reqs[0]
        headers = dict(req.headers)
        self.assertEqual(headers['Content-length'], '290')
        self.assertTrue('tarek' in req.data)

    def test_strict(self):
        cmd = self._get_cmd({})
        cmd.ensure_finalized()
        cmd.strict = 1
        self.assertRaises(DistutilsSetupError, cmd.run)
        try:
            import docutils
        except ImportError:
            return

        metadata = {'url': 'xxx',
         'author': 'xxx',
         'author_email': u'\xc3\xa9x\xc3\xa9x\xc3\xa9',
         'name': 'xxx',
         'version': 'xxx',
         'long_description': 'title\n==\n\ntext'}
        cmd = self._get_cmd(metadata)
        cmd.ensure_finalized()
        cmd.strict = 1
        self.assertRaises(DistutilsSetupError, cmd.run)
        metadata['long_description'] = 'title\n=====\n\ntext'
        cmd = self._get_cmd(metadata)
        cmd.ensure_finalized()
        cmd.strict = 1
        inputs = RawInputs('1', 'tarek', 'y')
        register_module.raw_input = inputs.__call__
        try:
            cmd.run()
        finally:
            del register_module.raw_input

        cmd = self._get_cmd()
        cmd.ensure_finalized()
        inputs = RawInputs('1', 'tarek', 'y')
        register_module.raw_input = inputs.__call__
        try:
            cmd.run()
        finally:
            del register_module.raw_input

    def test_check_metadata_deprecated(self):
        cmd = self._get_cmd()
        with check_warnings() as w:
            warnings.simplefilter('always')
            cmd.check_metadata()
            self.assertEqual(len(w.warnings), 1)


def test_suite():
    return unittest.makeSuite(RegisterTestCase)


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
