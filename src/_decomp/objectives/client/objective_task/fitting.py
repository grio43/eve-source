#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\client\objective_task\fitting.py
from carbonui.uicore import uicore
import localization
import evetypes
from eve.common.script.sys.eveCfg import IsDocked
from eve.client.script.ui.shared.inventory.invWindow import Inventory
from inventorycommon.const import INVENTORY_ID_STATION_SHIPS
from nodegraph.client.getters.module import GetFittedModules, GetFittedModule
from nodegraph.client.events.module import ModuleFitted, ModuleUnfitted
from nodegraph.client.conditions.fitting import ItemFitted
from objectives.client.objective_task.base import ObjectiveTask, ObjectiveTaskGroup
from objectives.client.ui.objective_task_widget import ObjectiveTaskWidget

class FitModuleTask(ObjectiveTask):
    objective_task_content_id = None
    WIDGET = ObjectiveTaskWidget
    USE_TYPE_ICON = True

    def __init__(self, module = None, **kwargs):
        super(FitModuleTask, self).__init__(**kwargs)
        self._condition = None
        self._module = None
        self.module = module

    @property
    def module(self):
        return self._module

    @module.setter
    def module(self, value):
        if self._module == value:
            return
        self._module = value
        self._get_module = GetFittedModule(**self._module)
        self._title = get_item_name(**self._module)
        self.update()

    @property
    def type_id(self):
        if self._module:
            return self._module.get('type_id', None)

    def double_click(self):
        if IsDocked():
            uicore.cmd.OpenFitting()

    def get_context_menu(self):
        type_id = self.type_id
        if type_id:
            return sm.GetService('menu').GetMenuFromItemIDTypeID(itemID=None, typeID=type_id, includeMarketDetails=True)
        else:
            return []

    def _update(self):
        fitted_module = self._get_module.get_values()
        self.completed = bool(fitted_module['item_id'])


class FitModulesTaskGroup(ObjectiveTaskGroup):
    objective_task_content_id = 13
    TASK = FitModuleTask
    __notifyevents__ = ['ProcessActiveShipChanged']

    def __init__(self, modules = None, **kwargs):
        super(FitModulesTaskGroup, self).__init__(**kwargs)
        self._update_modules(modules)
        from nodegraph.client.events.module import ModuleFittingChanged
        self._event = ModuleFittingChanged(callback=self._fitting_changed, keep_listening=True)

    def update_value(self, key, value):
        if key == 'modules':
            self._update_modules(value)
            self._on_task_state_changed()

    def _update_modules(self, modules):
        self.clear_tasks()
        if modules is None:
            modules = []
        elif not isinstance(modules, list):
            modules = [modules]
        for module in modules:
            task_id = module.get('item_id') or module.get('type_id') or module.get('group_id')
            self.add_task(task_id=task_id, module=module)

        self.all_tasks_added()

    def _register(self):
        super(FitModulesTaskGroup, self)._register()
        self._event.start()

    def _unregister(self):
        super(FitModulesTaskGroup, self)._unregister()
        self._event.stop()

    def _fitting_changed(self, **kwargs):
        self._update()

    def ProcessActiveShipChanged(self, *args, **kwargs):
        self.update()


