#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\nodes\other.py
import threadutils
from nodegraph.client.util import wait_for_session
from nodegraph.common.nodes.base import Node
from nodegraph.common.nodedata import OutPort

class WaitForSession(Node):
    node_type_id = 51

    def start(self, **kwargs):
        super(WaitForSession, self).start(**kwargs)
        self._start_thread()

    @threadutils.threaded
    def _start_thread(self, **kwargs):
        if not session.charid:
            return
        wait_for_session()
        self._start_connection(OutPort.output, **kwargs)
