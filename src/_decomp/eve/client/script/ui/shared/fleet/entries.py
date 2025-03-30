#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fleet\entries.py
import eveformat
import localization
from carbonui import Density, uiconst
from carbonui.control.button import Button
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.itemIcon import ItemIcon
from eveservices.menu import GetMenuService

class FleetCompositionEntry(Generic):
    __guid__ = 'listentry.FleetCompositionEntry'
    isDragObject = True

    def GetDragData(self, *args):
        return self.sr.node.scroll.GetSelectedNodes(self.sr.node)


class FleetCompSummaryEntry(Generic):
    __guid__ = 'listentry.FleetCompSummaryEntry'

    def Startup(self, *args):
        Generic.Startup(self, args)
        self.sr.label.left = 40
        self.sr.icon = ItemIcon(parent=self, pos=(1, 2, 32, 32), align=uiconst.TOPLEFT, idx=0)

    def Load(self, node):
        self.sr.node = node
        self.typeID = node.typeID
        self.sr.icon.SetTypeIDandItemID(self.typeID, None)
        self.sr.label.text = node.label
        if node.Get('selected', 0):
            self.Select()
        else:
            self.Deselect()
        self.sr.label.Update()

    def GetHeight(self, *args):
        node, width = args
        node.height = 37
        return node.height


class JoinRequestField(Generic):
    __guid__ = 'listentry.JoinRequestField'
    __nonpersistvars__ = []

    def Startup(self, *args):
        super(JoinRequestField, self).Startup(*args)
        reject_text = localization.GetByLabel('UI/Fleet/RejectJoinRequest')
        reject_button = Button(parent=self, idx=0, align=uiconst.CENTERRIGHT, left=4, label=reject_text, func=self.RejectJoinRequest, density=Density.COMPACT)
        accept_text = localization.GetByLabel('UI/Fleet/AcceptJoinRequest')
        Button(parent=self, idx=0, align=uiconst.CENTERRIGHT, left=reject_button.left + reject_button.width + 8, label=accept_text, func=self.AcceptJoinRequest, density=Density.COMPACT)

    def GetHeight(self, *args):
        node, width = args
        node.height = 23
        return node.height

    def GetMenu(self, *args):
        menuSvc = GetMenuService()
        charID = self.sr.node.charID
        return menuSvc.CharacterMenu(charID)

    def AcceptJoinRequest(self, *args):
        charID = self.sr.node.charID
        sm.GetService('fleet').Invite(charID, None, None, None)

    def RejectJoinRequest(self, *args):
        charID = self.sr.node.charID
        sm.GetService('fleet').RejectJoinRequest(charID)
