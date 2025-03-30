#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uiblinker\disposable.py
import logging
import signals
import uthread2
logger = logging.getLogger(__name__)

class Disposable(object):

    def __init__(self, value, finalizer, on_disposed = None):
        self._disposed = False
        self._value = value
        self._finalizer = finalizer
        self._on_disposed = None
        if on_disposed is not None:
            self.on_disposed.connect(on_disposed)

    @property
    def disposed(self):
        return self._disposed

    @property
    def on_disposed(self):
        if self._on_disposed is None:
            self._on_disposed = signals.Signal('on_disposed')
        return self._on_disposed

    def dispose(self):
        if not self._disposed:
            uthread2.start_tasklet(self._finalizer, self._value)
            self._value = None
            self._disposed = True
            if self._on_disposed is not None:
                uthread2.start_tasklet(self._on_disposed, self)

    def __del__(self):
        try:
            self.dispose()
        except Exception:
            logger.exception('Exception caught while deleting a Disposable')
