#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\monolithsentry\geoip2_tags.py
import monolithgeoip2
import monolithipify
import monolithsentry
from uthread2 import StartTasklet
import sentry_sdk
geoip_tags = {}
COUNTRY_KEY = 'country'
CONTINENT_KEY = 'continent'
ASN_KEY = 'asn'
ASO_KEY = 'aso'
IP_ADDRESS_KEY = 'ip'

def set_geo_tags():
    StartTasklet(_set_geo_tags)


def _set_geo_tags():
    ip_address = monolithipify.get_public_ip()
    country_result = monolithgeoip2.country(ip_address)
    asn_result = monolithgeoip2.asn(ip_address)
    if ip_address:
        _update_client_geoip2_tags(IP_ADDRESS_KEY, ip_address)
    if country_result:
        _update_client_geoip2_tags(COUNTRY_KEY, country_result.country.name)
        _update_client_geoip2_tags(CONTINENT_KEY, country_result.continent.name)
    if asn_result:
        _update_client_geoip2_tags(ASN_KEY, asn_result.autonomous_system_number)
        _update_client_geoip2_tags(ASO_KEY, asn_result.autonomous_system_organization)


def _update_client_geoip2_tags(key, value):
    geoip_tags[key] = value
    with sentry_sdk.configure_scope() as scope:
        scope.set_tag(key, value)
    monolithsentry.set_sentry_crash_key()


def get_geoip_tags():
    return geoip_tags
