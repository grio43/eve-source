#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\skills\skillplan\grpc\message_bus\requestsMessenger.py
import logging
import uuid
from eveexceptions import UserError
from stackless_response_router.exceptions import TimeoutException, UnpackException
logger = logging.getLogger(__name__)
STATUS_OK = 200
STATUS_BAD_REQUEST = 400
STATUS_NOT_FOUND = 404
STATUS_INVALID_DATA = 412
STATUS_INTERNAL_SERVER_ERROR = 500
USER_ERROR_BY_ERROR_CODE = {STATUS_BAD_REQUEST: 'SkillPlansErrorBadRequest',
 STATUS_NOT_FOUND: 'SkillPlansErrorDataNotFound',
 STATUS_INVALID_DATA: 'SkillPlansErrorInvalidData',
 STATUS_INTERNAL_SERVER_ERROR: 'SkillPlansErrorInternal'}

class ResponseFailureException(Exception):

    def __init__(self, error_message, user_error):
        super(ResponseFailureException, self).__init__(self)
        self.error_message = error_message
        self.user_error = user_error

    def __str__(self):
        return self.error_message

    def get_user_error(self):
        return self.user_error


def send_request(public_gateway, request, response_class):
    request_class_name = '{}.{}'.format(request.__module__, type(request).__name__)
    try:
        logger.info('Sending skill-plans gRPC request for: %s' % request_class_name)
        request_primitive, response_channel = public_gateway.send_character_request(request, response_class)
        response_primitive, payload = response_channel.receive()
        logger.info('Received skill-plans gRPC response for: %s' % request_class_name)
        _check_response_status(response_primitive)
        return payload
    except ResponseFailureException as rException:
        logger.exception(rException)
        raise UserError(rException.user_error)
    except TimeoutException as tException:
        logger.exception(tException)
        raise UserError('SkillPlansErrorTimeout')
    except UnpackException as uException:
        logger.exception(uException)
        raise UserError('SkillPlansErrorUnpacking')
    except Exception as e:
        logger.exception(e)
        raise UserError('SkillPlansErrorUnknowFailure')


def _check_response_status(response):
    status_code = getattr(response, 'status_code', None)
    correlation_uuid_bytes = getattr(response, 'correlation_uuid', None)
    if correlation_uuid_bytes is not None:
        correlation_uuid = str(uuid.UUID(bytes=correlation_uuid_bytes))
    else:
        correlation_uuid = None
    if status_code == STATUS_OK:
        return
    error_message = 'Response for: {} failed - error_message: {} - error_code: {} - correlation_uuid: {}'.format(response.payload.type_url, getattr(response, 'status_message', None), status_code, correlation_uuid)
    user_error = USER_ERROR_BY_ERROR_CODE.get(status_code, 'SkillPlansErrorUnexpectedResponse')
    raise ResponseFailureException(error_message, user_error)
