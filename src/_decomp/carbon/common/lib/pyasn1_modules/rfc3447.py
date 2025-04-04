#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\lib\pyasn1_modules\rfc3447.py
from pyasn1_modules.rfc2437 import *

class OtherPrimeInfo(univ.Sequence):
    componentType = namedtype.NamedTypes(namedtype.NamedType('prime', univ.Integer()), namedtype.NamedType('exponent', univ.Integer()), namedtype.NamedType('coefficient', univ.Integer()))


class OtherPrimeInfos(univ.SequenceOf):
    componentType = OtherPrimeInfo()
    subtypeSpec = univ.SequenceOf.subtypeSpec + constraint.ValueSizeConstraint(1, MAX)


class RSAPrivateKey(univ.Sequence):
    componentType = namedtype.NamedTypes(namedtype.NamedType('version', univ.Integer(namedValues=namedval.NamedValues(('two-prime', 0), ('multi', 1)))), namedtype.NamedType('modulus', univ.Integer()), namedtype.NamedType('publicExponent', univ.Integer()), namedtype.NamedType('privateExponent', univ.Integer()), namedtype.NamedType('prime1', univ.Integer()), namedtype.NamedType('prime2', univ.Integer()), namedtype.NamedType('exponent1', univ.Integer()), namedtype.NamedType('exponent2', univ.Integer()), namedtype.NamedType('coefficient', univ.Integer()), namedtype.OptionalNamedType('otherPrimeInfos', OtherPrimeInfos()))
