#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\stringutil\__init__.py
__author__ = 'fridrik'
import sys

def strx(o):
    try:
        return str(o)
    except UnicodeEncodeError:
        sys.exc_clear()
        return unicode(o).encode('ascii', 'replace')
