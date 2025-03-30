#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\beeline\middleware\awslambda\__init__.py
import traceback
import beeline
from beeline.propagation import Request
COLD_START = True

class LambdaRequest(Request):

    def __init__(self, event):
        self._type = None
        self._event = event
        if isinstance(event, dict):
            if 'headers' in event:
                if isinstance(event['headers'], dict):
                    self._attributes = event['headers']
                    self._type = 'headers'
            elif 'Records' in event:
                if len(event['Records']) == 1:
                    if 'EventSource' in event['Records'][0]:
                        if event['Records'][0]['EventSource'] == 'aws:sns':
                            self._attributes = event['Records'][0]['Sns']['MessageAttributes']
                            self._type = 'sns'
                    elif 'eventSource' in event['Records'][0]:
                        if event['Records'][0]['eventSource'] == 'aws:sqs':
                            self._attributes = event['Records'][0]['messageAttributes']
                            self._type = 'sqs'
            if self._type:
                self._keymap = {k.lower():k for k in self._attributes.keys()}

    def header(self, key):
        if not self._type:
            return None
        lookup_key = key.lower()
        if lookup_key not in self._keymap:
            return None
        lookup_key = self._keymap[lookup_key]
        if self._type == 'headers':
            return self._attributes[lookup_key]
        if self._type == 'sns':
            return self._attributes[lookup_key]['Value']
        if self._type == 'sqs':
            return self._attributes[lookup_key]['stringValue']

    def method(self):
        return None

    def scheme(self):
        return None

    def host(self):
        return None

    def path(self):
        return None

    def query(self):
        return None

    def middleware_request(self):
        return self._event


def beeline_wrapper(handler = None, record_input = True, record_output = True):

    def _beeline_wrapper(event, context):
        global COLD_START
        if not beeline.get_beeline():
            return handler(event, context)
        root_span = None
        try:
            request_context = {'app.function_name': getattr(context, 'function_name', ''),
             'app.function_version': getattr(context, 'function_version', ''),
             'app.request_id': getattr(context, 'aws_request_id', ''),
             'meta.cold_start': COLD_START,
             'name': handler.__name__}
            if record_input:
                request_context['app.event'] = event
            lr = LambdaRequest(event)
            root_span = beeline.propagate_and_start_trace(request_context, lr)
            resp = handler(event, context)
            if resp is not None and record_output:
                beeline.add_context_field('app.response', resp)
            return resp
        except Exception as e:
            beeline.add_context({'app.exception_type': str(type(e)),
             'app.exception_string': beeline.internal.stringify_exception(e),
             'app.exception_stacktrace': traceback.format_exc()})
            raise e
        finally:
            COLD_START = False
            beeline.finish_trace(root_span)
            beeline.get_beeline().client.flush()

    def outer_wrapper(*args, **kwargs):
        return beeline_wrapper(record_input=record_input, record_output=record_output, *args, **kwargs)

    if handler:
        return _beeline_wrapper
    return outer_wrapper
