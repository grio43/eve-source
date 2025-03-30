#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\actions\base.py
import threadutils
import uthread2
import logging
from nodegraph.common.atom import Atom
logger = logging.getLogger('client_trigger action')

class Action(Atom):

    def __init__(self, on_end = None, **kwargs):
        self._on_end_callback = on_end

    @threadutils.threaded
    def start_threaded(self, delay = None, **kwargs):
        if delay:
            uthread2.sleep(delay)
        self.start(**kwargs)

    def start(self, **kwargs):
        logger.info(u'%s Started - %s %s', self.__class__.__name__, self.__dict__, kwargs)

    def stop(self):
        logger.info(u'%s Stopped - %s', self.__class__.__name__, self.__dict__)

    def _on_end(self):
        if self._on_end_callback:
            self._on_end_callback()
