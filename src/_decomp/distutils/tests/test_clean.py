#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\distutils\tests\test_clean.py
import sys
import os
import unittest
import getpass
from distutils.command.clean import clean
from distutils.tests import support

class cleanTestCase(support.TempdirManager, support.LoggingSilencer, unittest.TestCase):

    def test_simple_run(self):
        pkg_dir, dist = self.create_dist()
        cmd = clean(dist)
        dirs = [ (d, os.path.join(pkg_dir, d)) for d in ('build_temp', 'build_lib', 'bdist_base', 'build_scripts', 'build_base') ]
        for name, path in dirs:
            os.mkdir(path)
            setattr(cmd, name, path)
            if name == 'build_base':
                continue
            for f in ('one', 'two', 'three'):
                self.write_file(os.path.join(path, f))

        cmd.all = 1
        cmd.ensure_finalized()
        cmd.run()
        for name, path in dirs:
            self.assertTrue(not os.path.exists(path), '%s was not removed' % path)

        cmd.all = 1
        cmd.ensure_finalized()
        cmd.run()


def test_suite():
    return unittest.makeSuite(cleanTestCase)


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
