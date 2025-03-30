#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\geoip2\database.py
import inspect
import maxminddb
from maxminddb import MODE_AUTO, MODE_MMAP, MODE_MMAP_EXT, MODE_FILE, MODE_MEMORY
import geoip2
import geoip2.models
import geoip2.errors

class Reader(object):

    def __init__(self, filename, locales = None, mode = MODE_AUTO):
        if locales is None:
            locales = ['en']
        self._db_reader = maxminddb.open_database(filename, mode)
        self._locales = locales

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def country(self, ip_address):
        return self._model_for(geoip2.models.Country, 'Country', ip_address)

    def city(self, ip_address):
        return self._model_for(geoip2.models.City, 'City', ip_address)

    def anonymous_ip(self, ip_address):
        return self._flat_model_for(geoip2.models.AnonymousIP, 'GeoIP2-Anonymous-IP', ip_address)

    def asn(self, ip_address):
        return self._flat_model_for(geoip2.models.ASN, 'GeoLite2-ASN', ip_address)

    def connection_type(self, ip_address):
        return self._flat_model_for(geoip2.models.ConnectionType, 'GeoIP2-Connection-Type', ip_address)

    def domain(self, ip_address):
        return self._flat_model_for(geoip2.models.Domain, 'GeoIP2-Domain', ip_address)

    def enterprise(self, ip_address):
        return self._model_for(geoip2.models.Enterprise, 'Enterprise', ip_address)

    def isp(self, ip_address):
        return self._flat_model_for(geoip2.models.ISP, 'GeoIP2-ISP', ip_address)

    def _get(self, database_type, ip_address):
        if database_type not in self.metadata().database_type:
            caller = inspect.stack()[2][3]
            raise TypeError('The %s method cannot be used with the %s database' % (caller, self.metadata().database_type))
        record = self._db_reader.get(ip_address)
        if record is None:
            raise geoip2.errors.AddressNotFoundError('The address %s is not in the database.' % ip_address)
        return record

    def _model_for(self, model_class, types, ip_address):
        record = self._get(types, ip_address)
        record.setdefault('traits', {})['ip_address'] = ip_address
        return model_class(record, locales=self._locales)

    def _flat_model_for(self, model_class, types, ip_address):
        record = self._get(types, ip_address)
        record['ip_address'] = ip_address
        return model_class(record)

    def metadata(self):
        return self._db_reader.metadata()

    def close(self):
        self._db_reader.close()
