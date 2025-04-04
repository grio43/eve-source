#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\lib\pyasn1_modules\rfc1155.py
from pyasn1.type import univ, namedtype, namedval, tag, constraint

class ObjectName(univ.ObjectIdentifier):
    pass


class SimpleSyntax(univ.Choice):
    componentType = namedtype.NamedTypes(namedtype.NamedType('number', univ.Integer()), namedtype.NamedType('string', univ.OctetString()), namedtype.NamedType('object', univ.ObjectIdentifier()), namedtype.NamedType('empty', univ.Null()))


class IpAddress(univ.OctetString):
    tagSet = univ.OctetString.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication, tag.tagFormatSimple, 0))
    subtypeSpec = univ.Integer.subtypeSpec + constraint.ValueSizeConstraint(4, 4)


class NetworkAddress(univ.Choice):
    componentType = namedtype.NamedTypes(namedtype.NamedType('internet', IpAddress()))


class Counter(univ.Integer):
    tagSet = univ.Integer.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication, tag.tagFormatSimple, 1))
    subtypeSpec = univ.Integer.subtypeSpec + constraint.ValueRangeConstraint(0, 4294967295L)


class Gauge(univ.Integer):
    tagSet = univ.Integer.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication, tag.tagFormatSimple, 2))
    subtypeSpec = univ.Integer.subtypeSpec + constraint.ValueRangeConstraint(0, 4294967295L)


class TimeTicks(univ.Integer):
    tagSet = univ.Integer.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication, tag.tagFormatSimple, 3))
    subtypeSpec = univ.Integer.subtypeSpec + constraint.ValueRangeConstraint(0, 4294967295L)


class Opaque(univ.OctetString):
    tagSet = univ.OctetString.tagSet.tagImplicitly(tag.Tag(tag.tagClassApplication, tag.tagFormatSimple, 4))


class ApplicationSyntax(univ.Choice):
    componentType = namedtype.NamedTypes(namedtype.NamedType('address', NetworkAddress()), namedtype.NamedType('counter', Counter()), namedtype.NamedType('gauge', Gauge()), namedtype.NamedType('ticks', TimeTicks()), namedtype.NamedType('arbitrary', Opaque()))


class ObjectSyntax(univ.Choice):
    componentType = namedtype.NamedTypes(namedtype.NamedType('simple', SimpleSyntax()), namedtype.NamedType('application-wide', ApplicationSyntax()))
