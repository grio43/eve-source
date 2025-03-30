#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\checkboxWithInputFieldEntry.py
import localization
from carbonui import const as uiconst
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.entries.checkbox import CheckboxEntry
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
MIN_INPUT_HEIGHT = 26

class CheckBoxWithInputField(CheckboxEntry):

    def Startup(self, *args):
        CheckboxEntry.Startup(self, args)
        self.moreInfoIcon = MoreInfoIcon(left=2, top=-1, parent=self, idx=0, align=uiconst.CENTERRIGHT)
        unitLeft = self.moreInfoIcon.left + self.moreInfoIcon.width + 2
        self.unitLabel = eveLabel.EveLabelSmall(text=localization.GetByLabel('UI/Shared/TypeSearchString'), parent=self, align=uiconst.CENTERRIGHT, left=unitLeft)
        self.inpt = SingleLineEditInteger(name='amount', parent=self, align=uiconst.CENTERRIGHT, maxLength=32, idx=0, top=0, OnChange=self.OnAmountChanged)

    def Load(self, node):
        CheckboxEntry.Load(self, node)
        self.unitLabel.text = node.unitString
        self.inpt.left = self.unitLabel.textwidth + 2 + self.unitLabel.left
        self.inpt.SetValue(node.currentValue, docallback=False)
        self.moreInfoIcon.LoadTooltipPanel = node.moreTooltip
        self._ChangeUiOpacity(node.checked)

    def _ChangeUiOpacity(self, isChecked):
        if not isChecked:
            self.inpt.opacity = 0.5
            self.unitLabel.opacity = 0.5
        else:
            self.inpt.opacity = 1.0
            self.unitLabel.opacity = 1.0

    def GetHeight(self, *args):
        node, width = args
        h = CheckboxEntry.GetHeight(self, *args)
        node.height = max(h, MIN_INPUT_HEIGHT)
        return node.height

    def OnAmountChanged(self, *args):
        node = self.sr.node
        currentValue = self.inpt.GetValue()
        node.currentValue = currentValue
        node.OnChange(self.inpt)

    def CheckBoxChange(self, *args):
        CheckboxEntry.CheckBoxChange(self, *args)
        self._ChangeUiOpacity(self.sr.node.checked)
