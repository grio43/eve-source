#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\stackless_tracing\tasklet_tracer.py
from attributes import SPAN_NAME, SERVICE_NAME, SPAN_KIND, TASKLET_CONTEXT, TASKLET_PARENT_CALLSITE
import stackless_tracing
import monolithconfig
NO_TRACE_METHOD_NAMES = [None, 'inner', 'MollycoddledUthread']
NO_TRACE_MODULE_NAMES = [None, 'uthread']

class TaskletTracer(object):

    def __init__(self, tasklet):
        self.tasklet = tasklet
        self.span = None

    def __enter__(self):
        self.module_name = getattr(self.tasklet, 'module_name', '').split('.')[-1]
        self.method_name = getattr(self.tasklet, 'method_name')
        if not self._is_traceable():
            return
        span_name = '{}.{}'.format(self.module_name, self.method_name)
        self.span, trace_context = stackless_tracing.start_span(span_name, self.module_name)
        if not stackless_tracing.get_sampled_from_context(trace_context):
            return self
        parent_callsite = getattr(self.tasklet, 'parent_callsite', '')
        tasklet_context = getattr(self.tasklet, 'context', '')
        self.span.add_context({SPAN_KIND: 'internal',
         TASKLET_CONTEXT: tasklet_context,
         TASKLET_PARENT_CALLSITE: parent_callsite})
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        stackless_tracing.end_span(self.span)

    def _is_traceable(self):
        if not monolithconfig.on_server():
            return False
        if self.method_name in NO_TRACE_METHOD_NAMES:
            return False
        if self.module_name in NO_TRACE_MODULE_NAMES:
            return False
        return True
