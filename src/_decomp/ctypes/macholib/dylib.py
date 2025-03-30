#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\ctypes\macholib\dylib.py
import re
__all__ = ['dylib_info']
DYLIB_RE = re.compile('(?x)\n(?P<location>^.*)(?:^|/)\n(?P<name>\n    (?P<shortname>\\w+?)\n    (?:\\.(?P<version>[^._]+))?\n    (?:_(?P<suffix>[^._]+))?\n    \\.dylib$\n)\n')

def dylib_info(filename):
    is_dylib = DYLIB_RE.match(filename)
    if not is_dylib:
        return None
    return is_dylib.groupdict()


def test_dylib_info():

    def d(location = None, name = None, shortname = None, version = None, suffix = None):
        return dict(location=location, name=name, shortname=shortname, version=version, suffix=suffix)


if __name__ == '__main__':
    test_dylib_info()
