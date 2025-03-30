#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\scriber\bifrost\__init__.py
from optimus.data import helpers
from scriber import httputils
import scriber

class Bifrost(object):

    def __init__(self, request, response, current_session, role_list = None):
        self._request = request
        self.request = httputils.parse_request(request)
        self.response = response
        self._current_session = current_session
        self.session = helpers.ComfySession(current_session)
        self.role_list = role_list or []
        self.is_closed = False

    def respond(self, code = 200, msg = 'OK', **kwargs):
        if not self.is_closed:
            self.response.contentType = 'application/json; charset=utf-8'
            self.response.status = '%s %s' % (code, msg)
            self.response.Write(scriber.scribe_json(**kwargs))
            self.is_closed = True

    def say_ok(self, **kwargs):
        if not kwargs:
            kwargs = {'message': 'OK'}
        self.respond(200, 'OK', **kwargs)

    def say_not_found(self, **kwargs):
        if not kwargs:
            kwargs = {'message': 'Not Found'}
        self.respond(404, 'Not Found', **kwargs)

    def say_unauthorized(self, **kwargs):
        if not kwargs:
            kwargs = {'message': 'Unauthorized'}
        self.respond(401, 'Unauthorized', **kwargs)

    def say_forbidden(self, **kwargs):
        if not kwargs:
            kwargs = {'message': 'Forbidden'}
        self.respond(403, 'Forbidden', **kwargs)

    def say_bad_request(self, **kwargs):
        if not kwargs:
            kwargs = {'message': 'Bad Request'}
        self.respond(400, 'Bad Request', **kwargs)

    def say_error(self, **kwargs):
        if not kwargs:
            kwargs = {'message': 'Internal Server Error'}
        self.respond(500, 'Internal Server Error', **kwargs)

    def say_not_implemented(self, **kwargs):
        if not kwargs:
            kwargs = {'message': 'Not Implemented'}
        self.respond(501, 'Not Implemented', **kwargs)

    def check_roles(self):
        if not self.session or not self.session.is_esp_session():
            self.say_unauthorized()
            return False
        if self.role_list:
            if not self.session.has_all_roles(self.role_list):
                self.say_forbidden()
                return False
        return True

    def get_str(self, name, default = ''):
        return self.request.get.str(name, default)

    def get_int(self, name, default = 0):
        return self.request.get.int(name, default)
