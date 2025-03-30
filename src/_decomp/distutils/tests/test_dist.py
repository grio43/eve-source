#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\distutils\tests\test_dist.py
import os
import StringIO
import sys
import unittest
import warnings
import textwrap
from distutils.dist import Distribution, fix_help_options, DistributionMetadata
from distutils.cmd import Command
import distutils.dist
from test.test_support import TESTFN, captured_stdout
from distutils.tests import support

class test_dist(Command):
    user_options = [('sample-option=', 'S', 'help text')]

    def initialize_options(self):
        self.sample_option = None


class TestDistribution(Distribution):

    def find_config_files(self):
        return self._config_files


class DistributionTestCase(support.TempdirManager, support.LoggingSilencer, support.EnvironGuard, unittest.TestCase):

    def setUp(self):
        super(DistributionTestCase, self).setUp()
        self.argv = (sys.argv, sys.argv[:])
        del sys.argv[1:]

    def tearDown(self):
        sys.argv = self.argv[0]
        sys.argv[:] = self.argv[1]
        super(DistributionTestCase, self).tearDown()

    def create_distribution(self, configfiles = ()):
        d = TestDistribution()
        d._config_files = configfiles
        d.parse_config_files()
        d.parse_command_line()
        return d

    def test_debug_mode(self):
        with open(TESTFN, 'w') as f:
            f.write('[global]')
            f.write('command_packages = foo.bar, splat')
        files = [TESTFN]
        sys.argv.append('build')
        with captured_stdout() as stdout:
            self.create_distribution(files)
        stdout.seek(0)
        self.assertEqual(stdout.read(), '')
        distutils.dist.DEBUG = True
        try:
            with captured_stdout() as stdout:
                self.create_distribution(files)
            stdout.seek(0)
            self.assertEqual(stdout.read(), '')
        finally:
            distutils.dist.DEBUG = False

    def test_command_packages_unspecified(self):
        sys.argv.append('build')
        d = self.create_distribution()
        self.assertEqual(d.get_command_packages(), ['distutils.command'])

    def test_command_packages_cmdline(self):
        from distutils.tests.test_dist import test_dist
        sys.argv.extend(['--command-packages',
         'foo.bar,distutils.tests',
         'test_dist',
         '-Ssometext'])
        d = self.create_distribution()
        self.assertEqual(d.get_command_packages(), ['distutils.command', 'foo.bar', 'distutils.tests'])
        cmd = d.get_command_obj('test_dist')
        self.assertTrue(isinstance(cmd, test_dist))
        self.assertEqual(cmd.sample_option, 'sometext')

    def test_command_packages_configfile(self):
        sys.argv.append('build')
        self.addCleanup(os.unlink, TESTFN)
        f = open(TESTFN, 'w')
        try:
            print >> f, '[global]'
            print >> f, 'command_packages = foo.bar, splat'
        finally:
            f.close()

        d = self.create_distribution([TESTFN])
        self.assertEqual(d.get_command_packages(), ['distutils.command', 'foo.bar', 'splat'])
        sys.argv[1:] = ['--command-packages', 'spork', 'build']
        d = self.create_distribution([TESTFN])
        self.assertEqual(d.get_command_packages(), ['distutils.command', 'spork'])
        sys.argv[1:] = ['--command-packages', '', 'build']
        d = self.create_distribution([TESTFN])
        self.assertEqual(d.get_command_packages(), ['distutils.command'])

    def test_write_pkg_file(self):
        tmp_dir = self.mkdtemp()
        my_file = os.path.join(tmp_dir, 'f')
        klass = Distribution
        dist = klass(attrs={'author': u'Mister Caf\xe9',
         'name': 'my.package',
         'maintainer': u'Caf\xe9 Junior',
         'description': u'Caf\xe9 torr\xe9fi\xe9',
         'long_description': u'H\xe9h\xe9h\xe9'})
        dist.metadata.write_pkg_file(open(my_file, 'w'))
        dist = klass(attrs={'author': 'Mister Cafe',
         'name': 'my.package',
         'maintainer': 'Cafe Junior',
         'description': 'Cafe torrefie',
         'long_description': 'Hehehe'})
        my_file2 = os.path.join(tmp_dir, 'f2')
        dist.metadata.write_pkg_file(open(my_file, 'w'))

    def test_empty_options(self):
        klass = Distribution
        warns = []

        def _warn(msg):
            warns.append(msg)

        old_warn = warnings.warn
        warnings.warn = _warn
        try:
            dist = klass(attrs={'author': 'xxx',
             'name': 'xxx',
             'version': 'xxx',
             'url': 'xxxx',
             'options': {}})
        finally:
            warnings.warn = old_warn

        self.assertEqual(len(warns), 0)

    def test_finalize_options(self):
        attrs = {'keywords': 'one,two',
         'platforms': 'one,two'}
        dist = Distribution(attrs=attrs)
        dist.finalize_options()
        self.assertEqual(dist.metadata.platforms, ['one', 'two'])
        self.assertEqual(dist.metadata.keywords, ['one', 'two'])

    def test_get_command_packages(self):
        dist = Distribution()
        self.assertEqual(dist.command_packages, None)
        cmds = dist.get_command_packages()
        self.assertEqual(cmds, ['distutils.command'])
        self.assertEqual(dist.command_packages, ['distutils.command'])
        dist.command_packages = 'one,two'
        cmds = dist.get_command_packages()
        self.assertEqual(cmds, ['distutils.command', 'one', 'two'])

    def test_announce(self):
        dist = Distribution()
        args = ('ok',)
        kwargs = {'level': 'ok2'}
        self.assertRaises(ValueError, dist.announce, args, kwargs)

    def test_find_config_files_disable(self):
        temp_home = self.mkdtemp()
        if os.name == 'posix':
            user_filename = os.path.join(temp_home, '.pydistutils.cfg')
        else:
            user_filename = os.path.join(temp_home, 'pydistutils.cfg')
        with open(user_filename, 'w') as f:
            f.write('[distutils]\n')

        def _expander(path):
            return temp_home

        old_expander = os.path.expanduser
        os.path.expanduser = _expander
        try:
            d = distutils.dist.Distribution()
            all_files = d.find_config_files()
            d = distutils.dist.Distribution(attrs={'script_args': ['--no-user-cfg']})
            files = d.find_config_files()
        finally:
            os.path.expanduser = old_expander

        self.assertEqual(len(all_files) - 1, len(files))


