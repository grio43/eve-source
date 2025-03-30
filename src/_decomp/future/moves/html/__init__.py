#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\future\moves\html\__init__.py
from __future__ import absolute_import
from future.utils import PY3
__future_module__ = True
if PY3:
    from html import *
else:

    def escape(s, quote = True):
        s = s.replace('&', '&amp;')
        s = s.replace('<', '&lt;')
        s = s.replace('>', '&gt;')
        if quote:
            s = s.replace('"', '&quot;')
            s = s.replace("'", '&#x27;')
        return s


    __all__ = ['escape']
