#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\libhoney\fields.py
import inspect
import json
from libhoney.internal import json_default_handler

class FieldHolder:

    def __init__(self):
        self._data = {}
        self._dyn_fields = set()

    def __add__(self, other):
        self._data.update(other._data)
        self._dyn_fields.update(other._dyn_fields)
        return self

    def __eq__(self, other):
        return (self._data, self._dyn_fields) == (other._data, other._dyn_fields)

    def __ne__(self, other):
        return not self.__eq__(other)

    def add_field(self, name, val):
        self._data[name] = val

    def add_dynamic_field(self, fn):
        if not inspect.isroutine(fn):
            raise TypeError('add_dynamic_field requires function argument')
        self._dyn_fields.add(fn)

    def add(self, data):
        try:
            for k, v in data.items():
                self.add_field(k, v)

        except AttributeError:
            raise TypeError('add requires a dict-like argument')

    def is_empty(self):
        return len(self._data) == 0

    def __str__(self):
        return json.dumps(self._data, default=json_default_handler)
