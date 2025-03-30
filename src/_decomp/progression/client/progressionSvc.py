#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\progression\client\progressionSvc.py
from carbon.common.script.sys.service import Service
from localization import GetByMessageID
from progression.common.objectives import load_objective
from progression.common.progressiondata import ObjectiveData, TaskWidgetData
from progression.common.tasks import load_task
from progression.common.widgets import load_widget

class ProgressionService(Service):
    __guid__ = 'svc.progressionSvc'
    __notifyevents__ = ['OnProgressionRoomJoined',
     'OnProgressionLeft',
     'OnProgressionAdvanced',
     'OnProgressionTaskWidgetUpdate',
     'OnProgressionTaskCompleted']
    __dependencies__ = ['infoPanel', 'uiHighlightingService']

    def __init__(self):
        super(ProgressionService, self).__init__()
        self.progressionContainer = None
        self.progressionHistoryCache = []
        self.objective_data = None
        self.current_room_id = None
        self.last_task_completed = None
        self.inDungeon = False
        self.widget_cache = {}
        self.progression_name_id = None

    def _update_task_widget_cache_from_list(self, task_widget_states):
        for widget_state in task_widget_states:
            task_id, task_widget_id, widget_state = widget_state
            self.widget_cache[task_id, task_widget_id] = widget_state

    def OnProgressionRoomJoined(self, progression_name_id, objective_id, task_widget_states, objective_history, roomID):
        self.progression_name_id = progression_name_id
        self._update_task_widget_cache_from_list(task_widget_states)
        self.progressionHistoryCache = [ load_objective(objective_id) for objective_id in objective_history ]
        self.CreateObjectiveData(objective_id)
        self.current_room_id = roomID
        self.inDungeon = True
        self.infoPanel.UpdateDungeonProgressionPanel()
        sm.ScatterEvent('OnProgressionRoomJoinedUpdateInfoPanel')

    def OnProgressionLeft(self):
        self.inDungeon = False
        self.widget_cache.clear()
        self.progressionHistoryCache = []
        self.progression_name_id = None
        self.objective_data = None
        self.current_room_id = None
        self.last_task_completed = None
        self.infoPanel.UpdateDungeonProgressionPanel()

    def OnProgressionAdvanced(self, objective_id, last_completed_task_id):
        self.last_task_completed = last_completed_task_id
        self.CreateObjectiveData(objective_id)
        self.progressionHistoryCache.append(self.objective_data)
        sm.ScatterEvent('OnProgressionAdvancedUpdateInfoPanel')

    def IsInDungeon(self):
        return self.inDungeon

    def GetObjectiveData(self):
        return self.objective_data

    def GetCurrentRoomID(self):
        return self.current_room_id

    def GetLastTaskCompleted(self):
        return self.last_task_completed

    def GetProgressionHistory(self):
        return self.progressionHistoryCache

    def get_task_data(self, task_id):
        return load_task(task_id)

    def get_task_widget_data(self, task_widget_id):
        return load_widget(task_widget_id)

    def OnProgressionTaskWidgetUpdate(self, task_id, task_widget_id, widget_state):
        self.widget_cache[task_id, task_widget_id] = widget_state
        sm.ScatterEvent('OnProgressionTaskWidgetUpdateInfoPanel')

    def OnProgressionTaskCompleted(self, task_id):
        self.last_task_completed = task_id
        for cached_task_id, cached_task_widget_id in self.widget_cache.keys():
            if task_id == cached_task_id:
                self.widget_cache.pop((cached_task_id, cached_task_widget_id), None)

        sm.ScatterEvent('OnProgressionTaskCompleteUpdateInfoPanel')

    def get_widget_state(self, task_id, widget_id):
        return self.widget_cache.get((task_id, widget_id), None)

    def get_widget_states_for_task(self, task_id):
        widget_states = []
        task_static_data = load_task(task_id)
        for task_widget_id in task_static_data.task_widgets:
            widget_state = TaskWidgetData(task_id, task_widget_id, self.get_widget_state(task_id, task_widget_id))
            widget_states.append(widget_state)

        return widget_states

    def CreateObjectiveData(self, objective_id):
        objective_static_data = load_objective(objective_id)
        task_widget_data_list = []
        for task_id in objective_static_data.tasks:
            task_widget_data_list.extend(self.get_widget_states_for_task(task_id))

        self.objective_data = ObjectiveData(objective_id, objective_static_data.room_ids, objective_static_data.title, objective_static_data.description, objective_static_data.tasks, task_widget_data_list)

    def get_progression_name(self):
        return GetByMessageID(self.progression_name_id)
