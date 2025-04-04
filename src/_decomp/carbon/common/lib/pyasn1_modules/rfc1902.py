#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\lib\pyasn1_modules\rfc1902.py
from pyasn1.type import univ, namedtype, namedval, tag, constraint

class Integer(univ.Integer):
    subtypeSpec = univ.Integer.subtypeSpec + constraint.ValueRangeConstraint(-2147483648, 2147483647)


class Integer32(univ.Integer):
    subtypeSpec = univ.Integer.subtypeSpec + constraint.ValueRangeConstraint(-2147483648, 2147483647)


class OctetString(univ.OctetString):
    subtypeSpec = univ.Integer.subtypeSpec + constraint.ValueSizeConstraint(0, 65535)


class IpAddress(univ.OctetString):
    tagSet = univ.OctetString.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication, tag.tagFormatSimple, 0))
    subtypeSpec = univ.OctetString.subtypeSpec + constraint.ValueSizeConstraint(4, 4)


class Counter32(univ.Integer):
    tagSet = univ.Integer.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication, tag.tagFormatSimple, 1))
    subtypeSpec = univ.Integer.subtypeSpec + constraint.ValueRangeConstraint(0, 4294967295L)


class Gauge32(univ.Integer):
    tagSet = univ.Integer.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication, tag.tagFormatSimple, 2))
    subtypeSpec = univ.Integer.subtypeSpec + constraint.ValueRangeConstraint(0, 4294967295L)


class Unsigned32(univ.Integer):
    tagSet = univ.Integer.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication, tag.tagFormatSimple, 2))
    subtypeSpec = univ.Integer.subtypeSpec + constraint.ValueRangeConstraint(0, 4294967295L)


class TimeTicks(univ.Integer):
    tagSet = univ.Integer.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication, tag.tagFormatSimple, 3))
    subtypeSpec = univ.Integer.subtypeSpec + constraint.ValueRangeConstraint(0, 4294967295L)


class Opaque(univ.OctetString):
    tagSet = univ.OctetString.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication, tag.tagFormatSimple, 4))


class Counter64(univ.Integer):
    tagSet = univ.Integer.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication, tag.tagFormatSimple, 6))
    subtypeSpec = univ.Integer.subtypeSpec + constraint.ValueRangeConstraint(0, 18446744073709551615L)


class Bits(univ.OctetString):
    pass


class ObjectName(univ.ObjectIdentifier):
    pass


class SimpleSyntax(univ.Choice):
    componentType = namedtype.NamedTypes(namedtype.NamedType('integer-value', Integer()), namedtype.NamedType('string-value', OctetString()), namedtype.NamedType('objectID-value', univ.ObjectIdentifier()))


class ApplicationSyntax(univ.Choice):
    componentType = namedtype.NamedTypes(namedtype.NamedType('ipAddress-value', IpAddress()), namedtype.NamedType('counter-value', Counter32()), namedtype.NamedType('timeticks-value', TimeTicks()), namedtype.NamedType('arbitrary-value', Opaque()), namedtype.NamedType('big-counter-value', Counter64()), namedtype.NamedType('gauge32-value', Gauge32()))


class ObjectSyntax(univ.Choice):
    componentType = namedtype.NamedTypes(namedtype.NamedType('simple', SimpleSyntax()), namedtype.NamedType('application-wide', ApplicationSyntax()))
