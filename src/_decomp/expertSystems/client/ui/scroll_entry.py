#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\expertSystems\client\ui\scroll_entry.py
from carbonui import uiconst, Density
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control import itemIcon
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.item import Item
from expertSystems.client.ui.store_button import ViewExpertSystemInStoreButton
from expertSystems.client.util import expert_system_benefits_player

class ExpertSystemEntry(Item):

    def Startup(self, *args):
        Generic.Startup(self, args)
        labelCont = Container(name='labelCont', parent=self, padRight=8)
        self.sr.label.SetParent(labelCont)
        self.sr.label.left = 8
        self.sr.label.autoFadeSides = 16
        self.sr.icon = itemIcon.ItemIcon(parent=self, state=uiconst.UI_DISABLED, pos=(1, 2, 24, 24), align=uiconst.TOPLEFT, idx=0)
        for eventName in ('OnClick', 'OnMouseDown', 'OnMouseUp', 'OnDblClick', 'OnMouseHover'):
            setattr(self.sr, eventName, None)

    def Load(self, node):
        self.sr.node = node
        self.itemID = node.itemID
        self.typeID = node.typeID
        self.confirmOnDblClick = node.Get('confirmOnDblClick', 0)
        self.showTooltip = node.Get('showTooltip', True)
        benefitsPlayer = expert_system_benefits_player(self.typeID)
        if benefitsPlayer:
            ViewExpertSystemInStoreButton(parent=ContainerAutoSize(parent=self, align=uiconst.TORIGHT, left=4, idx=0), align=uiconst.CENTER, expert_system_type_id=self.typeID, density=Density.COMPACT)
        self.sr.icon.SetTypeIDandItemID(self.typeID, self.itemID)
        self.sr.icon.opacity = 1.0 if benefitsPlayer else 0.5
        self.sr.label.left = self.height + 4
        self.sr.label.text = node.label
