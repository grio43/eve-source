#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\labelEditable.py
import carbonui.const as uiconst
from carbon.common.script.util.format import FmtAmt
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.fontconst import DEFAULT_FONTSIZE
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import Label
from carbonui.uicore import uicore

class LabelEditable(Container):
    default_height = 40
    default_width = 100
    default_maxWidth = None
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_PICKCHILDREN
    default_alwaysVisible = False
    EDIT_FIELD_PADDING = 34

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.defaultText = attributes.get('defaultText', None)
        self.currentText = attributes['text']
        hint = attributes.get('hint', None)
        self.configName = attributes['configName']
        self.maxLength = attributes.get('maxLength', None)
        self.minLength = attributes.get('minLength', None)
        self.maxWidth = attributes.get('maxWidth', self.default_maxWidth)
        fontsize = attributes.get('fontsize', DEFAULT_FONTSIZE)
        self.minValue = attributes.get('minValue', 0)
        self.maxValue = attributes.get('maxValue', None)
        onEditFieldChangedFunc = attributes.get('onEditFieldChanged', self.OnEditFieldChanged)
        self.textEditFieldSwitchCallback = attributes.get('textEditFieldSwitchCallback', None)
        self.alwaysVisible = attributes.get('alwaysVisible', self.default_alwaysVisible)
        singleLineEditClass = SingleLineEditInteger if self.minValue or self.maxValue else SingleLineEditText
        self.editField = singleLineEditClass(name='editField', parent=self, align=uiconst.CENTERLEFT, pos=(0, 0, 100, 0), setvalue=self.currentText, OnFocusLost=self.OnEditFieldLostFocus, OnChange=onEditFieldChangedFunc, OnReturn=self.OnEditFieldLostFocus, OnSetFocus=self.OnEditFieldSetFocus, maxLength=self.maxLength, fontsize=fontsize, minValue=self.minValue, maxValue=self.maxValue)
        self.ChangeEditFieldVisibility(active=False)
        self.editField._GetSizeForHistoryMenu = self._GetSizeForHistoryMenu
        self.textLabel = Label(name='textLabel', parent=self, left=SingleLineEditInteger.default_textLeftMargin + self.editField._textClipper.padLeft, state=uiconst.UI_NORMAL, maxLines=1, align=uiconst.CENTERLEFT, fontsize=self.editField.textLabel.fontsize, text=self.currentText, autoFadeSides=20)
        self.textLabel.SetRGBA(1.0, 1.0, 1.0, 1.0)
        self.textLabel.cursor = uiconst.UICURSOR_IBEAM
        self.editField.width = self.textLabel.textwidth + 20
        self.width = self.editField.width
        self.height = self.editField.height
        self.textLabel.OnClick = self.OnLabelClicked
        if hint:
            self.textLabel.hint = hint

    def OnLabelClicked(self, *args):
        self.SetAsActive()
        uicore.registry.SetFocus(self.editField)
        self.editField.caretIndex = self.editField.GetCursorFromIndex(-1)

    def ChangeEditFieldVisibility(self, active = False):
        if active:
            if self.alwaysVisible:
                self.editField.opacity = 1.0
            else:
                self.editField.display = True
        elif self.alwaysVisible:
            self.editField.opacity = 0.7
        else:
            self.editField.display = False

    def SetAsActive(self):
        self.textLabel.display = False
        self.ChangeEditFieldVisibility(active=True)
        self.ChangesCallback()

    def OnEditFieldSetFocus(self, *args):
        self.SetAsActive()

    def OnEditFieldLostFocus(self, *args):
        currentText = unicode(self.currentText)
        if self.minLength and len(currentText) < self.minLength and self.defaultText:
            currentText = self.defaultText
            self.SetValue(currentText)
        self.textLabel.display = True
        self.ChangeEditFieldVisibility(active=False)
        settings.user.ui.Set(self.configName, currentText)
        self.ChangesCallback()

    def OnEditFieldChanged(self, *args):
        self.currentText = self.editField.GetValue()
        self.SetTextLabelText()
        self.SetWidth()

    def SetWidth(self):
        width = self.editField.textLabel.textwidth
        if self.maxWidth:
            width = min(width, self.maxWidth)
        self.editField.width = width + self.EDIT_FIELD_PADDING
        self.width = self.editField.width

    def GetValue(self):
        return self.editField.GetValue()

    def SetValue(self, text):
        self.currentText = text
        self.SetTextLabelText()
        self.editField.SetText(text)
        self.OnEditFieldChanged()

    def SetTextLabelText(self):
        if self.minValue or self.maxValue:
            self.textLabel.text = FmtAmt(self.currentText)
            return
        self.textLabel.text = self.currentText

    def ChangesCallback(self):
        if self.textEditFieldSwitchCallback:
            self.textEditFieldSwitchCallback()

    def _GetSizeForHistoryMenu(self):
        l, t, w, h = self.editField.GetAbsolute()
        if self.maxWidth:
            w = max(w, self.maxWidth) + 4
        return (l,
         t,
         w,
         h)

    def SetMaxWidth(self, value):
        self.maxWidth = value - self.EDIT_FIELD_PADDING
        self.SetWidth()
