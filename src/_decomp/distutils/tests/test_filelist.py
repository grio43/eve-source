#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\distutils\tests\test_filelist.py
from os.path import join
import unittest
from test.test_support import captured_stdout
from distutils.filelist import glob_to_re, FileList
from distutils import debug
MANIFEST_IN = 'include ok\ninclude xo\nexclude xo\ninclude foo.tmp\nglobal-include *.x\nglobal-include *.txt\nglobal-exclude *.tmp\nrecursive-include f *.oo\nrecursive-exclude global *.x\ngraft dir\nprune dir3\n'

class FileListTestCase(unittest.TestCase):

    def test_glob_to_re(self):
        self.assertEqual(glob_to_re('foo*'), 'foo[^/]*\\Z(?ms)')
        self.assertEqual(glob_to_re('foo?'), 'foo[^/]\\Z(?ms)')
        self.assertEqual(glob_to_re('foo??'), 'foo[^/][^/]\\Z(?ms)')
        self.assertEqual(glob_to_re('foo\\\\*'), 'foo\\\\\\\\[^/]*\\Z(?ms)')
        self.assertEqual(glob_to_re('foo\\\\\\*'), 'foo\\\\\\\\\\\\[^/]*\\Z(?ms)')
        self.assertEqual(glob_to_re('foo????'), 'foo[^/][^/][^/][^/]\\Z(?ms)')
        self.assertEqual(glob_to_re('foo\\\\??'), 'foo\\\\\\\\[^/][^/]\\Z(?ms)')

    def test_process_template_line(self):
        file_list = FileList()
        file_list.allfiles = ['foo.tmp',
         'ok',
         'xo',
         'four.txt',
         join('global', 'one.txt'),
         join('global', 'two.txt'),
         join('global', 'files.x'),
         join('global', 'here.tmp'),
         join('f', 'o', 'f.oo'),
         join('dir', 'graft-one'),
         join('dir', 'dir2', 'graft2'),
         join('dir3', 'ok'),
         join('dir3', 'sub', 'ok.txt')]
        for line in MANIFEST_IN.split('\n'):
            if line.strip() == '':
                continue
            file_list.process_template_line(line)

        wanted = ['ok',
         'four.txt',
         join('global', 'one.txt'),
         join('global', 'two.txt'),
         join('f', 'o', 'f.oo'),
         join('dir', 'graft-one'),
         join('dir', 'dir2', 'graft2')]
        self.assertEqual(file_list.files, wanted)

    def test_debug_print(self):
        file_list = FileList()
        with captured_stdout() as stdout:
            file_list.debug_print('xxx')
        stdout.seek(0)
        self.assertEqual(stdout.read(), '')
        debug.DEBUG = True
        try:
            with captured_stdout() as stdout:
                file_list.debug_print('xxx')
            stdout.seek(0)
            self.assertEqual(stdout.read(), 'xxx\n')
        finally:
            debug.DEBUG = False


def test_suite():
    return unittest.makeSuite(FileListTestCase)


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
