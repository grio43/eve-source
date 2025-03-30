#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\future\backports\email\mime\base.py
from __future__ import absolute_import, division, unicode_literals
from future.backports.email import message
__all__ = [u'MIMEBase']

class MIMEBase(message.Message):

    def __init__(self, _maintype, _subtype, **_params):
        message.Message.__init__(self)
        ctype = u'%s/%s' % (_maintype, _subtype)
        self.add_header(u'Content-Type', ctype, **_params)
        self[u'MIME-Version'] = u'1.0'
