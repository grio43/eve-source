#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\lib\pyasn1_modules\rfc2314.py
from pyasn1.type import tag, namedtype, namedval, univ, constraint
from pyasn1_modules.rfc2459 import *

class Attributes(univ.SetOf):
    componentType = Attribute()


class Version(univ.Integer):
    pass


class CertificationRequestInfo(univ.Sequence):
    componentType = namedtype.NamedTypes(namedtype.NamedType('version', Version()), namedtype.NamedType('subject', Name()), namedtype.NamedType('subjectPublicKeyInfo', SubjectPublicKeyInfo()), namedtype.NamedType('attributes', Attributes().subtype(implicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 0))))


class Signature(univ.BitString):
    pass


class SignatureAlgorithmIdentifier(AlgorithmIdentifier):
    pass


class CertificationRequest(univ.Sequence):
    componentType = namedtype.NamedTypes(namedtype.NamedType('certificationRequestInfo', CertificationRequestInfo()), namedtype.NamedType('signatureAlgorithm', SignatureAlgorithmIdentifier()), namedtype.NamedType('signature', Signature()))
