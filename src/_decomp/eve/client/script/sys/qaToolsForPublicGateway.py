#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\sys\qaToolsForPublicGateway.py
from uthread2 import Sleep

class MockResponsePrimitive(object):

    def __init__(self, status_code):
        self.status_code = status_code
        self.status_message = 'Error: %s' % status_code


class MockResponseChannel(object):

    def __init__(self, status_code):
        self.status_code = status_code

    def receive(self):
        response_primitive = MockResponsePrimitive(self.status_code)
        response_payload = None
        return (response_primitive, response_payload)


class PublicGatewayRequestHijacker(object):
    SETTING_PUBLIC_REQUEST_HIJACKER_ENABLED = 'public_request_hijacker_enabled'
    SETTING_PUBLIC_REQUEST_HIJACKER_ERROR = 'public_request_hijacker_error'
    SETTING_PUBLIC_REQUEST_HIJACKER_LATENCY = 'public_request_hijacker_latency'

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway
        self._original_user_sender = public_gateway.send_user_request
        self._original_character_sender = public_gateway.send_character_request
        self._original_user_blocking_sender = public_gateway.send_blocking_user_request_and_receive_response
        self._original_character_blocking_sender = public_gateway.send_blocking_character_request_and_receive_response
        self._is_enabled = None
        self._error = None
        self._latency = None

    def load_data(self):
        self._load_data_from_settings()
        self._apply()

    def get_data(self):
        return (self._is_enabled, self._error, self._latency)

    def enable(self, error, latency):
        self._is_enabled = True
        self._error = error
        self._latency = latency
        self._save_data_and_apply()

    def disable(self):
        self._is_enabled = False
        self._error = None
        self._latency = None
        self._save_data_and_apply()

    def _apply(self):
        if self._is_enabled:
            self._hijack_methods()
        else:
            self._revert_methods_to_original()

    def _load_data_from_settings(self):
        self._is_enabled = settings.user.ui.Get(self.SETTING_PUBLIC_REQUEST_HIJACKER_ENABLED, False)
        self._error = settings.user.ui.Get(self.SETTING_PUBLIC_REQUEST_HIJACKER_ERROR, None)
        self._latency = settings.user.ui.Get(self.SETTING_PUBLIC_REQUEST_HIJACKER_LATENCY, None)

    def _save_data_and_apply(self):
        self._save_data_in_settings()
        self._apply()

    def _save_data_in_settings(self):
        settings.user.ui.Set(self.SETTING_PUBLIC_REQUEST_HIJACKER_ENABLED, self._is_enabled)
        settings.user.ui.Set(self.SETTING_PUBLIC_REQUEST_HIJACKER_ERROR, self._error)
        settings.user.ui.Set(self.SETTING_PUBLIC_REQUEST_HIJACKER_LATENCY, self._latency)
        settings.user.WriteToDiskImmediate()

    def _revert_methods_to_original(self):
        self.public_gateway.send_user_request = self._original_user_sender
        self.public_gateway.send_character_request = self._original_character_sender
        self.public_gateway.send_blocking_user_request_and_receive_response = self._original_user_blocking_sender
        self.public_gateway.send_blocking_character_request_and_receive_response = self._original_character_blocking_sender

    def _hijack_methods(self):
        self.public_gateway.send_user_request = lambda *args, **kwargs: self._hijacked_method(self._error, self._latency, self._original_user_sender, *args, **kwargs)
        self.public_gateway.send_character_request = lambda *args, **kwargs: self._hijacked_method(self._error, self._latency, self._original_character_sender, *args, **kwargs)
        self.public_gateway.send_blocking_user_request_and_receive_response = lambda *args, **kwargs: self._hijacked_blocking_method(self._error, self._latency, self._original_user_blocking_sender, *args, **kwargs)
        self.public_gateway.send_blocking_character_request_and_receive_response = lambda *args, **kwargs: self._hijacked_blocking_method(self._error, self._latency, self._original_character_blocking_sender, *args, **kwargs)

    def _hijacked_method(self, error, latency, original_method, *args, **kwargs):
        if latency:
            Sleep(latency)
        if not error:
            return original_method(*args, **kwargs)
        if isinstance(error, type) and issubclass(error, Exception):
            raise error()
        request_primitive = None
        response_channel = MockResponseChannel(error)
        return (request_primitive, response_channel)

    def _hijacked_blocking_method(self, error, latency, original_method, *args, **kwargs):
        if latency:
            Sleep(latency)
        if not error:
            return original_method(*args, **kwargs)
        if isinstance(error, type) and issubclass(error, Exception):
            raise error()
        response_primitive = MockResponsePrimitive(error)
        response_payload = None
        return (response_primitive, response_payload)
