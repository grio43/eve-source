#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sentry_sdk\serializer.py
import contextlib
from datetime import datetime
from sentry_sdk.utils import AnnotatedValue, capture_internal_exceptions, safe_repr, strip_string
from sentry_sdk._compat import text_type, PY2, string_types, number_types, iteritems
if False:
    from typing import Any
    from typing import Dict
    from typing import List
    from typing import Optional
if PY2:
    from collections import Mapping, Sequence
else:
    from collections.abc import Mapping, Sequence
MAX_DATABAG_DEPTH = 5
MAX_DATABAG_BREADTH = 10
CYCLE_MARKER = u'<cyclic>'
global_repr_processors = []

def add_global_repr_processor(processor):
    global_repr_processors.append(processor)


class MetaNode(object):
    __slots__ = ('_parent', '_segment', '_depth', '_data', '_is_databag', '_should_repr_strings')

    def __init__(self):
        self._parent = None
        self._segment = None
        self._depth = 0
        self._data = None
        self._is_databag = None
        self._should_repr_strings = None

    def startswith_path(self, path):
        if len(path) > self._depth:
            return False
        return self.is_path(path + [None] * (self._depth - len(path)))

    def is_path(self, path):
        if len(path) != self._depth:
            return False
        cur = self
        for segment in reversed(path):
            if segment is not None and segment != cur._segment:
                return False
            cur = cur._parent

        return cur._segment is None

    def enter(self, segment):
        rv = MetaNode()
        rv._parent = self
        rv._depth = self._depth + 1
        rv._segment = segment
        return rv

    def _create_annotations(self):
        if self._data is not None:
            return
        self._data = {}
        if self._parent is not None:
            self._parent._create_annotations()
            self._parent._data[str(self._segment)] = self._data

    def annotate(self, **meta):
        self._create_annotations()
        self._data.setdefault('', {}).update(meta)

    def should_repr_strings(self):
        if self._should_repr_strings is None:
            self._should_repr_strings = self.startswith_path(['exception',
             'values',
             None,
             'stacktrace',
             'frames',
             None,
             'vars']) or self.startswith_path(['threads',
             'values',
             None,
             'stacktrace',
             'frames',
             None,
             'vars']) or self.startswith_path(['stacktrace',
             'frames',
             None,
             'vars'])
        return self._should_repr_strings

    def is_databag(self):
        if self._is_databag is None:
            self._is_databag = self.startswith_path(['request', 'data']) or self.startswith_path(['breadcrumbs', None]) or self.startswith_path(['extra']) or self.startswith_path(['exception',
             'values',
             None,
             'stacktrace',
             'frames',
             None,
             'vars']) or self.startswith_path(['threads',
             'values',
             None,
             'stacktrace',
             'frames',
             None,
             'vars']) or self.startswith_path(['stacktrace',
             'frames',
             None,
             'vars'])
        return self._is_databag


def _flatten_annotated(obj, meta_node):
    if isinstance(obj, AnnotatedValue):
        meta_node.annotate(**obj.metadata)
        obj = obj.value
    return obj


class Memo(object):

    def __init__(self):
        self._inner = {}

    @contextlib.contextmanager
    def memoize(self, obj):
        if id(obj) in self._inner:
            yield True
        else:
            self._inner[id(obj)] = obj
            yield False
            self._inner.pop(id(obj), None)


class Serializer(object):

    def __init__(self):
        self.memo = Memo()
        self.meta_node = MetaNode()

    @contextlib.contextmanager
    def enter(self, segment):
        old_node = self.meta_node
        self.meta_node = self.meta_node.enter(segment)
        try:
            yield
        finally:
            self.meta_node = old_node

    def serialize_event(self, obj):
        rv = self._serialize_node(obj)
        if self.meta_node._data is not None:
            rv['_meta'] = self.meta_node._data
        return rv

    def _serialize_node(self, obj, **kwargs):
        with capture_internal_exceptions():
            with self.memo.memoize(obj) as result:
                if result:
                    return CYCLE_MARKER
                return self._serialize_node_impl(obj, **kwargs)
        if self.meta_node.is_databag():
            return u'<failed to serialize, use init(debug=True) to see error logs>'

    def _serialize_node_impl(self, obj, max_depth = None, max_breadth = None):
        if max_depth is None and max_breadth is None and self.meta_node.is_databag():
            max_depth = self.meta_node._depth + MAX_DATABAG_DEPTH
            max_breadth = self.meta_node._depth + MAX_DATABAG_BREADTH
        if max_depth is None:
            remaining_depth = None
        else:
            remaining_depth = max_depth - self.meta_node._depth
        obj = _flatten_annotated(obj, self.meta_node)
        if remaining_depth is not None and remaining_depth <= 0:
            self.meta_node.annotate(rem=[['!limit', 'x']])
            if self.meta_node.is_databag():
                return _flatten_annotated(strip_string(safe_repr(obj)), self.meta_node)
            return
        if self.meta_node.is_databag():
            hints = {'memo': self.memo,
             'remaining_depth': remaining_depth}
            for processor in global_repr_processors:
                with capture_internal_exceptions():
                    result = processor(obj, hints)
                    if result is not NotImplemented:
                        return _flatten_annotated(result, self.meta_node)

        if isinstance(obj, Mapping):
            items = []
            for i, (k, v) in enumerate(iteritems(obj)):
                if max_breadth is not None and i >= max_breadth:
                    self.meta_node.annotate(len=max_breadth)
                    break
                items.append((k, v))

            rv_dict = {}
            for k, v in items:
                k = text_type(k)
                with self.enter(k):
                    v = self._serialize_node(v, max_depth=max_depth, max_breadth=max_breadth)
                    if v is not None:
                        rv_dict[k] = v

            return rv_dict
        if isinstance(obj, Sequence) and not isinstance(obj, string_types):
            rv_list = []
            for i, v in enumerate(obj):
                if max_breadth is not None and i >= max_breadth:
                    self.meta_node.annotate(len=max_breadth)
                    break
                with self.enter(i):
                    rv_list.append(self._serialize_node(v, max_depth=max_depth, max_breadth=max_breadth))

            return rv_list
        if self.meta_node.should_repr_strings():
            obj = safe_repr(obj)
        else:
            if obj is None or isinstance(obj, (bool, number_types)):
                return obj
            if isinstance(obj, datetime):
                return text_type(obj.strftime('%Y-%m-%dT%H:%M:%SZ'))
            if isinstance(obj, bytes):
                obj = obj.decode('utf-8', 'replace')
            if not isinstance(obj, string_types):
                obj = safe_repr(obj)
        return _flatten_annotated(strip_string(obj), self.meta_node)
