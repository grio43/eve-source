#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\__init__.py
from caching.memoize import Memoize

@Memoize
def IsClient():
    from eveprefs import boot
    return boot.role == 'client'
