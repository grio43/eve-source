#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\buttons\clockButton.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst
from carbonui.primitives.fill import Fill
from carbonui.uicore import uicore
from eve.client.script.ui.shared.neocom.neocom.buttons.wrapperButton import WrapperButton
import blue
from gametime.ingameclock import InGameClock
from localization.formatters import FormatDateTime

class ClockButton(WrapperButton):
    cmdName = 'OpenCalendar'

    def ApplyAttributes(self, attributes):
        super(ClockButton, self).ApplyAttributes(attributes)
        clock = InGameClock(parent=self, align=uiconst.TOALL, label_font_size=11)
        clock.update_clock()
        Fill(bgParent=self, color=(0, 0, 0, 0.4))

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric3ColumnTemplate()
        cmd = uicore.cmd.commandMap.GetCommandByName(self.cmdName)
        tooltipPanel.AddCommandTooltip(cmd)
        timeLabel = FormatDateTime(blue.os.GetTime(), dateFormat='full', timeFormate=None)
        tooltipPanel.AddLabelMedium(text=timeLabel, colSpan=tooltipPanel.columns)

    def OnClick(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        cmd = uicore.cmd.commandMap.GetCommandByName(self.cmdName)
        cmd.callback()
        self.SetBlinkingOff()
