#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\distutils\tests\test_build_scripts.py
import os
import unittest
from distutils.command.build_scripts import build_scripts
from distutils.core import Distribution
import sysconfig
from distutils.tests import support

class BuildScriptsTestCase(support.TempdirManager, support.LoggingSilencer, unittest.TestCase):

    def test_default_settings(self):
        cmd = self.get_build_scripts_cmd('/foo/bar', [])
        self.assertTrue(not cmd.force)
        self.assertTrue(cmd.build_dir is None)
        cmd.finalize_options()
        self.assertTrue(cmd.force)
        self.assertEqual(cmd.build_dir, '/foo/bar')

    def test_build(self):
        source = self.mkdtemp()
        target = self.mkdtemp()
        expected = self.write_sample_scripts(source)
        cmd = self.get_build_scripts_cmd(target, [ os.path.join(source, fn) for fn in expected ])
        cmd.finalize_options()
        cmd.run()
        built = os.listdir(target)
        for name in expected:
            self.assertTrue(name in built)

    def get_build_scripts_cmd(self, target, scripts):
        import sys
        dist = Distribution()
        dist.scripts = scripts
        dist.command_obj['build'] = support.DummyCommand(build_scripts=target, force=1, executable=sys.executable)
        return build_scripts(dist)

    def write_sample_scripts(self, dir):
        expected = []
        expected.append('script1.py')
        self.write_script(dir, 'script1.py', '#! /usr/bin/env python2.3\n# bogus script w/ Python sh-bang\npass\n')
        expected.append('script2.py')
        self.write_script(dir, 'script2.py', '#!/usr/bin/python\n# bogus script w/ Python sh-bang\npass\n')
        expected.append('shell.sh')
        self.write_script(dir, 'shell.sh', '#!/bin/sh\n# bogus shell script w/ sh-bang\nexit 0\n')
        return expected

    def write_script(self, dir, name, text):
        f = open(os.path.join(dir, name), 'w')
        try:
            f.write(text)
        finally:
            f.close()

    def test_version_int(self):
        source = self.mkdtemp()
        target = self.mkdtemp()
        expected = self.write_sample_scripts(source)
        cmd = self.get_build_scripts_cmd(target, [ os.path.join(source, fn) for fn in expected ])
        cmd.finalize_options()
        old = sysconfig.get_config_vars().get('VERSION')
        sysconfig._CONFIG_VARS['VERSION'] = 4
        try:
            cmd.run()
        finally:
            if old is not None:
                sysconfig._CONFIG_VARS['VERSION'] = old

        built = os.listdir(target)
        for name in expected:
            self.assertTrue(name in built)


def test_suite():
    return unittest.makeSuite(BuildScriptsTestCase)


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
