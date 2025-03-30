#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\buttons\buttonInventory.py
import uthread
import uthread2
from carbonui import const as uiconst
from carbonui.uicore import uicore
from eve.client.script.ui.shared.neocom.neocom import neocomConst
from eve.client.script.ui.shared.neocom.neocom.buttons.buttonWindow import ButtonWindow
from eve.client.script.ui.shared.neocom.neocom.neocomUtil import IsBlinkingEnabled

class ButtonInventory(ButtonWindow):
    default_name = 'ButtonInventory'

    def OnDragEnter(self, panelEntry, nodes):
        if not self._IsValidDropData(nodes):
            return
        self.dropFrame.state = uiconst.UI_DISABLED
        self.OnMouseEnter()

    def OnDragExit(self, *args):
        self.dropFrame.state = uiconst.UI_HIDDEN
        self.OnMouseExit()

    def OnDropData(self, source, nodes):
        if not self._IsValidDropData(nodes):
            return
        items = []
        locationID = None
        for node in nodes:
            if node.Get('__guid__', None) in ('xtriui.InvItem', 'listentry.InvItem'):
                items.append(node.itemID)
                locationID = node.rec.locationID
                break

        if locationID and items:
            if session.stationid or session.structureid:
                invLocationID = const.containerHangar
                invFlagID = const.flagHangar
                inventory = sm.GetService('invCache').GetInventoryFromId(invLocationID)
                inventory.MultiAdd(items, locationID, flag=invFlagID)
        self.dropFrame.state = uiconst.UI_HIDDEN

    def _IsValidDropData(self, nodes):
        if not nodes:
            return False
        for node in nodes:
            if node.Get('__guid__', None) in ('xtriui.InvItem', 'listentry.InvItem'):
                return True

        return False

    def StopBlinkThread(self, numBlinks):
        uthread2.Sleep(numBlinks * neocomConst.BLINK_INTERVAL)
        self.btnData.SetBlinkingOff()
