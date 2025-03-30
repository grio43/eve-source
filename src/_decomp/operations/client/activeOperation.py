#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\operations\client\activeOperation.py
import signals
import threadutils
from operations.common.fsdloaders import OperationsLoader

class ActiveOperations(object):
    __notifyevents__ = ['OnOperationMadeActive',
     'OnOperationCompleted',
     'OnOperationQuit',
     'OnOperationTaskMadeActive']

    def __init__(self, get_active_task_id):
        sm.RegisterNotify(self)
        self._operations = {}
        self._get_active_task_id = get_active_task_id

    def stop(self):
        sm.UnregisterNotify(self)
        for active_operation in self._operations.itervalues():
            active_operation.stop()

        self._operations.clear()

    def has_operations(self):
        return bool(self._operations)

    def get_operations(self):
        return sorted(self._operations.items(), key=lambda operation: operation.start_date_time)

    def OnOperationMadeActive(self, category_id, operation_id, old_active_category_id, old_active_operation_id, is_silent):
        if operation_id in self._operations:
            return
        self._operations[operation_id] = ActiveOperation(operation_id, self._get_active_task_id())
        operation = self._operations.pop(old_active_operation_id, None)
        if operation:
            operation.complete()

    def OnOperationCompleted(self, category_id, operation_id):
        operation = self._operations.pop(operation_id, None)
        if operation:
            operation.complete()

    def OnOperationQuit(self, category_id, operation_id):
        if self._operations:
            operation_id = list(self._operations.keys())[0]
        operation = self._operations.pop(operation_id, None)
        if operation:
            operation.quit()

    def OnOperationTaskMadeActive(self, task_id, old_task_id, operation_id):
        if operation_id in self._operations:
            self._operations[operation_id].set_active_task(task_id)


class ActiveOperation(object):

    def __init__(self, operation_id, active_task_id):
        self.operation_id = operation_id
        self.active_task_id = active_task_id
        self.node_graph = None
        self.objectives = {}
        self.authored_data = None
        self.on_complete = signals.Signal('on_complete')
        self.on_end = signals.Signal('on_end')
        self.on_update = signals.Signal('on_update')
        self._initializing = True
        self._initialize()

    @threadutils.threaded
    def _initialize(self):
        self.authored_data = OperationsLoader.GetByID(self.operation_id)
        node_graph_id = getattr(self.authored_data, 'clientNodeGraph', None)
        self.node_graph = None
        if node_graph_id:
            self.node_graph = sm.GetService('node_graph').start_node_graph(node_graph_id, blackboard_parameters={'operation_id': self.operation_id})
        self._initializing = False
        active_task_id = self.active_task_id
        if active_task_id:
            self.active_task_id = None
            self.set_active_task(active_task_id)

    def add_objective(self):
        pass

    def complete(self):
        self.stop()

    def quit(self):
        self.stop()

    def set_active_task(self, task_id):
        if self.active_task_id == task_id:
            return
        self.active_task_id = task_id
        if self._initializing:
            return
        if self.node_graph:
            self.node_graph.context.update_value('active_operation_task_id', task_id)

    def stop(self):
        if self.node_graph:
            sm.GetService('node_graph').stop_node_graph(self.node_graph.instance_id)
