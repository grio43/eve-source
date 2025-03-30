#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\buttons\buttonNotification.py
from carbonui.uicore import uicore
from eve.client.script.ui.shared.neocom.neocom.buttons.baseNeocomButton import BaseNeocomButton
from eve.client.script.ui.shared.neocom.neocom.neocomUtil import IsBlinkingEnabled

class ButtonNotification(BaseNeocomButton):

    def LoadTooltipPanel(self, panel, owner):
        panel.LoadGeneric1ColumnTemplate()
        panel.AddLabelMedium(text=self.btnData.label, wrapWidth=220)

    def OnClickCommand(self):
        uicore.cmd.GetCommandAndExecute(self.btnData.cmdName)
