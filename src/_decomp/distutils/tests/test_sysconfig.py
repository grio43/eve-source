#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\distutils\tests\test_sysconfig.py
import os
import test
import unittest
import shutil
from distutils import sysconfig
from distutils.tests import support
from test.test_support import TESTFN

class SysconfigTestCase(support.EnvironGuard, unittest.TestCase):

    def setUp(self):
        super(SysconfigTestCase, self).setUp()
        self.makefile = None

    def tearDown(self):
        if self.makefile is not None:
            os.unlink(self.makefile)
        self.cleanup_testfn()
        super(SysconfigTestCase, self).tearDown()

    def cleanup_testfn(self):
        path = test.test_support.TESTFN
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)

    def test_get_python_lib(self):
        lib_dir = sysconfig.get_python_lib()
        self.assertNotEqual(sysconfig.get_python_lib(), sysconfig.get_python_lib(prefix=TESTFN))
        _sysconfig = __import__('sysconfig')
        res = sysconfig.get_python_lib(True, True)
        self.assertEqual(_sysconfig.get_path('platstdlib'), res)

    def test_get_python_inc(self):
        inc_dir = sysconfig.get_python_inc()
        self.assertTrue(os.path.isdir(inc_dir), inc_dir)
        python_h = os.path.join(inc_dir, 'Python.h')
        self.assertTrue(os.path.isfile(python_h), python_h)

    def test_parse_makefile_base(self):
        self.makefile = test.test_support.TESTFN
        fd = open(self.makefile, 'w')
        try:
            fd.write("CONFIG_ARGS=  '--arg1=optarg1' 'ENV=LIB'\n")
            fd.write('VAR=$OTHER\nOTHER=foo')
        finally:
            fd.close()

        d = sysconfig.parse_makefile(self.makefile)
        self.assertEqual(d, {'CONFIG_ARGS': "'--arg1=optarg1' 'ENV=LIB'",
         'OTHER': 'foo'})

    def test_parse_makefile_literal_dollar(self):
        self.makefile = test.test_support.TESTFN
        fd = open(self.makefile, 'w')
        try:
            fd.write("CONFIG_ARGS=  '--arg1=optarg1' 'ENV=\\$$LIB'\n")
            fd.write('VAR=$OTHER\nOTHER=foo')
        finally:
            fd.close()

        d = sysconfig.parse_makefile(self.makefile)
        self.assertEqual(d, {'CONFIG_ARGS': "'--arg1=optarg1' 'ENV=\\$LIB'",
         'OTHER': 'foo'})


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SysconfigTestCase))
    return suite


if __name__ == '__main__':
    test.test_support.run_unittest(test_suite())
