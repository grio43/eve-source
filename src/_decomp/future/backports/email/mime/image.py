#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\future\backports\email\mime\image.py
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
__all__ = [u'MIMEImage']
import imghdr
from future.backports.email import encoders
from future.backports.email.mime.nonmultipart import MIMENonMultipart

class MIMEImage(MIMENonMultipart):

    def __init__(self, _imagedata, _subtype = None, _encoder = encoders.encode_base64, **_params):
        if _subtype is None:
            _subtype = imghdr.what(None, _imagedata)
        if _subtype is None:
            raise TypeError(u'Could not guess image MIME subtype')
        MIMENonMultipart.__init__(self, u'image', _subtype, **_params)
        self.set_payload(_imagedata)
        _encoder(self)
