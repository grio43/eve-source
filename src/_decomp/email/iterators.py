#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\email\iterators.py
__all__ = ['body_line_iterator', 'typed_subpart_iterator', 'walk']
import sys
from cStringIO import StringIO

def walk(self):
    yield self
    if self.is_multipart():
        for subpart in self.get_payload():
            for subsubpart in subpart.walk():
                yield subsubpart


def body_line_iterator(msg, decode = False):
    for subpart in msg.walk():
        payload = subpart.get_payload(decode=decode)
        if isinstance(payload, basestring):
            for line in StringIO(payload):
                yield line


def typed_subpart_iterator(msg, maintype = 'text', subtype = None):
    for subpart in msg.walk():
        if subpart.get_content_maintype() == maintype:
            if subtype is None or subpart.get_content_subtype() == subtype:
                yield subpart


def _structure(msg, fp = None, level = 0, include_default = False):
    if fp is None:
        fp = sys.stdout
    tab = ' ' * (level * 4)
    print >> fp, tab + msg.get_content_type(),
    if include_default:
        print >> fp, '[%s]' % msg.get_default_type()
    else:
        print >> fp
    if msg.is_multipart():
        for subpart in msg.get_payload():
            _structure(subpart, fp, level + 1, include_default)
