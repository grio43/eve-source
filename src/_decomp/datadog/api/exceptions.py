#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\datadog\api\exceptions.py


class ClientError(Exception):

    def __init__(self, method, url, exception):
        message = u'Could not request {method} {url}: {exception}. Please check the network connection or try again later. If the problem persists, please contact support@datadoghq.com'.format(method=method, url=url, exception=exception)
        super(ClientError, self).__init__(message)


class HttpTimeout(Exception):

    def __init__(self, method, url, timeout):
        message = u'{method} {url} timed out after {timeout}. Please try again later. If the problem persists, please contact support@datadoghq.com'.format(method=method, url=url, timeout=timeout)
        super(HttpTimeout, self).__init__(message)


class HttpBackoff(Exception):

    def __init__(self, backoff_period):
        message = u"Too many timeouts. Won't try again for {backoff_period} seconds. ".format(backoff_period=backoff_period)
        super(HttpBackoff, self).__init__(message)


class HTTPError(Exception):

    def __init__(self, status_code = None, reason = None):
        self.status_code = status_code
        reason = u' - {reason}'.format(reason=reason) if reason else u''
        message = u'Datadog returned a bad HTTP response code: {status_code}{reason}. Please try again later. If the problem persists, please contact support@datadoghq.com'.format(status_code=status_code, reason=reason)
        super(HTTPError, self).__init__(message)


class ApiError(Exception):
    pass


class ApiNotInitialized(Exception):
    pass
