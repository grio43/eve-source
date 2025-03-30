#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\client\objective_task\mining.py
import evetypes
from objectives.client.objective_task.target import TargetTask

class MiningCycleTask(TargetTask):
    objective_task_content_id = 21
    __notifyevents__ = ['OnMultipleItemChange']

    def __init__(self, asteroid_info = None, **kwargs):
        self._current_amount = None
        self._asteroid_info = None
        super(MiningCycleTask, self).__init__(**kwargs)
        self.asteroid_info = asteroid_info

    @property
    def asteroid_info(self):
        return self._asteroid_info

    @asteroid_info.setter
    def asteroid_info(self, value):
        if self._asteroid_info == value:
            return
        self._asteroid_info = value
        asteroid_group_id = None
        if self._asteroid_info:
            if 'group_id' in self._asteroid_info:
                asteroid_group_id = self._asteroid_info['group_id']
            elif 'type_id' in self._asteroid_info:
                asteroid_group_id = evetypes.GetGroupID(self._asteroid_info['type_id'])
        if asteroid_group_id:
            self.target = {'group_id': asteroid_group_id}
        else:
            self.target = None
        self._update_cached_amount()

    def OnMultipleItemChange(self, items, change):
        if self._current_amount is None:
            return
        for item in items:
            group_id = evetypes.GetGroupID(item.typeID)
            if group_id == self.group_id:
                amount = self._get_ore_amount()
                if amount > self._current_amount:
                    self.completed = True
                    self._unregister()
                else:
                    self._current_amount = amount
                break

    def _update_cached_amount(self):
        if self._current_amount is not None:
            return
        self._current_amount = self._get_ore_amount()

    def _get_ore_amount(self):
        if not self.group_id:
            return None
        from nodegraph.client.getters.inventory import GetItemQuantityInShipCargo
        return GetItemQuantityInShipCargo(group_id=self.group_id).get_values()['quantity']
