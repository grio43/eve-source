#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\distutils\tests\test_bdist_msi.py
import unittest
import sys
from test.test_support import run_unittest
from distutils.tests import support

@unittest.skipUnless(sys.platform == 'win32', 'These tests are only for win32')

class BDistMSITestCase(support.TempdirManager, support.LoggingSilencer, unittest.TestCase):

    def test_minial(self):
        from distutils.command.bdist_msi import bdist_msi
        pkg_pth, dist = self.create_dist()
        cmd = bdist_msi(dist)
        cmd.ensure_finalized()


def test_suite():
    return unittest.makeSuite(BDistMSITestCase)


if __name__ == '__main__':
    run_unittest(test_suite())
