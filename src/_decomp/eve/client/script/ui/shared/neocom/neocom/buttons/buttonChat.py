#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\buttons\buttonChat.py
import uthread
from carbonui import const as uiconst
from carbonui.uicore import uicore
from eve.client.script.ui.shared.neocom.neocom.buttons.baseNeocomButton import BaseNeocomButton

class ButtonChat(BaseNeocomButton):
    default_name = 'ButtonChat'

    def ApplyAttributes(self, attributes):
        BaseNeocomButton.ApplyAttributes(self, attributes)

    def OnClickCommand(self):
        uthread.new(self.ToggleNeocomPanel)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        isOpen = self._openNeocomPanel and not self._openNeocomPanel.destroyed
        if isOpen:
            return
        tooltipPanel.LoadGeneric3ColumnTemplate()
        cmd = uicore.cmd.commandMap.GetCommandByName('OpenChannels')
        tooltipPanel.AddCommandTooltip(cmd)
