#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\requests\packages\chardet\__init__.py
__version__ = '2.3.0'
from sys import version_info

def detect(aBuf):
    if version_info < (3, 0) and isinstance(aBuf, unicode) or version_info >= (3, 0) and not isinstance(aBuf, bytes):
        raise ValueError('Expected a bytes object, not a unicode object')
    from . import universaldetector
    u = universaldetector.UniversalDetector()
    u.reset()
    u.feed(aBuf)
    u.close()
    return u.result
