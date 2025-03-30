#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\expertSystems\client\ui\character_sheet\browse\entry.py
import eveui
import localization
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.sys.serviceManager import ServiceManager
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.eveWindowUnderlay import ListEntryUnderlay
from eve.client.script.ui.control.itemIcon import ItemIcon
from expertSystems.client.const import Color
from expertSystems.client.ui.vertical_centered_container import VerticalCenteredContainer

class ExpertSystemEntry(ContainerAutoSize):
    isDragObject = True
    ICON_SIZE = 48

    def __init__(self, expert_system, page_controller, **kwargs):
        self.expert_system = expert_system
        self.page_controller = page_controller
        self.selected_indicator = None
        super(ExpertSystemEntry, self).__init__(state=uiconst.UI_NORMAL, alignMode=uiconst.TOTOP, minHeight=self.ICON_SIZE, **kwargs)
        self.layout()
        self.update()
        self.page_controller.on_selected_expert_system_changed.connect(self._handle_selected_expert_system_changed)

    @property
    def is_selected(self):
        return self.page_controller.selected_expert_system is not None and self.page_controller.selected_expert_system.type_id == self.expert_system.type_id

    def layout(self):
        main_container = ContainerAutoSize(parent=self, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padding=8)
        ExpertSystemIcon(parent=Container(parent=main_container, align=uiconst.TOLEFT, width=self.ICON_SIZE), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, expert_system=self.expert_system, width=self.ICON_SIZE, height=self.ICON_SIZE)
        label_container = VerticalCenteredContainer(parent=main_container, align=uiconst.TOTOP, minHeight=self.ICON_SIZE, padLeft=8)
        eveLabel.EveLabelLargeBold(parent=label_container, align=uiconst.TOTOP, text=self.expert_system.name)
        if self.expert_system.associated_type_ids:
            eveLabel.EveLabelSmall(parent=label_container, align=uiconst.TOTOP, text=localization.GetByLabel('UI/ExpertSystem/ShipUnlockHint', ship_count=len(self.expert_system.associated_type_ids)), color=Color.text_secondary)
        self.selected_indicator = ListEntryUnderlay(bgParent=self)

    def update(self):
        if self.is_selected:
            self.selected_indicator.Select()
        else:
            self.selected_indicator.Deselect()

    def _handle_selected_expert_system_changed(self):
        self.update()

    def OnClick(self, *args):
        self.page_controller.selected_expert_system = self.expert_system

    def OnMouseEnter(self, *args):
        self.selected_indicator.hovered = True
        PlaySound(uiconst.SOUND_ENTRY_HOVER)

    def OnMouseExit(self, *args):
        self.selected_indicator.hovered = False

    def GetDragData(self):
        return [eveui.dragdata.ItemType(type_id=self.expert_system.type_id)]

    def GetMenu(self):
        return ServiceManager.Instance().GetService('menu').GetMenuFromItemIDTypeID(itemID=None, typeID=self.expert_system.type_id)


class ExpertSystemIcon(ItemIcon):
    default_showOmegaOverlay = False

    def __init__(self, expert_system, **kwargs):
        self._expert_system = expert_system
        super(ExpertSystemIcon, self).__init__(typeID=expert_system.type_id, **kwargs)
