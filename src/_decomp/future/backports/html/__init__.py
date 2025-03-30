#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\future\backports\html\__init__.py
from __future__ import unicode_literals
_escape_map = {ord(u'&'): u'&amp;',
 ord(u'<'): u'&lt;',
 ord(u'>'): u'&gt;'}
_escape_map_full = {ord(u'&'): u'&amp;',
 ord(u'<'): u'&lt;',
 ord(u'>'): u'&gt;',
 ord(u'"'): u'&quot;',
 ord(u"'"): u'&#x27;'}

def escape(s, quote = True):
    if quote:
        return s.translate(_escape_map_full)
    return s.translate(_escape_map)
