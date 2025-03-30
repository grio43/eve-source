#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\buttonEvent.py
import localization
from carbonui import const as uiconst
from carbonui.uicore import uicore
from eve.client.script.ui.shared.neocom.neocom.buttons.baseNeocomButton import BaseNeocomButton

class ButtonEvent(BaseNeocomButton):

    def LoadTooltipPanel(self, tooltipPanel, owner):
        tooltipPanel.LoadGeneric3ColumnTemplate()
        description = localization.GetByLabel(self.btnData.descriptionPath)
        tooltipPanel.AddLabelShortcut(self.btnData.label, None)
        tooltipPanel.AddLabelMedium(text=description, align=uiconst.TOPLEFT, wrapWidth=200, colSpan=tooltipPanel.columns, color=(0.6, 0.6, 0.6, 1))

    def OnClickCommand(self):
        uicore.cmd.GetCommandAndExecute(self.btnData.cmdName)
