#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodditests\client\runner.py
import time
from carbonui.uicore import uicore
from eve.client.script.util.sessiontools import wait_for_session_ready

class Runner(object):
    __notifyevents__ = ['OnCharacterSelectionViewEntered',
     'OnGameViewEntered',
     'OnTestStarted',
     'OnTestSucceeded',
     'OnTestFailed',
     'OnTestMetaDataLogged',
     'OnNodeGraphStopped']

    def __init__(self, arguments, select_character, run_node_graph, reporter):
        self._character_id = arguments.get_int_value('/select_character')
        self._node_graph_id = arguments.get_int_value('/noddi_test')
        self._close_at_completion = arguments.has_argument('/noddi_close_at_completion')
        self._select_character = select_character
        self._run_node_graph = run_node_graph
        self._reporter = reporter
        self._node_graph_instance_id = None

    def OnCharacterSelectionViewEntered(self):
        self._reporter.log_character_select(self._character_id)
        self._select_character(self._character_id)

    def OnGameViewEntered(self):
        wait_for_session_ready()
        self._node_graph_instance_id = self._run_node_graph(self._node_graph_id)
        self._reporter.log_node_graph_started(self._node_graph_id)

    def OnTestStarted(self, step):
        self._reporter.log_test_update(step, 'testStarted')

    def OnTestSucceeded(self, step):
        self._reporter.log_test_update(step, 'testFinished')

    def OnTestFailed(self, step, reason):
        self._reporter.log_test_update(step, 'testFailed')

    def OnTestMetaDataLogged(self, step, key, value):
        self._reporter.log_test_metadata(step, key, value)

    def OnNodeGraphStopped(self, instance_id, node_graph_id):
        if instance_id == self._node_graph_instance_id:
            self._reporter.log_node_graph_completed(self._node_graph_id)
            if self._close_at_completion:
                time.sleep(2)
                uicore.cmd.DoQuitGame()
