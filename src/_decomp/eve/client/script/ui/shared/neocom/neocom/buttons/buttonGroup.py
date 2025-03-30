#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\buttons\buttonGroup.py
import uthread
from carbonui import const as uiconst
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.themeColored import LabelThemeColored
from eve.client.script.ui.shared.neocom.neocom.buttons.baseNeocomButton import BaseNeocomButton

class ButtonGroup(BaseNeocomButton):
    default_name = 'ButtonGroup'

    def ApplyAttributes(self, attributes):
        BaseNeocomButton.ApplyAttributes(self, attributes)
        self.btnData.on_name_changed.connect(self.OnNameChanged)
        if self.btnData.labelAbbrev:
            self.label = EveLabelMedium(parent=self, align=uiconst.CENTERBOTTOM, text=self.btnData.labelAbbrev, color=eveColor.SILVER_GREY, top=6, idx=0)

    def OnNameChanged(self):
        self.label.text = self.btnData.labelAbbrev

    def LoadTooltipPanel(self, tooltipPanel, *args):
        isOpen = self._openNeocomPanel and not self._openNeocomPanel.destroyed
        if isOpen:
            return
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.AddLabelMedium(text=self.btnData.label)

    def OnClickCommand(self):
        self.ToggleNeocomPanel()

    def OnDragEnter(self, source, dropData):
        if not sm.GetService('neocom').IsValidDropData(dropData):
            return
        self.dropFrame.state = uiconst.UI_DISABLED
        self.OnMouseEnter()
        uthread.new(self.ShowPanelOnMouseHoverThread)

    def OnDragExit(self, *args):
        self.dropFrame.state = uiconst.UI_HIDDEN
        self.OnMouseExit()

    def OnDropData(self, source, dropData):
        if not sm.GetService('neocom').IsValidDropData(dropData):
            return
        btnData = dropData[0]
        oldRootNode = btnData.GetRootNode()
        btnData.MoveTo(self.btnData)
        if oldRootNode == sm.GetService('neocom').GetEveMenuBtnDataRoot():
            btnData.isRemovable = True
