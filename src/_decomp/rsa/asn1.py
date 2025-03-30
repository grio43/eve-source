#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\rsa\asn1.py
from pyasn1.type import univ, namedtype, tag

class PubKeyHeader(univ.Sequence):
    componentType = namedtype.NamedTypes(namedtype.NamedType('oid', univ.ObjectIdentifier()), namedtype.NamedType('parameters', univ.Null()))


class OpenSSLPubKey(univ.Sequence):
    componentType = namedtype.NamedTypes(namedtype.NamedType('header', PubKeyHeader()), namedtype.NamedType('key', univ.OctetString().subtype(implicitTag=tag.Tag(tagClass=0, tagFormat=0, tagId=3))))


class AsnPubKey(univ.Sequence):
    componentType = namedtype.NamedTypes(namedtype.NamedType('modulus', univ.Integer()), namedtype.NamedType('publicExponent', univ.Integer()))
