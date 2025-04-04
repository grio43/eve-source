#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\future\backports\email\iterators.py
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
__all__ = [u'body_line_iterator', u'typed_subpart_iterator', u'walk']
import sys
from io import StringIO

def walk(self):
    yield self
    if self.is_multipart():
        for subpart in self.get_payload():
            for subsubpart in subpart.walk():
                yield subsubpart


def body_line_iterator(msg, decode = False):
    for subpart in msg.walk():
        payload = subpart.get_payload(decode=decode)
        if isinstance(payload, str):
            for line in StringIO(payload):
                yield line


def typed_subpart_iterator(msg, maintype = u'text', subtype = None):
    for subpart in msg.walk():
        if subpart.get_content_maintype() == maintype:
            if subtype is None or subpart.get_content_subtype() == subtype:
                yield subpart


def _structure(msg, fp = None, level = 0, include_default = False):
    if fp is None:
        fp = sys.stdout
    tab = u' ' * (level * 4)
    print(tab + msg.get_content_type(), end=u'', file=fp)
    if include_default:
        print(u' [%s]' % msg.get_default_type(), file=fp)
    else:
        print(file=fp)
    if msg.is_multipart():
        for subpart in msg.get_payload():
            _structure(subpart, fp, level + 1, include_default)
