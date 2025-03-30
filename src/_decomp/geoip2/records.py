#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\geoip2\records.py
from abc import ABCMeta
from geoip2.mixins import SimpleEquality

class Record(SimpleEquality):
    __metaclass__ = ABCMeta
    _valid_attributes = set()

    def __init__(self, **kwargs):
        valid_args = dict(((k, kwargs.get(k)) for k in self._valid_attributes))
        self.__dict__.update(valid_args)

    def __setattr__(self, name, value):
        raise AttributeError("can't set attribute")

    def __repr__(self):
        args = ', '.join(('%s=%r' % x for x in self.__dict__.items()))
        return '{module}.{class_name}({data})'.format(module=self.__module__, class_name=self.__class__.__name__, data=args)


class PlaceRecord(Record):
    __metaclass__ = ABCMeta

    def __init__(self, locales = None, **kwargs):
        if locales is None:
            locales = ['en']
        if kwargs.get('names') is None:
            kwargs['names'] = {}
        object.__setattr__(self, '_locales', locales)
        super(PlaceRecord, self).__init__(**kwargs)

    @property
    def name(self):
        return next((self.names.get(x) for x in self._locales if x in self.names), None)


class City(PlaceRecord):
    _valid_attributes = set(['confidence', 'geoname_id', 'names'])


class Continent(PlaceRecord):
    _valid_attributes = set(['code', 'geoname_id', 'names'])


class Country(PlaceRecord):
    _valid_attributes = set(['confidence',
     'geoname_id',
     'iso_code',
     'names'])


class RepresentedCountry(Country):
    _valid_attributes = set(['confidence',
     'geoname_id',
     'iso_code',
     'names',
     'type'])


class Location(Record):
    _valid_attributes = set(['average_income',
     'accuracy_radius',
     'latitude',
     'longitude',
     'metro_code',
     'population_density',
     'postal_code',
     'postal_confidence',
     'time_zone'])


class MaxMind(Record):
    _valid_attributes = set(['queries_remaining'])


class Postal(Record):
    _valid_attributes = set(['code', 'confidence'])


class Subdivision(PlaceRecord):
    _valid_attributes = set(['confidence',
     'geoname_id',
     'iso_code',
     'names'])


class Subdivisions(tuple):

    def __new__(cls, locales, *subdivisions):
        subdivisions = [ Subdivision(locales, **x) for x in subdivisions ]
        obj = super(cls, Subdivisions).__new__(cls, subdivisions)
        return obj

    def __init__(self, locales, *subdivisions):
        self._locales = locales
        super(Subdivisions, self).__init__()

    @property
    def most_specific(self):
        try:
            return self[-1]
        except IndexError:
            return Subdivision(self._locales)


class Traits(Record):
    _valid_attributes = set(['autonomous_system_number',
     'autonomous_system_organization',
     'connection_type',
     'domain',
     'is_anonymous_proxy',
     'is_legitimate_proxy',
     'is_satellite_provider',
     'isp',
     'ip_address',
     'organization',
     'user_type'])

    def __init__(self, **kwargs):
        for k in ['is_anonymous_proxy', 'is_legitimate_proxy', 'is_satellite_provider']:
            kwargs[k] = bool(kwargs.get(k, False))

        super(Traits, self).__init__(**kwargs)
