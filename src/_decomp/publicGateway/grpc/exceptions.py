#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\publicGateway\grpc\exceptions.py


class GenericException(Exception):

    def __init__(self, request_primitive, response_primitive):
        self.request_primitive = request_primitive
        self.response_primitive = response_primitive

    def __new__(cls, request_primitive, response_primitive):
        if response_primitive.status_code // 100 == 4:
            if response_primitive.status_code % 400 == 3:
                cls = AccessForbiddenException
            else:
                cls = RequestException
        elif response_primitive.status_code // 100 == 5:
            cls = ServerException
        return Exception.__new__(cls)

    @property
    def character_id(self):
        return get_character_id(self)

    @property
    def status_code(self):
        return get_status_code(self)

    @property
    def status_message(self):
        return get_status_message(self)

    def __repr__(self):
        return '%s(status_code=%s, status_message=%s)' % (self.__class__.__name__, self.status_code, self.status_message)

    def __str__(self):
        return self.__repr__()


class ServerException(GenericException):
    pass


class RequestException(GenericException):
    pass


class AccessForbiddenException(RequestException):
    pass


class BackedOffException(Exception):
    pass


def get_character_id(e):
    return e.request_primitive.authoritative_context.identity.character.sequential


def get_status_code(e):
    return e.response_primitive.status_code


def get_status_message(e):
    return e.response_primitive.status_message
