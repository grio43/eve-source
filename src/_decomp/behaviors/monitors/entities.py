#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\monitors\entities.py
from ballpark.messenger.const import MESSAGE_ON_ADDITIONAL_LOOT_REMOVED, MESSAGE_ON_INVENTORY_CHANGE
from behaviors.tasks import MonitorTask

class AdditionalInventoryRemovalMonitor(MonitorTask):

    def _get_message(self):
        return MESSAGE_ON_ADDITIONAL_LOOT_REMOVED


class InventoryChangeMonitor(MonitorTask):

    def _get_message(self):
        return MESSAGE_ON_INVENTORY_CHANGE
