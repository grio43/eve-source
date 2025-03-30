#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\pkg_resources\_vendor\packaging\utils.py
from __future__ import absolute_import, division, print_function
import re
_canonicalize_regex = re.compile('[-_.]+')

def canonicalize_name(name):
    return _canonicalize_regex.sub('-', name).lower()
