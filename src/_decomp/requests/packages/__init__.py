#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\requests\packages\__init__.py
from __future__ import absolute_import
import sys
try:
    from . import urllib3
except ImportError:
    import urllib3
    sys.modules['%s.urllib3' % __name__] = urllib3

try:
    from . import chardet
except ImportError:
    import chardet
    sys.modules['%s.chardet' % __name__] = chardet
