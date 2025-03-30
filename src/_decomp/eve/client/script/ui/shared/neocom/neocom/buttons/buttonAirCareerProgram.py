#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\buttons\buttonAirCareerProgram.py
from carbonui.uicore import uicore
from eve.client.script.ui.shared.neocom.neocom.buttons.buttonWindow import ButtonWindow

class ButtonAIRCareerProgram(ButtonWindow):

    def OnClickCommand(self):
        uicore.cmd.GetCommandAndExecute(self.btnData.cmdName)
