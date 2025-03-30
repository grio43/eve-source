#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\beeline\patch\urllib.py
from wrapt import wrap_function_wrapper
import beeline
import beeline.propagation
import urllib.request

def _urllibopen(_urlopen, instance, args, kwargs):
    if type(args[0]) != urllib.request.Request:
        args = (urllib.request.Request(args[0]),) + tuple(args[1:])
    span = beeline.start_span(context={'meta.type': 'http_client'})
    b = beeline.get_beeline()
    if b and b.http_trace_propagation_hook is not None:
        new_headers = beeline.http_trace_propagation_hook()
        if new_headers:
            b.log('urllib lib - adding trace context to outbound request: %s', new_headers)
            args[0].headers.update(new_headers)
    try:
        resp = None
        beeline.add_context({'name': 'urllib_%s' % args[0].get_method(),
         'request.method': args[0].get_method(),
         'request.uri': args[0].full_url})
        resp = _urlopen(*args, **kwargs)
        return resp
    except Exception as e:
        beeline.add_context({'request.error_type': str(type(e)),
         'request.error': beeline.internal.stringify_exception(e)})
        raise
    finally:
        if resp:
            beeline.add_context_field('response.status_code', resp.status)
            content_type = resp.getheader('content-type')
            if content_type:
                beeline.add_context_field('response.content_type', content_type)
            content_length = resp.getheader('content-length')
            if content_length:
                beeline.add_context_field('response.content_length', content_length)
        beeline.finish_span(span)


wrap_function_wrapper('urllib.request', 'urlopen', _urllibopen)
