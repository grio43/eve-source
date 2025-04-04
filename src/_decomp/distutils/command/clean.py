#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\distutils\command\clean.py
__revision__ = '$Id: clean.py 82110 2010-06-20 13:38:51Z kristjan.jonsson $'
import os
from distutils.core import Command
from distutils.dir_util import remove_tree
from distutils import log

class clean(Command):
    description = "clean up temporary files from 'build' command"
    user_options = [('build-base=', 'b', "base build directory (default: 'build.build-base')"),
     ('build-lib=', None, "build directory for all modules (default: 'build.build-lib')"),
     ('build-temp=', 't', "temporary build directory (default: 'build.build-temp')"),
     ('build-scripts=', None, "build directory for scripts (default: 'build.build-scripts')"),
     ('bdist-base=', None, 'temporary directory for built distributions'),
     ('all', 'a', 'remove all build output, not just temporary by-products')]
    boolean_options = ['all']

    def initialize_options(self):
        self.build_base = None
        self.build_lib = None
        self.build_temp = None
        self.build_scripts = None
        self.bdist_base = None
        self.all = None

    def finalize_options(self):
        self.set_undefined_options('build', ('build_base', 'build_base'), ('build_lib', 'build_lib'), ('build_scripts', 'build_scripts'), ('build_temp', 'build_temp'))
        self.set_undefined_options('bdist', ('bdist_base', 'bdist_base'))

    def run(self):
        if os.path.exists(self.build_temp):
            remove_tree(self.build_temp, dry_run=self.dry_run)
        else:
            log.debug("'%s' does not exist -- can't clean it", self.build_temp)
        if self.all:
            for directory in (self.build_lib, self.bdist_base, self.build_scripts):
                if os.path.exists(directory):
                    remove_tree(directory, dry_run=self.dry_run)
                else:
                    log.warn("'%s' does not exist -- can't clean it", directory)

        if not self.dry_run:
            try:
                os.rmdir(self.build_base)
                log.info("removing '%s'", self.build_base)
            except OSError:
                pass
