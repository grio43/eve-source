#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\beeline\propagation\honeycomb.py
import beeline
from beeline.propagation import PropagationContext
import base64
import json
from urllib import quote, unquote

def http_trace_parser_hook(request):
    trace_header = request.header('X-Honeycomb-Trace')
    if trace_header:
        try:
            trace_id, parent_id, context, dataset = unmarshal_propagation_context_with_dataset(trace_header)
            return PropagationContext(trace_id, parent_id, context, dataset)
        except Exception as e:
            beeline.internal.log('error attempting to extract trace context: %s', beeline.internal.stringify_exception(e))


def http_trace_propagation_hook(propagation_context):
    if not propagation_context:
        return None
    return {'X-Honeycomb-Trace': marshal_propagation_context(propagation_context)}


def marshal_propagation_context(propagation_context):
    if not propagation_context:
        return None
    version = 1
    trace_fields = base64.b64encode(json.dumps(propagation_context.trace_fields).encode()).decode()
    components = ['trace_id={}'.format(propagation_context.trace_id), 'parent_id={}'.format(propagation_context.parent_id), 'context={}'.format(trace_fields)]
    if propagation_context.dataset:
        components.insert(0, 'dataset={}'.format(quote(propagation_context.dataset)))
    trace_header = '{};{}'.format(version, ','.join(components))
    return trace_header


def unmarshal_propagation_context(trace_header):
    trace_id, parent_id, context, _dataset = unmarshal_propagation_context_with_dataset(trace_header)
    return (trace_id, parent_id, context)


def unmarshal_propagation_context_with_dataset(trace_header):
    version, data = trace_header.split(';', 1)
    if version != '1':
        beeline.internal.log('warning: trace_header version %s is unsupported', version)
        return (None, None, None, None)
    kv_pairs = data.split(',')
    trace_id, parent_id, context, dataset = (None, None, None, None)
    for pair in kv_pairs:
        k, v = pair.split('=', 1)
        if k == 'trace_id':
            trace_id = v
        elif k == 'parent_id':
            parent_id = v
        elif k == 'context':
            context = json.loads(base64.b64decode(v.encode()).decode())
        elif k == 'dataset':
            dataset = unquote(v)

    if context is None:
        context = {}
    return (trace_id,
     parent_id,
     context,
     dataset)
