#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\clientRefreshToken\discovery_hacks.py
import requests
import uthread2
import logging
import urlparse
logger = logging.getLogger(__name__)
WELL_KNOWN_PATH = '/.well-known/oauth-authorization-server/'
DEFAULT_SCHEME = 'https'
FALLBACK_FQDN = '{}://login.eveonline.com'.format(DEFAULT_SCHEME)
FALLBACK_WELL_KNOWN_URL = urlparse.urljoin(FALLBACK_FQDN, WELL_KNOWN_PATH)
FALLBACK_TOKEN_ENDPOINT = urlparse.urljoin(FALLBACK_FQDN, '/v2/oauth/token')
FALLBACK_CLIENT_ID = 'eveLauncherTQ'

def discover_refresh_parameters_from_user_token(user_token_payload):
    try:
        token_endpoint = discover_token_endpoint_from_user_token(user_token_payload)
        client_id = discover_client_id_from_user_token(user_token_payload)
        return (client_id, token_endpoint)
    except Exception as e:
        logger.exception('Failed to discover refresh parameters, using fallbacks', extra={'fallback_client_id': FALLBACK_CLIENT_ID,
         'fallback_token_endpoint': FALLBACK_TOKEN_ENDPOINT})
        return (FALLBACK_CLIENT_ID, FALLBACK_TOKEN_ENDPOINT)


def discover_client_id_from_user_token(user_token_payload):
    return user_token_payload['azp']


def discover_token_endpoint_from_user_token(user_token_payload):
    well_known_url = create_well_known_url_from_iss_claim(user_token_payload.get('iss'))
    max_retries = 10
    attempts = 0
    while True:
        attempts += 1
        if attempts >= 10:
            raise RuntimeError('max retries ({}) attempted'.format(max_retries))
        response = requests.get(well_known_url)
        if not response.ok:
            uthread2.sleep(1)
            continue
        content = response.json()
        token_endpoint = content['token_endpoint']
        if token_endpoint:
            return token_endpoint


def create_well_known_url_from_iss_claim(issuer):
    iss_res = urlparse.urlparse(issuer)
    if not iss_res.netloc:
        if not iss_res.path:
            raise RuntimeError('Malformed `iss` claim in SSO token')
        iss_res = iss_res._replace(netloc=iss_res.path)
    if not iss_res.scheme:
        iss_res = iss_res._replace(scheme=DEFAULT_SCHEME)
    if iss_res.path != WELL_KNOWN_PATH:
        iss_res = iss_res._replace(path=WELL_KNOWN_PATH)
    return iss_res.geturl()


if __name__ == '__main__':
    for test_val in ('', '?foo=bar', '#baz'):
        try:
            create_well_known_url_from_iss_claim(test_val)
        except RuntimeError as e:
            pass
