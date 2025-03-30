#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\publicGateway\notice\signal_registry.py
import signals
import inspect
from google.protobuf.message import Message as ProtobufMessage

class NoticeSignalRegistry(object):

    def __init__(self):
        self._signals_by_payload_type_name = {}
        self._rooted_deserialize_funcs = []

    def subscribe_to_notice(self, notice, function):
        if not inspect.isclass(notice):
            raise RuntimeError('notice argument must be a class')
        if not issubclass(notice, ProtobufMessage):
            raise RuntimeError('notice class must be a protobuf message')
        notice_payload_type_name = self._get_message_name(notice)

        def deserialize_and_call(notice_primitive):
            notice_payload = notice()
            notice_primitive.payload.Unpack(notice_payload)
            function(notice_payload, notice_primitive)

        self._rooted_deserialize_funcs.append(deserialize_and_call)
        if notice_payload_type_name not in self._signals_by_payload_type_name:
            self._signals_by_payload_type_name[notice_payload_type_name] = signals.Signal()
        signal = self._signals_by_payload_type_name[notice_payload_type_name]
        signal.connect(deserialize_and_call)

    def invoke_signal_for_notice(self, notice_primitive):
        payload_name = self._get_notice_payload_name(notice_primitive)
        signal = self._signals_by_payload_type_name.get(payload_name, None)
        if signal is None:
            return
        signal(notice_primitive)

    @staticmethod
    def _get_message_name(notice):
        return notice.DESCRIPTOR.full_name

    @staticmethod
    def _get_notice_payload_name(notice):
        return notice.payload.TypeName()
