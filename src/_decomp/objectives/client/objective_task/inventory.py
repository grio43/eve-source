#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\client\objective_task\inventory.py
import evetypes
import eveformat
import threadutils
import eveicon
from objectives.client.ui.objective_task_widget import ProgressBarTaskWidget
from objectives.client.objective_task.base import ObjectiveTask, ObjectiveTaskGroup

class ItemInInventoryTask(ObjectiveTask):
    objective_task_content_id = None
    WIDGET = ProgressBarTaskWidget
    __notifyevents__ = ['OnMultipleItemChange', 'OnSessionChanged']
    USE_TYPE_ICON = True

    def __init__(self, item = None, location_id = None, **kwargs):
        super(ItemInInventoryTask, self).__init__(**kwargs)
        self._item = None
        self.item = item
        self._location_id = location_id
        self._current_quantity = 0

    def get_values(self):
        result = super(ItemInInventoryTask, self).get_values()
        result['current_quantity'] = self._current_quantity
        result['progress'] = self.progress
        return result

    @property
    def item(self):
        return self._item

    @item.setter
    def item(self, value):
        if self._item == value:
            return
        self._item = value
        self._title = evetypes.GetName(self.type_id)
        self.update()

    @property
    def location_id(self):
        return self._location_id

    @location_id.setter
    def location_id(self, value):
        if self.location_id == value:
            return
        self.location_id = value
        self.update()

    def _update(self):
        self._check_inventory()

    def OnMultipleItemChange(self, items, change):
        for item in items:
            if item.typeID == self.type_id:
                self._check_inventory()
                return

    def OnSessionChanged(self, is_remote, session, change):
        if 'shipid' in change or 'locationid' in change:
            self._check_inventory()

    @property
    def item_id(self):
        return self.item.get('item_id', None)

    @property
    def type_id(self):
        return self.item.get('type_id', None)

    @property
    def quantity(self):
        return self.item.get('quantity', 1)

    @threadutils.threaded
    def _check_inventory(self):
        result = self._quantity_function(type_id=self.type_id, location_id=self.location_id).get_values()
        if result:
            value = max(min(result['quantity'], self.quantity), 0)
        else:
            value = 0
        if self._current_quantity == value:
            return
        self._current_quantity = value
        self.on_update(objective_task=self)
        self.completed = self._current_quantity >= self.quantity

    @property
    def _quantity_function(self):
        from nodegraph.client.getters.inventory import GetItemQuantity
        return GetItemQuantity

    @property
    def value(self):
        return u'{}/{}'.format(eveformat.number(self._current_quantity, 0), eveformat.number(self.quantity, 0))

    @property
    def progress(self):
        return min(self._current_quantity / float(self.quantity), 1.0)

    def get_context_menu(self):
        return sm.GetService('menu').GetMenuFromItemIDTypeID(itemID=self.item_id, typeID=self.type_id, includeMarketDetails=True)


class ItemInInventoryTaskGroup(ObjectiveTaskGroup):
    objective_task_content_id = 4
    TASK = ItemInInventoryTask

    def __init__(self, items = None, location_id = None, **kwargs):
        super(ItemInInventoryTaskGroup, self).__init__(**kwargs)
        self._location_id = location_id
        self._update_items(items)

    def update_value(self, key, value):
        if key == 'items':
            self._update_items(value)
        elif key == 'location_id':
            self._update_location(value)

    def _update_items(self, items):
        self.clear_tasks()
        if items is None:
            items = []
        elif not isinstance(items, list):
            items = [items]
        for item in items:
            task_id = item.get('item_id') or item.get('type_id') or item.get('group_id')
            self.add_task(task_id=task_id, item=item, location_id=self._location_id)

        self.all_tasks_added()

    def _update_location(self, location_id):
        self._location_id = location_id
        for task in self.tasks:
            task.update_value('location_id', location_id)


class ItemInShipCargoTask(ItemInInventoryTask):

    @property
    def _quantity_function(self):
        from nodegraph.client.getters.inventory import GetItemQuantityInShipCargo
        return GetItemQuantityInShipCargo


class ItemInShipCargoTaskGroup(ItemInInventoryTaskGroup):
    objective_task_content_id = 2
    TASK = ItemInShipCargoTask


class ItemInHangarTask(ItemInInventoryTask):

    @property
    def _quantity_function(self):
        from nodegraph.client.getters.inventory import GetItemQuantityInHangar
        return GetItemQuantityInHangar


class ItemInHangarTaskGroup(ItemInInventoryTaskGroup):
    objective_task_content_id = 3
    TASK = ItemInHangarTask
