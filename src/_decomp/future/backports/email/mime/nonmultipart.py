#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\future\backports\email\mime\nonmultipart.py
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
__all__ = [u'MIMENonMultipart']
from future.backports.email import errors
from future.backports.email.mime.base import MIMEBase

class MIMENonMultipart(MIMEBase):

    def attach(self, payload):
        raise errors.MultipartConversionError(u'Cannot attach additional subparts to non-multipart/*')
