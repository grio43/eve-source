#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\urllib3\packages\ssl_match_hostname\_implementation.py
import re
__version__ = '3.4.0.2'

class CertificateError(ValueError):
    pass


def _dnsname_match(dn, hostname, max_wildcards = 1):
    pats = []
    if not dn:
        return False
    parts = dn.split('.')
    leftmost = parts[0]
    remainder = parts[1:]
    wildcards = leftmost.count('*')
    if wildcards > max_wildcards:
        raise CertificateError('too many wildcards in certificate DNS name: ' + repr(dn))
    if not wildcards:
        return dn.lower() == hostname.lower()
    if leftmost == '*':
        pats.append('[^.]+')
    elif leftmost.startswith('xn--') or hostname.startswith('xn--'):
        pats.append(re.escape(leftmost))
    else:
        pats.append(re.escape(leftmost).replace('\\*', '[^.]*'))
    for frag in remainder:
        pats.append(re.escape(frag))

    pat = re.compile('\\A' + '\\.'.join(pats) + '\\Z', re.IGNORECASE)
    return pat.match(hostname)


def match_hostname(cert, hostname):
    if not cert:
        raise ValueError('empty or no certificate')
    dnsnames = []
    san = cert.get('subjectAltName', ())
    for key, value in san:
        if key == 'DNS':
            if _dnsname_match(value, hostname):
                return
            dnsnames.append(value)

    if not dnsnames:
        for sub in cert.get('subject', ()):
            for key, value in sub:
                if key == 'commonName':
                    if _dnsname_match(value, hostname):
                        return
                    dnsnames.append(value)

    if len(dnsnames) > 1:
        raise CertificateError("hostname %r doesn't match either of %s" % (hostname, ', '.join(map(repr, dnsnames))))
    elif len(dnsnames) == 1:
        raise CertificateError("hostname %r doesn't match %r" % (hostname, dnsnames[0]))
    else:
        raise CertificateError('no appropriate commonName or subjectAltName fields were found')
