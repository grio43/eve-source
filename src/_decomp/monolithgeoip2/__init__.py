#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\monolithgeoip2\__init__.py
import logging
import os
import geoip2.database
from maxminddb import MODE_MEMORY
try:
    from blue import pyos, paths
except ImportError:
    pyos = None
    paths = None

log = logging.getLogger(__name__)

def _get_root():
    root = os.path.split(__file__)[0]
    if pyos:
        if pyos.packaged:
            root = paths.ResolvePath(u'bin:/') + 'packages/monolithgeoip2/'
    return root


def _get_country_db_path():
    return os.path.join(_get_root(), 'data', 'GeoLite2-Country.mmdb')


def _get_asn_db_path():
    return os.path.join(_get_root(), 'data', 'GeoLite2-ASN.mmdb')


def country(ipaddress_string):
    if country_reader is None:
        return
    try:
        return country_reader.country(ipaddress_string)
    except Exception:
        return


def asn(ipaddress_string):
    if asn_reader is None:
        return
    try:
        return asn_reader.asn(ipaddress_string)
    except Exception:
        return


try:
    country_db_path = _get_country_db_path()
    country_reader = geoip2.database.Reader(country_db_path, mode=MODE_MEMORY)
except Exception:
    log.warning('Failed to load country DB', exc_info=1)
    country_reader = None

try:
    asn_db_path = _get_asn_db_path()
    asn_reader = geoip2.database.Reader(asn_db_path, mode=MODE_MEMORY)
except Exception:
    log.warning('Failed to load ASN DB', exc_info=1)
    asn_reader = None
