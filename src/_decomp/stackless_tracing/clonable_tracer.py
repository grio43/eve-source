#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\stackless_tracing\clonable_tracer.py
from beeline.trace import Span, Trace
import beeline
import logging
import tasklet_tracer
_cut_span_names = set()
logger = logging.getLogger(__name__)

def set_cut_span_names(span_names):
    global _cut_span_names
    _cut_span_names = span_names


def is_cut(span_name):
    return span_name in _cut_span_names


class CloneableTracer(beeline.SynchronousTracer):

    def clone(self):
        new_tracer = CloneableTracer(self._client)
        if not self._trace:
            return None
        new_tracer._trace = self._trace.copy()
        return new_tracer

    @staticmethod
    def get_tasklet_tracer(t):
        return tasklet_tracer.TaskletTracer(t)

    def has_cut_parent(self):
        if len(self._trace.stack) == 0:
            return
        parent_span = self._trace.stack[-1]
        return self._was_cut(parent_span)

    def start_or_cut_span(self, span_name, context, trace_id, parent_id):
        if is_cut(span_name):
            return self._cut_span(span_name, trace_id, parent_id)
        if self.has_cut_parent():
            context.update({'eve.tracing.has_removed_parents': True})
        return self.start_span(context=context, parent_id=parent_id)

    def finish_span(self, span):
        if self._was_cut(span):
            return self._pop_cut_span()
        return super(CloneableTracer, self).finish_span(span)

    def start_or_cut_trace(self, span_name, context, trace_id, parent_id):
        if is_cut(span_name):
            return self._cut_span(span_name, trace_id, parent_id)
        return self.start_trace(context=context, trace_id=trace_id, parent_span_id=parent_id)

    def finish_trace(self, span):
        if self._was_cut(span):
            self._pop_cut_span()
            self._trace = None
            return
        return super(CloneableTracer, self).finish_trace(span)

    def _cut_span(self, span_name, trace_id, parent_span_id):
        if self._trace is None:
            if trace_id is None or parent_span_id is None:
                logger.error('cannot cut span, no active trace and supplied trace context is incomplete')
                return
            self._trace = Trace(trace_id, None)
        inactive_span = Span(trace_id=trace_id, parent_id=parent_span_id, id=parent_span_id, event=self._client.new_event(data=self._trace.fields), is_root=len(self._trace.stack) == 0)
        setattr(inactive_span, 'inactive_span', True)
        self._trace.stack.append(inactive_span)
        return inactive_span

    def _was_cut(self, span = None):
        if span is None:
            span = self.get_active_span()
        return hasattr(span, 'inactive_span')

    def _pop_cut_span(self):
        active_span = self.get_active_span()
        if not hasattr(active_span, 'inactive_span'):
            logger.error('invalid cut-span {}\nexpected a span with attribute "inactive_span" set'.format(active_span))
            return
        self._trace.stack.pop()
