#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\client\objective_task\container.py
from hackingcommon.hackingConstants import hackingStateHacked
from nodegraph.client.conditions.window import InventoryOpen
from objectives.client.objective_task.target import TargetTask, TargetsTask, BaseTargetsTask

class OpenLootContainerTask(TargetTask):
    objective_task_content_id = 16
    __notifyevents__ = ['OnInventoryContainerShown', 'OnInventoryClosed']

    def __init__(self, *args, **kwargs):
        self._inventory = None
        super(OpenLootContainerTask, self).__init__(*args, **kwargs)

    def OnInventoryContainerShown(self, inventory_container, previous_inventory_container):
        if self.item_id and self.item_id == inventory_container[1]:
            self._inventory = inventory_container
        self.completed = self._check_inventory()

    def OnInventoryClosed(self, inventory_container):
        self.completed = self._check_inventory()

    def _check_inventory(self):
        if self._inventory:
            return InventoryOpen(inventory_container=self._inventory[0], window_instance_id=self._inventory[1]).validate()
        return False


class HackContainerTask(TargetTask):
    objective_task_content_id = 18
    __notifyevents__ = ['OnSlimItemChange']

    def __init__(self, personal_only = None, **kwargs):
        self._personal_only = True if personal_only is None else personal_only
        super(HackContainerTask, self).__init__(**kwargs)

    def OnSlimItemChange(self, old_slim_item, new_slim_item):
        if new_slim_item.itemID != self.item_id:
            return
        self._check_completed(new_slim_item)

    def _slim_item_initialized(self):
        self._check_completed(self._slim_item)

    def _check_completed(self, slim_item):
        if not slim_item:
            return
        hacking_state = getattr(slim_item, 'hackingSecurityState')
        owner_id = getattr(slim_item, 'ownerID')
        self.completed = hacking_state == hackingStateHacked and (not self._personal_only or owner_id == session.charid)


class HackContainersTask(TargetsTask):
    objective_task_content_id = 54
    TASK = HackContainerTask
    __notifyevents__ = TargetsTask.__notifyevents__ + ['OnObjectExplode']

    def __init__(self, personal_only = None, **kwargs):
        self._personal_only = personal_only
        super(HackContainersTask, self).__init__(**kwargs)

    def add_task(self, *args, **kwargs):
        super(HackContainersTask, self).add_task(personal_only=self._personal_only, *args, **kwargs)

    def OnObjectExplode(self, type_id, item_id):
        self.remove_task(item_id)


class HackAllContainersTask(BaseTargetsTask):
    objective_task_content_id = 55
    TASK = HackContainerTask
    __notifyevents__ = BaseTargetsTask.__notifyevents__ + ['OnObjectExplode']

    def __init__(self, personal_only = None, **kwargs):
        self._personal_only = personal_only
        super(HackAllContainersTask, self).__init__(**kwargs)

    def add_task(self, *args, **kwargs):
        super(HackAllContainersTask, self).add_task(personal_only=self._personal_only, *args, **kwargs)

    def OnObjectExplode(self, type_id, item_id):
        self.remove_task(item_id)

    def _validate_target(self, slim_item):
        return getattr(slim_item, 'hackingSecurityState') is not None


class SalvageWreckTask(TargetTask):
    objective_task_content_id = 17
    __notifyevents__ = ['OnEveMessage']
    _salvage_success_messages = ['SalvagingSuccess',
     'SalvagingSuccessHollow',
     'LockedContainerOpened',
     'LockedContainerOpenedAlready']

    def OnEveMessage(self, message_key, message_values):
        if message_values and message_values.get('itemID') == self.item_id and message_key in self._salvage_success_messages:
            self.completed = True
