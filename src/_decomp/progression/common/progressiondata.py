#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\progression\common\progressiondata.py


class TaskWidgetData(object):

    def __init__(self, task_id, task_widget_id, widget_state):
        self.task_id = task_id
        self.task_widget_id = task_widget_id
        self.widget_state = widget_state


class ObjectiveData(object):

    def __init__(self, objective_id, room_ids, title, description, tasks, task_widgets):
        self.objective_id = objective_id
        self.room_ids = room_ids
        self.title = title
        self.description = description
        self.tasks = tasks
        self.task_widgets = task_widgets
