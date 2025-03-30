#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evemail\client\link.py
SCHEME = 'evemail'
SCHEME_ALIAS = 'evemailto'

def register_link_handlers(registry):
    for scheme in (SCHEME, SCHEME_ALIAS):
        registry.register(scheme, handle_evemail_link, hint='UI/Mail/SendMail')


def handle_evemail_link(url):
    recipient, subject, body = parse_evemail_url(url)
    sm.GetService('mailSvc').SendMsgDlg(toCharacterIDs=[recipient], subject=subject, body=body)


def parse_evemail_url(url):
    parts = url[url.index(':') + 1:].split('::')
    recipient = int(parts[0])
    subject = None
    body = None
    if len(parts) == 3:
        subject = parts[1]
        body = parts[2].replace('\r', '').replace('\n', '<br>')
    return (recipient, subject, body)


def format_evemail_url(recipient, subject = None, body = None):
    if subject or body:
        return u'{}:{}::{}::{}'.format(SCHEME, recipient, subject, body)
    else:
        return u'{}:{}'.format(SCHEME, recipient)
