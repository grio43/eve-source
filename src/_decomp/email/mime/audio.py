#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\email\mime\audio.py
__all__ = ['MIMEAudio']
try:
    import sndhdr
except ImportError:
    pass

from cStringIO import StringIO
from email import encoders
from email.mime.nonmultipart import MIMENonMultipart
_sndhdr_MIMEmap = {'au': 'basic',
 'wav': 'x-wav',
 'aiff': 'x-aiff',
 'aifc': 'x-aiff'}

def _whatsnd(data):
    hdr = data[:512]
    fakefile = StringIO(hdr)
    for testfn in sndhdr.tests:
        res = testfn(hdr, fakefile)
        if res is not None:
            return _sndhdr_MIMEmap.get(res[0])


class MIMEAudio(MIMENonMultipart):

    def __init__(self, _audiodata, _subtype = None, _encoder = encoders.encode_base64, **_params):
        if _subtype is None:
            _subtype = _whatsnd(_audiodata)
        if _subtype is None:
            raise TypeError('Could not find audio MIME subtype')
        MIMENonMultipart.__init__(self, 'audio', _subtype, **_params)
        self.set_payload(_audiodata)
        _encoder(self)
