#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\requests\packages\chardet\compat.py
import sys
if sys.version_info < (3, 0):
    base_str = (str, unicode)
else:
    base_str = (bytes, str)

def wrap_ord(a):
    if sys.version_info < (3, 0) and isinstance(a, base_str):
        return ord(a)
    else:
        return a
