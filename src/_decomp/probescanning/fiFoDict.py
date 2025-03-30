#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\probescanning\fiFoDict.py
from collections import OrderedDict

class FiFoDict(OrderedDict):

    def __init__(self, max_size = 0, default_factory = None, *args, **kwargs):
        self.max_size = max_size
        OrderedDict.__init__(self, *args, **kwargs)
        self.default_factory = default_factory
        if default_factory and not callable(self.default_factory):
            raise TypeError('default_factory must be callable')
        self.factory_params = kwargs.pop('factory_params', None)

    def __setitem__(self, key, value, *args):
        OrderedDict.__setitem__(self, key, value)
        self._check_size_limit()

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        if self.factory_params:
            self[key] = value = self.default_factory(*self.factory_params)
        else:
            self[key] = value = self.default_factory()
        return value

    def update(self, other = (), **kwargs):
        if other:
            OrderedDict.update(self, other=other, **kwargs)
            self._check_size_limit()

    def _check_size_limit(self):
        if self.max_size is not None:
            while len(self) > self.max_size:
                self.popitem(last=False)
