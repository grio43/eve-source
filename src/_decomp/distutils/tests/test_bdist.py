#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\distutils\tests\test_bdist.py
import unittest
import sys
import os
import tempfile
import shutil
from test.test_support import run_unittest
from distutils.core import Distribution
from distutils.command.bdist import bdist
from distutils.tests import support
from distutils.spawn import find_executable
from distutils import spawn
from distutils.errors import DistutilsExecError

class BuildTestCase(support.TempdirManager, unittest.TestCase):

    def test_formats(self):
        pkg_pth, dist = self.create_dist()
        cmd = bdist(dist)
        cmd.formats = ['msi']
        cmd.ensure_finalized()
        self.assertEqual(cmd.formats, ['msi'])
        formats = ['rpm',
         'zip',
         'gztar',
         'bztar',
         'ztar',
         'tar',
         'wininst',
         'msi']
        formats.sort()
        founded = cmd.format_command.keys()
        founded.sort()
        self.assertEqual(founded, formats)


def test_suite():
    return unittest.makeSuite(BuildTestCase)


if __name__ == '__main__':
    run_unittest(test_suite())
