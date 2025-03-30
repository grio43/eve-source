#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\distutils\tests\test_util.py
import sys
import unittest
from distutils.errors import DistutilsPlatformError, DistutilsByteCompileError
from distutils.util import byte_compile

class UtilTestCase(unittest.TestCase):

    def test_dont_write_bytecode(self):
        old_dont_write_bytecode = sys.dont_write_bytecode
        sys.dont_write_bytecode = True
        try:
            self.assertRaises(DistutilsByteCompileError, byte_compile, [])
        finally:
            sys.dont_write_bytecode = old_dont_write_bytecode


def test_suite():
    return unittest.makeSuite(UtilTestCase)


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
