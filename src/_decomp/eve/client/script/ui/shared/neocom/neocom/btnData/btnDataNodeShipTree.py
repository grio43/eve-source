#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\btnData\btnDataNodeShipTree.py
from eve.client.script.ui.shared.neocom.neocom.btnData.btnDataNode import BtnDataNode
import shipprogression.shipUnlockSignals as shipUnlockSignals
from shipprogression.shipUnlockSvc import GetShipUnlockService

class BtnDataNodeShipTree(BtnDataNode):

    def __init__(self, parent = None, children = None, iconPath = None, label = None, btnID = None, btnType = None, isRemovable = True, isDraggable = True, isOpen = False, isBlinking = False, labelAbbrev = None, wndCls = None, cmdName = None, **kw):
        BtnDataNode.__init__(self, parent, children, iconPath, label, btnID, btnType, isRemovable, isDraggable, isOpen, isBlinking, labelAbbrev, wndCls, cmdName, **kw)
        shipUnlockSignals.on_group_unlocked.connect(self.on_ship_unlock_groups_changed)
        shipUnlockSignals.on_group_unlock_viewed.connect(self.on_ship_unlock_viewed)
        shipUnlockSignals.on_unlocks_dismissed.connect(self.OnBadgeCountChanged)

    def on_ship_unlock_groups_changed(self, shipUnlockEntry):
        self.OnBadgeCountChanged()

    def on_ship_unlock_viewed(self, shipUnlockEntry):
        if self.GetItemCount() == 0:
            self.OnBadgeCountChanged()

    def GetItemCount(self):
        service = GetShipUnlockService()
        if service:
            return len(service.GetUnseenEntries())
        return 0

    def _disconnect_signals(self):
        BtnDataNode._disconnect_signals(self)
        shipUnlockSignals.on_group_unlocked.disconnect(self.on_ship_unlock_groups_changed)
        shipUnlockSignals.on_group_unlock_viewed.disconnect(self.on_ship_unlock_viewed)
        shipUnlockSignals.on_unlocks_dismissed.disconnect(self.OnBadgeCountChanged)

    def GetMenu(self):
        return BtnDataNode.GetMenu(self)