class MetadataTestCase(support.TempdirManager, support.EnvironGuard, unittest.TestCase):

    def setUp(self):
        super(MetadataTestCase, self).setUp()
        self.argv = (sys.argv, sys.argv[:])

    def tearDown(self):
        sys.argv = self.argv[0]
        sys.argv[:] = self.argv[1]
        super(MetadataTestCase, self).tearDown()

    def test_simple_metadata(self):
        attrs = {'name': 'package',
         'version': '1.0'}
        dist = Distribution(attrs)
        meta = self.format_metadata(dist)
        self.assertTrue('Metadata-Version: 1.0' in meta)
        self.assertTrue('provides:' not in meta.lower())
        self.assertTrue('requires:' not in meta.lower())
        self.assertTrue('obsoletes:' not in meta.lower())

    def test_provides(self):
        attrs = {'name': 'package',
         'version': '1.0',
         'provides': ['package', 'package.sub']}
        dist = Distribution(attrs)
        self.assertEqual(dist.metadata.get_provides(), ['package', 'package.sub'])
        self.assertEqual(dist.get_provides(), ['package', 'package.sub'])
        meta = self.format_metadata(dist)
        self.assertTrue('Metadata-Version: 1.1' in meta)
        self.assertTrue('requires:' not in meta.lower())
        self.assertTrue('obsoletes:' not in meta.lower())

    def test_provides_illegal(self):
        self.assertRaises(ValueError, Distribution, {'name': 'package',
         'version': '1.0',
         'provides': ['my.pkg (splat)']})

    def test_requires(self):
        attrs = {'name': 'package',
         'version': '1.0',
         'requires': ['other', 'another (==1.0)']}
        dist = Distribution(attrs)
        self.assertEqual(dist.metadata.get_requires(), ['other', 'another (==1.0)'])
        self.assertEqual(dist.get_requires(), ['other', 'another (==1.0)'])
        meta = self.format_metadata(dist)
        self.assertTrue('Metadata-Version: 1.1' in meta)
        self.assertTrue('provides:' not in meta.lower())
        self.assertTrue('Requires: other' in meta)
        self.assertTrue('Requires: another (==1.0)' in meta)
        self.assertTrue('obsoletes:' not in meta.lower())

    def test_requires_illegal(self):
        self.assertRaises(ValueError, Distribution, {'name': 'package',
         'version': '1.0',
         'requires': ['my.pkg (splat)']})

    def test_obsoletes(self):
        attrs = {'name': 'package',
         'version': '1.0',
         'obsoletes': ['other', 'another (<1.0)']}
        dist = Distribution(attrs)
        self.assertEqual(dist.metadata.get_obsoletes(), ['other', 'another (<1.0)'])
        self.assertEqual(dist.get_obsoletes(), ['other', 'another (<1.0)'])
        meta = self.format_metadata(dist)
        self.assertTrue('Metadata-Version: 1.1' in meta)
        self.assertTrue('provides:' not in meta.lower())
        self.assertTrue('requires:' not in meta.lower())
        self.assertTrue('Obsoletes: other' in meta)
        self.assertTrue('Obsoletes: another (<1.0)' in meta)

    def test_obsoletes_illegal(self):
        self.assertRaises(ValueError, Distribution, {'name': 'package',
         'version': '1.0',
         'obsoletes': ['my.pkg (splat)']})

    def format_metadata(self, dist):
        sio = StringIO.StringIO()
        dist.metadata.write_pkg_file(sio)
        return sio.getvalue()

    def test_custom_pydistutils(self):
        if os.name == 'posix':
            user_filename = '.pydistutils.cfg'
        else:
            user_filename = 'pydistutils.cfg'
        temp_dir = self.mkdtemp()
        user_filename = os.path.join(temp_dir, user_filename)
        f = open(user_filename, 'w')
        try:
            f.write('.')
        finally:
            f.close()

        try:
            dist = Distribution()
            if sys.platform in ('linux', 'darwin'):
                os.environ['HOME'] = temp_dir
                files = dist.find_config_files()
                self.assertTrue(user_filename in files)
            if sys.platform == 'win32':
                os.environ['HOME'] = temp_dir
                files = dist.find_config_files()
                self.assertTrue(user_filename in files, '%r not found in %r' % (user_filename, files))
        finally:
            os.remove(user_filename)

    def test_fix_help_options(self):
        help_tuples = [('a', 'b', 'c', 'd'), (1, 2, 3, 4)]
        fancy_options = fix_help_options(help_tuples)
        self.assertEqual(fancy_options[0], ('a', 'b', 'c'))
        self.assertEqual(fancy_options[1], (1, 2, 3))

    def test_show_help(self):
        dist = Distribution()
        sys.argv = []
        dist.help = 1
        dist.script_name = 'setup.py'
        with captured_stdout() as s:
            dist.parse_command_line()
        output = [ line for line in s.getvalue().split('\n') if line.strip() != '' ]
        self.assertTrue(len(output) > 0)

    def test_long_description(self):
        long_desc = textwrap.dedent('        example::\n              We start here\n            and continue here\n          and end here.')
        attrs = {'name': 'package',
         'version': '1.0',
         'long_description': long_desc}
        dist = distutils.dist.Distribution(attrs)
        meta = self.format_metadata(dist)
        meta = meta.replace('\n' + '        ', '\n')
        self.assertTrue(long_desc in meta)

    def test_read_metadata(self):
        attrs = {'name': 'package',
         'version': '1.0',
         'long_description': 'desc',
         'description': 'xxx',
         'download_url': 'http://example.com',
         'keywords': ['one', 'two'],
         'requires': ['foo']}
        dist = Distribution(attrs)
        metadata = dist.metadata
        PKG_INFO = StringIO.StringIO()
        metadata.write_pkg_file(PKG_INFO)
        PKG_INFO.seek(0)
        metadata.read_pkg_file(PKG_INFO)
        self.assertEqual(metadata.name, 'package')
        self.assertEqual(metadata.version, '1.0')
        self.assertEqual(metadata.description, 'xxx')
        self.assertEqual(metadata.download_url, 'http://example.com')
        self.assertEqual(metadata.keywords, ['one', 'two'])
        self.assertEqual(metadata.platforms, ['UNKNOWN'])
        self.assertEqual(metadata.obsoletes, None)
        self.assertEqual(metadata.requires, ['foo'])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DistributionTestCase))
    suite.addTest(unittest.makeSuite(MetadataTestCase))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
