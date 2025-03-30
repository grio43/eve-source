#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\distutils\tests\test_bdist_rpm.py
import unittest
import sys
import os
import tempfile
import shutil
from test.test_support import run_unittest
from distutils.core import Distribution
from distutils.command.bdist_rpm import bdist_rpm
from distutils.tests import support
from distutils.spawn import find_executable
from distutils import spawn
from distutils.errors import DistutilsExecError
SETUP_PY = "from distutils.core import setup\nimport foo\n\nsetup(name='foo', version='0.1', py_modules=['foo'],\n      url='xxx', author='xxx', author_email='xxx')\n\n"

class BuildRpmTestCase(support.TempdirManager, support.LoggingSilencer, unittest.TestCase):

    def setUp(self):
        super(BuildRpmTestCase, self).setUp()
        self.old_location = os.getcwd()
        self.old_sys_argv = (sys.argv, sys.argv[:])

    def tearDown(self):
        os.chdir(self.old_location)
        sys.argv = self.old_sys_argv[0]
        sys.argv[:] = self.old_sys_argv[1]
        super(BuildRpmTestCase, self).tearDown()

    def test_quiet(self):
        if sys.platform != 'linux2':
            return
        if find_executable('rpm') is None or find_executable('rpmbuild') is None:
            return
        tmp_dir = self.mkdtemp()
        pkg_dir = os.path.join(tmp_dir, 'foo')
        os.mkdir(pkg_dir)
        self.write_file((pkg_dir, 'setup.py'), SETUP_PY)
        self.write_file((pkg_dir, 'foo.py'), '#')
        self.write_file((pkg_dir, 'MANIFEST.in'), 'include foo.py')
        self.write_file((pkg_dir, 'README'), '')
        dist = Distribution({'name': 'foo',
         'version': '0.1',
         'py_modules': ['foo'],
         'url': 'xxx',
         'author': 'xxx',
         'author_email': 'xxx'})
        dist.script_name = 'setup.py'
        os.chdir(pkg_dir)
        sys.argv = ['setup.py']
        cmd = bdist_rpm(dist)
        cmd.fix_python = True
        cmd.quiet = 1
        cmd.ensure_finalized()
        cmd.run()
        dist_created = os.listdir(os.path.join(pkg_dir, 'dist'))
        self.assertTrue('foo-0.1-1.noarch.rpm' in dist_created)

    def test_no_optimize_flag(self):
        if sys.platform != 'linux2':
            return
        if find_executable('rpm') is None or find_executable('rpmbuild') is None:
            return
        tmp_dir = self.mkdtemp()
        pkg_dir = os.path.join(tmp_dir, 'foo')
        os.mkdir(pkg_dir)
        self.write_file((pkg_dir, 'setup.py'), SETUP_PY)
        self.write_file((pkg_dir, 'foo.py'), '#')
        self.write_file((pkg_dir, 'MANIFEST.in'), 'include foo.py')
        self.write_file((pkg_dir, 'README'), '')
        dist = Distribution({'name': 'foo',
         'version': '0.1',
         'py_modules': ['foo'],
         'url': 'xxx',
         'author': 'xxx',
         'author_email': 'xxx'})
        dist.script_name = 'setup.py'
        os.chdir(pkg_dir)
        sys.argv = ['setup.py']
        cmd = bdist_rpm(dist)
        cmd.fix_python = True
        cmd.quiet = 1
        cmd.ensure_finalized()
        cmd.run()
        dist_created = os.listdir(os.path.join(pkg_dir, 'dist'))
        self.assertTrue('foo-0.1-1.noarch.rpm' in dist_created)
        os.remove(os.path.join(pkg_dir, 'dist', 'foo-0.1-1.noarch.rpm'))


def test_suite():
    return unittest.makeSuite(BuildRpmTestCase)


if __name__ == '__main__':
    run_unittest(test_suite())