class BoardShipTask(ObjectiveTask):
    objective_task_content_id = 10
    USE_TYPE_ICON = True
    __notifyevents__ = ['ProcessActiveShipChanged']

    def __init__(self, type_id = None, group_id = None, **kwargs):
        super(BoardShipTask, self).__init__(**kwargs)
        self._ship_info = {'type_id': type_id,
         'group_id': group_id}
        self._update_title()

    @property
    def type_id(self):
        return self._ship_info.get('type_id')

    @type_id.setter
    def type_id(self, value):
        if self._ship_info.get('type_id') == value:
            return
        self._ship_info['type_id'] = value
        self._update_title()
        self.update()

    @property
    def group_id(self):
        return self._ship_info.get('group_id')

    @group_id.setter
    def group_id(self, value):
        if self._ship_info.get('group_id') == value:
            return
        self._ship_info['group_id'] = value
        self._update_title()
        self.update()

    def ProcessActiveShipChanged(self, *args, **kwargs):
        self.update()

    def double_click(self):
        if IsDocked():
            Inventory.OpenOrShow(invID=(INVENTORY_ID_STATION_SHIPS, session.locationid))

    def get_context_menu(self):
        type_id = self.type_id
        if type_id:
            return sm.GetService('menu').GetMenuFromItemIDTypeID(itemID=None, typeID=type_id, includeMarketDetails=True)
        else:
            return []

    def _update_title(self):
        if self.type_id or self.group_id:
            self._title = get_item_name(**self._ship_info)
        else:
            self._title = localization.GetByLabel('UI/Objectives/Titles/BoardAny')

    def _update(self):
        from nodegraph.client.conditions.ship import InShip
        super(BoardShipTask, self)._update()
        self.completed = InShip(**self._ship_info).validate()


class FitAnyTask(ObjectiveTask):
    objective_task_content_id = None
    WIDGET = ObjectiveTaskWidget
    __notifyevents__ = ['ProcessActiveShipChanged']

    def __init__(self, *args, **kwargs):
        super(FitAnyTask, self).__init__(*args, **kwargs)
        self.fitted_event = ModuleFitted(callback=self._module_fitted, keep_listening=True)
        self.unfitted_event = ModuleUnfitted(callback=self._module_unfitted, keep_listening=True)

    def ProcessActiveShipChanged(self, *args, **kwargs):
        self._update()

    def _register(self):
        super(FitAnyTask, self)._register()
        self.fitted_event.start()
        self.unfitted_event.start()

    def _unregister(self):
        super(FitAnyTask, self)._unregister()
        self.fitted_event.stop()
        self.unfitted_event.stop()

    def _module_fitted(self, type_id = None, **kwargs):
        self._update(type_id)

    def _module_unfitted(self, **kwargs):
        self._update()

    def _update(self, type_id = None):
        pass

    def double_click(self):
        if IsDocked():
            uicore.cmd.OpenFitting()


class FitWeaponTask(FitAnyTask):
    objective_task_content_id = 25

    def __init__(self, *args, **kwargs):
        super(FitWeaponTask, self).__init__(*args, **kwargs)
        self._get_modules = GetFittedModules(only_weapons=True)

    def _update(self, type_id = None):
        if type_id:
            if evetypes.IsWeaponModule(type_id):
                self.completed = True
        else:
            self.completed = bool(self._get_modules.get_values()['fitted_modules'])


class FitMiningLaserTask(FitAnyTask):
    objective_task_content_id = 26

    def __init__(self, *args, **kwargs):
        super(FitMiningLaserTask, self).__init__(*args, **kwargs)
        self._get_modules = GetFittedModules(type_list_id=evetypes.TYPE_LIST_MINING_LASER_MODULES)

    def _update(self, type_id = None):
        if type_id:
            all_types = evetypes.GetTypeIDsByListID(evetypes.TYPE_LIST_MINING_LASER_MODULES)
            if type_id in all_types:
                self.completed = True
        else:
            modules = self._get_modules.get_values()['fitted_modules']
            self.completed = bool(modules)


def get_item_name(**kwargs):
    import evetypes
    type_id = kwargs.get('type_id', None)
    if type_id:
        return evetypes.GetName(type_id)
    group_id = kwargs.get('group_id', None)
    if group_id:
        return evetypes.GetGroupNameByGroup(group_id)
    category_id = kwargs.get('category_id', None)
    if category_id:
        return evetypes.GetCategoryNameByCategory(category_id)
    type_list_id = kwargs.get('type_list_id', None)
    if type_list_id:
        try:
            return evetypes.GetTypeListDisplayName(type_list_id)
        except:
            pass

    return ''
