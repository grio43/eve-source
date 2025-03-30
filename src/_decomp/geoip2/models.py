#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\geoip2\models.py
from abc import ABCMeta
import geoip2.records
from geoip2.mixins import SimpleEquality

class Country(SimpleEquality):

    def __init__(self, raw_response, locales = None):
        if locales is None:
            locales = ['en']
        self._locales = locales
        self.continent = geoip2.records.Continent(locales, **raw_response.get('continent', {}))
        self.country = geoip2.records.Country(locales, **raw_response.get('country', {}))
        self.registered_country = geoip2.records.Country(locales, **raw_response.get('registered_country', {}))
        self.represented_country = geoip2.records.RepresentedCountry(locales, **raw_response.get('represented_country', {}))
        self.maxmind = geoip2.records.MaxMind(**raw_response.get('maxmind', {}))
        self.traits = geoip2.records.Traits(**raw_response.get('traits', {}))
        self.raw = raw_response

    def __repr__(self):
        return '{module}.{class_name}({data}, {locales})'.format(module=self.__module__, class_name=self.__class__.__name__, data=self.raw, locales=self._locales)


class City(Country):

    def __init__(self, raw_response, locales = None):
        super(City, self).__init__(raw_response, locales)
        self.city = geoip2.records.City(locales, **raw_response.get('city', {}))
        self.location = geoip2.records.Location(**raw_response.get('location', {}))
        self.postal = geoip2.records.Postal(**raw_response.get('postal', {}))
        self.subdivisions = geoip2.records.Subdivisions(locales, *raw_response.get('subdivisions', []))


class Insights(City):
    pass


class Enterprise(City):
    pass


class SimpleModel(SimpleEquality):
    __metaclass__ = ABCMeta

    def __repr__(self):
        return '{module}.{class_name}({data})'.format(module=self.__module__, class_name=self.__class__.__name__, data=str(self.raw))


class AnonymousIP(SimpleModel):

    def __init__(self, raw):
        self.is_anonymous = raw.get('is_anonymous', False)
        self.is_anonymous_vpn = raw.get('is_anonymous_vpn', False)
        self.is_hosting_provider = raw.get('is_hosting_provider', False)
        self.is_public_proxy = raw.get('is_public_proxy', False)
        self.is_tor_exit_node = raw.get('is_tor_exit_node', False)
        self.ip_address = raw.get('ip_address')
        self.raw = raw


class ASN(SimpleModel):

    def __init__(self, raw):
        self.autonomous_system_number = raw.get('autonomous_system_number')
        self.autonomous_system_organization = raw.get('autonomous_system_organization')
        self.ip_address = raw.get('ip_address')
        self.raw = raw


class ConnectionType(SimpleModel):

    def __init__(self, raw):
        self.connection_type = raw.get('connection_type')
        self.ip_address = raw.get('ip_address')
        self.raw = raw


class Domain(SimpleModel):

    def __init__(self, raw):
        self.domain = raw.get('domain')
        self.ip_address = raw.get('ip_address')
        self.raw = raw


class ISP(ASN):

    def __init__(self, raw):
        super(ISP, self).__init__(raw)
        self.isp = raw.get('isp')
        self.organization = raw.get('organization')
