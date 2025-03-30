#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\datadog\api\http_client.py
import logging
import urllib
try:
    import requests
except ImportError:
    requests = None

try:
    from google.appengine.api import urlfetch, urlfetch_errors
except ImportError:
    urlfetch, urlfetch_errors = (None, None)

from datadog.api.exceptions import ClientError, HTTPError, HttpTimeout
log = logging.getLogger('datadog.api')

class HTTPClient(object):

    @classmethod
    def request(cls, method, url, headers, params, data, timeout, proxies, verify, max_retries):
        raise NotImplementedError(u'Must be implemented by HTTPClient subclasses.')


class RequestClient(HTTPClient):

    @classmethod
    def request(cls, method, url, headers, params, data, timeout, proxies, verify, max_retries):
        s = requests.Session()
        http_adapter = requests.adapters.HTTPAdapter(max_retries=max_retries)
        s.mount('https://', http_adapter)
        try:
            result = s.request(method, url, headers=headers, params=params, data=data, timeout=timeout, proxies=proxies, verify=verify)
            result.raise_for_status()
        except requests.ConnectionError as e:
            raise ClientError(method, url, e)
        except requests.exceptions.Timeout:
            raise HttpTimeout(method, url, timeout)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code in (400, 403, 404, 409):
                pass
            else:
                raise HTTPError(e.response.status_code, result.reason)
        except TypeError as e:
            raise TypeError(u"Your installed version of `requests` library seems not compatible withDatadog's usage. We recommand upgrading it ('pip install -U requests').If you need help or have any question, please contact support@datadoghq.com")

        return result


class URLFetchClient(HTTPClient):

    @classmethod
    def request(cls, method, url, headers, params, data, timeout, proxies, verify, max_retries):
        validate_certificate = True if verify else False
        url_with_params = '{url}?{params}'.format(url=url, params=urllib.urlencode(params))
        try:
            result = urlfetch.fetch(url=url_with_params, method=method, headers=headers, validate_certificate=validate_certificate, deadline=timeout, payload=data, follow_redirects=False)
            cls.raise_on_status(result)
        except urlfetch.DownloadError as e:
            raise ClientError(method, url, e)
        except urlfetch_errors.DeadlineExceededError:
            raise HttpTimeout(method, url, timeout)

        return result

    @classmethod
    def raise_on_status(cls, result):
        status_code = result.status_code
        if status_code / 100 != 2:
            if status_code in (400, 403, 404, 409):
                pass
            else:
                raise HTTPError(status_code)


def resolve_http_client():
    if requests:
        log.debug(u'Use `requests` based HTTP client.')
        return RequestClient
    if urlfetch and urlfetch_errors:
        log.debug(u'Use `urlfetch` based HTTP client.')
        return URLFetchClient
    raise ImportError(u'Datadog API client was unable to resolve a HTTP client.  Please install `requests` library.')
