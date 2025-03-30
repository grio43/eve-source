#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\beeline\propagation\__init__.py
import six
from abc import ABCMeta, abstractmethod
import beeline

class PropagationContext(object):

    def __init__(self, trace_id, parent_id, trace_fields = {}, dataset = None):
        self.trace_id = trace_id
        self.parent_id = parent_id
        self.trace_fields = trace_fields
        self.dataset = dataset


@six.add_metaclass(ABCMeta)

class Request(object):

    @abstractmethod
    def header(self, key):
        pass

    @abstractmethod
    def method(self):
        pass

    @abstractmethod
    def scheme(self):
        pass

    @abstractmethod
    def host(self):
        pass

    @abstractmethod
    def path(self):
        pass

    @abstractmethod
    def query(self):
        pass

    @abstractmethod
    def middleware_request(self):
        pass


class DictRequest(Request):

    def __init__(self, headers, props = {}):
        self._headers = headers
        self._props = props
        self._keymap = {k.lower():k for k in self._headers.keys()}

    def header(self, key):
        lookup_key = key.lower()
        if lookup_key not in self._keymap:
            return None
        lookup_key = self._keymap[lookup_key]
        return self._headers[lookup_key]

    def method(self):
        return self._props['method']

    def scheme(self):
        return self._props['scheme']

    def host(self):
        return self._props['host']

    def path(self):
        return self._props['path']

    def query(self):
        return self._props['query']

    def middleware_request(self):
        return {'headers': self._headers,
         'props': self._props}
