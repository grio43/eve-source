#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\common\log.py
import logging
import datetime
import signals
from eveprefs import prefs, boot
from carbon.common.script.sys.serviceConst import ROLE_QA
logger = logging.getLogger('node_graph')

class NodeGraphLog(object):

    def __init__(self, node_graph_id, node_graph_instance_id):
        self._node_graph_id = node_graph_id
        self._node_graph_instance_id = node_graph_instance_id
        if boot.role == 'client':
            self._keep_cached = bool(session.role & ROLE_QA)
        else:
            self._keep_cached = prefs.clusterMode != 'LIVE'
        self.history = []
        self.on_log = signals.Signal()

    def graph_starting(self, **kwargs):
        self._log('graph', 'starting', kwargs)

    def graph_started(self, **kwargs):
        self._log('graph', 'started', kwargs)

    def graph_stopped(self, **kwargs):
        self._log('graph', 'stopped', kwargs)

    def node_started(self, **kwargs):
        self._log('node', 'started', kwargs)

    def node_stopped(self, **kwargs):
        self._log('node', 'stopped', kwargs)

    def node_active(self, **kwargs):
        self._log('node', 'active', kwargs)

    def node_inactive(self, **kwargs):
        self._log('node', 'inactive', kwargs)

    def node_connection_started(self, **kwargs):
        self._log('node', 'connection_started', kwargs)

    def node_connection_stopped(self, **kwargs):
        self._log('node', 'connection_stopped', kwargs)

    def node_get_values(self, **kwargs):
        self._log('node', 'get_values', kwargs)

    def blackboard_update(self, **kwargs):
        self._log('blackboard', 'update', kwargs)

    def _log(self, from_type, event, info):
        result = {'node_graph_id': self._node_graph_id,
         'node_graph_instance_id': self._node_graph_instance_id,
         'type': from_type,
         'event': event,
         'info': info}
        logger.info(result)
        if self._keep_cached:
            result['timestamp'] = datetime.datetime.now().isoformat()
            self.history.append(result)
            self.on_log(result)
