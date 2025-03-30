#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\certifi\core.py
import os
try:
    from blue import pyos, paths
except ImportError:
    pyos = None
    paths = None

class DeprecatedBundleWarning(DeprecationWarning):
    pass


def where():
    return os.path.join(get_root(), 'cacert.pem')


def get_root():
    root = os.path.split(__file__)[0]
    if pyos:
        if pyos.packaged:
            root = paths.ResolvePath(u'bin:/') + 'packages/certifi/'
    return root


if __name__ == '__main__':
    print where()
