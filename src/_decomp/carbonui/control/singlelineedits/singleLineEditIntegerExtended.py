#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\singlelineedits\singleLineEditIntegerExtended.py
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from eve.client.script.ui.tooltips.tooltipUtil import RefreshTooltipForOwner
from carbonui.control.buttonIcon import ButtonIcon
from uthread2 import start_tasklet

class SingleLineEditIntegerExtended(SingleLineEditInteger):
    defaultIncrease = 1
    typeID = None

    def OnTextChange(self, docallback = True):
        self.CheckHintText()
        self.RefreshCaretPosition()
        self.RefreshTextClipper()
        if docallback and self.OnChange:
            self.OnChange(self.GetText(), self.typeID)
        RefreshTooltipForOwner(self)

    def ApplyAttributes(self, attributes):
        super(SingleLineEditIntegerExtended, self).ApplyAttributes(attributes)
        self.defaultIncrease = attributes.get('increaseAmount')
        self.typeID = attributes.get('typeID')

    def OnMouseWheel(self, *args):
        indicator = args[0]
        if indicator > 0:
            self.ChangeNumericValue(self.defaultIncrease)
        else:
            self.ChangeNumericValue(-self.defaultIncrease)

    def OnNumericUpButtonMouseDown(self, *args):
        ButtonIcon.OnMouseDown(self.upButton, *args)
        self.updateNumericInputThread = start_tasklet(self.UpdateNumericInputThread, self.defaultIncrease)

    def OnNumericDownButtonMouseDown(self, *args):
        ButtonIcon.OnMouseDown(self.downButton, *args)
        self.updateNumericInputThread = start_tasklet(self.UpdateNumericInputThread, -self.defaultIncrease)
