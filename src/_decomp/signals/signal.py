#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\signals\signal.py
import inspect
import logging
import sys
import weakref

class Signal(object):

    def __init__(self, signalName = None):
        self._signalName = signalName
        self._functions = weakref.WeakSet()
        self._methods = weakref.WeakKeyDictionary()

    def __repr__(self):
        if self._signalName:
            nameText = self._signalName + ' '
        else:
            nameText = ''
        if len(self) > 0:
            return '%s%s connected to %s>' % (nameText, object.__repr__(self)[:-1], ','.join([ str(f) for f in self ]))
        return nameText + object.__repr__(self)

    def __call__(self, *args, **kwargs):
        for call in self:
            try:
                call(*args, **kwargs)
            except Exception:
                logging.exception('Exception in signal handler: {}'.format(call))
                sys.exc_clear()

    def __len__(self):
        return len(self._functions) + sum([ len(methods) for methods in self._methods.itervalues() ])

    def __iter__(self):
        callables = []
        callables.extend(self._functions)
        for obj, funcs in self._methods.items():
            callables.extend([ func.__get__(obj) for func in funcs ])

        return iter(callables)

    def connect(self, slot):
        if inspect.ismethod(slot):
            if slot.__self__ not in self._methods:
                self._methods[slot.__self__] = weakref.WeakSet()
            self._methods[slot.__self__].add(slot.__func__)
        elif inspect.isfunction(slot) and slot.__name__ == '<lambda>':
            raise TypeError('Signal cannot connect lambda methods')
        elif callable(slot):
            self._functions.add(slot)
        else:
            raise TypeError('Signal connect requires a callable slot')

    def disconnect(self, slot):
        if inspect.ismethod(slot):
            if slot.__self__ in self._methods:
                self._methods[slot.__self__].discard(slot.__func__)
        else:
            self._functions.discard(slot)

    def clear(self):
        self._functions.clear()
        self._methods.clear()

    @property
    def debugDisplayName(self):
        return self._signalName
