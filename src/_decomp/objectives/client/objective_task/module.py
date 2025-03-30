#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\client\objective_task\module.py
import evetypes
import signals
from nodegraph.client.actions.blinks import BlinkUiElement
from nodegraph.client.conditions.module import ModuleActive
from nodegraph.client.getters.module import GetFittedModule
from objectives.client.objective_task.base import ObjectiveTask
from objectives.client.objective_task.target import TargetTask
from objectives.client.ui.objective_task_widget import ObjectiveTaskGroupWidget

class ActivateModuleTask(ObjectiveTask):
    objective_task_content_id = 23
    USE_TYPE_ICON = True
    __notifyevents__ = ['OnModuleActivated']

    def __init__(self, module_info = None, **kwargs):
        super(ActivateModuleTask, self).__init__(**kwargs)
        self._module_info = None
        self._fitted_module = None
        self.module_info = module_info

    def get_values(self):
        result = super(ActivateModuleTask, self).get_values()
        result['fitted_module'] = self._fitted_module
        return result

    @property
    def module_info(self):
        return self._module_info

    @module_info.setter
    def module_info(self, value):
        if self._module_info == value:
            return
        self._module_info = value
        self._update_module()

    def _update_module(self):
        if self._module_info:
            self._fitted_module = GetFittedModule(**self._module_info).get_values()
            type_id = self.type_id
        else:
            self._fitted_module = None
            type_id = None
        if type_id:
            self._title = evetypes.GetName(type_id)
        elif self._module_info.get('group_id'):
            self._title = evetypes.GetGroupNameByGroup(self._module_info['group_id'])
        else:
            self._title = ''
        if self._fitted_module and type_id:
            self.highlight = BlinkUiElement(ui_element_path='ModuleButton_{}'.format(type_id), blink_type='ring')
        else:
            self.highlight = None
        self.update()

    @property
    def type_id(self):
        if self._module_info:
            return self._fitted_module.get('type_id', self._module_info.get('type_id', None))
        else:
            return None

    def get_context_menu(self):
        type_id = self.type_id
        if type_id:
            return sm.GetService('menu').GetMenuFromItemIDTypeID(itemID=None, typeID=type_id, includeMarketDetails=False)
        else:
            return []

    def OnModuleActivated(self, *args, **kwargs):
        if self._is_module_active():
            self._on_module_activated()

    def _is_module_active(self):
        return ModuleActive(**self._module_info).validate()

    def _on_module_activated(self):
        self.completed = True


class ActivateModuleOnTargetTask(ActivateModuleTask):
    objective_task_content_id = 22
    WIDGET = ObjectiveTaskGroupWidget

    def __init__(self, target = None, show_module = True, **kwargs):
        kwargs['show_completed'] = False
        super(ActivateModuleOnTargetTask, self).__init__(**kwargs)
        self._target_task = TargetTask(target=target, task_id='module_target')
        self._show_module = show_module
        self.on_group_changed = signals.Signal('on_task_group_changed')

    @property
    def target(self):
        return self._target_task.target

    @target.setter
    def target(self, value):
        self._target_task.target = value

    def get_task_ids(self):
        return ('module', 'target')

    def get_total_tasks(self):
        return 2

    def construct_task_widget(self, task_id, *args, **kwargs):
        if task_id == 'module':
            if self._show_module:
                return ActivateModuleTask.WIDGET(objective_task=self, *args, **kwargs)
        elif task_id == 'target':
            return self._target_task.WIDGET(objective_task=self._target_task, *args, **kwargs)

    def is_module_active_on_target(self):
        return ModuleActive(target_item_id=self._target_task.item_id, **self._module_info).validate()

    def _on_module_activated(self):
        if self._target_task.item_id:
            self.completed = self.is_module_active_on_target()
        else:
            self.completed = False

    def _start(self):
        super(ActivateModuleOnTargetTask, self)._start()
        self._target_task.start()

    def _stop(self):
        self._target_task.stop()
        super(ActivateModuleOnTargetTask, self)._stop()
