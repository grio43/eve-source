#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\characterskills\client\link.py
import inventorycommon.const
from utillib import KeyVal
SCHEME_CERTIFICATE = 'CertEntry'

def register_link_handlers(registry):
    registry.register(scheme=SCHEME_CERTIFICATE, handler=handle_certificate_link, hint='UI/Commands/ShowInfo')


def handle_certificate_link(url):
    certificate_id, level = parse_certificate_url(url)
    abstract_info = KeyVal(certificateID=certificate_id, level=level)
    sm.StartService('info').ShowInfo(inventorycommon.const.typeCertificate, abstractinfo=abstract_info)


def parse_certificate_url(url):
    certificate_id, level = url[url.index(':') + 1:].split('//')
    return (int(certificate_id), int(level))


def format_certificate_url(certificate_id, level):
    return u'{}:{}//{}'.format(SCHEME_CERTIFICATE, certificate_id, level)
