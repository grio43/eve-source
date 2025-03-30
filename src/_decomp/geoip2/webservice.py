#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\geoip2\webservice.py
import requests
from requests.utils import default_user_agent
import geoip2
import geoip2.models
from .compat import compat_ip_address
from .errors import AddressNotFoundError, AuthenticationError, GeoIP2Error, HTTPError, InvalidRequestError, OutOfQueriesError, PermissionRequiredError

class Client(object):

    def __init__(self, user_id, license_key, host = 'geoip.maxmind.com', locales = None, timeout = None):
        if locales is None:
            locales = ['en']
        self._locales = locales
        self._user_id = user_id if isinstance(user_id, bytes) else str(user_id)
        self._license_key = license_key
        self._base_uri = 'https://%s/geoip/v2.1' % host
        self._timeout = timeout

    def city(self, ip_address = 'me'):
        return self._response_for('city', geoip2.models.City, ip_address)

    def country(self, ip_address = 'me'):
        return self._response_for('country', geoip2.models.Country, ip_address)

    def insights(self, ip_address = 'me'):
        return self._response_for('insights', geoip2.models.Insights, ip_address)

    def _response_for(self, path, model_class, ip_address):
        if ip_address != 'me':
            ip_address = str(compat_ip_address(ip_address))
        uri = '/'.join([self._base_uri, path, ip_address])
        response = requests.get(uri, auth=(self._user_id, self._license_key), headers={'Accept': 'application/json',
         'User-Agent': self._user_agent()}, timeout=self._timeout)
        if response.status_code == 200:
            body = self._handle_success(response, uri)
            return model_class(body, locales=self._locales)
        self._handle_error(response, uri)

    def _user_agent(self):
        return 'GeoIP2 Python Client v%s (%s)' % (geoip2.__version__, default_user_agent())

    def _handle_success(self, response, uri):
        try:
            return response.json()
        except ValueError as ex:
            raise GeoIP2Error('Received a 200 response for %(uri)s but could not decode the response as JSON: ' % locals() + ', '.join(ex.args), 200, uri)

    def _handle_error(self, response, uri):
        status = response.status_code
        if 400 <= status < 500:
            self._handle_4xx_status(response, status, uri)
        elif 500 <= status < 600:
            self._handle_5xx_status(status, uri)
        else:
            self._handle_non_200_status(status, uri)

    def _handle_4xx_status(self, response, status, uri):
        if not response.content:
            raise HTTPError('Received a %(status)i error for %(uri)s with no body.' % locals(), status, uri)
        elif response.headers['Content-Type'].find('json') == -1:
            raise HTTPError('Received a %i for %s with the following body: %s' % (status, uri, response.content), status, uri)
        try:
            body = response.json()
        except ValueError as ex:
            raise HTTPError('Received a %(status)i error for %(uri)s but it did not include the expected JSON body: ' % locals() + ', '.join(ex.args), status, uri)
        else:
            if 'code' in body and 'error' in body:
                self._handle_web_service_error(body.get('error'), body.get('code'), status, uri)
            else:
                raise HTTPError('Response contains JSON but it does not specify code or error keys', status, uri)

    def _handle_web_service_error(self, message, code, status, uri):
        if code in ('IP_ADDRESS_NOT_FOUND', 'IP_ADDRESS_RESERVED'):
            raise AddressNotFoundError(message)
        elif code in ('AUTHORIZATION_INVALID', 'LICENSE_KEY_REQUIRED', 'USER_ID_REQUIRED', 'USER_ID_UNKNOWN'):
            raise AuthenticationError(message)
        elif code in ('INSUFFICIENT_FUNDS', 'OUT_OF_QUERIES'):
            raise OutOfQueriesError(message)
        elif code == 'PERMISSION_REQUIRED':
            raise PermissionRequiredError(message)
        raise InvalidRequestError(message, code, status, uri)

    def _handle_5xx_status(self, status, uri):
        raise HTTPError('Received a server error (%(status)i) for %(uri)s' % locals(), status, uri)

    def _handle_non_200_status(self, status, uri):
        raise HTTPError('Received a very surprising HTTP status (%(status)i) for %(uri)s' % locals(), status, uri)
