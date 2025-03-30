#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\geoip2\errors.py


class GeoIP2Error(RuntimeError):
    pass


class AddressNotFoundError(GeoIP2Error):
    pass


class AuthenticationError(GeoIP2Error):
    pass


class HTTPError(GeoIP2Error):

    def __init__(self, message, http_status = None, uri = None):
        super(HTTPError, self).__init__(message)
        self.http_status = http_status
        self.uri = uri


class InvalidRequestError(GeoIP2Error):
    pass


class OutOfQueriesError(GeoIP2Error):
    pass


class PermissionRequiredError(GeoIP2Error):
    pass
