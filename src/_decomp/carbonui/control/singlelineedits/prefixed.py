#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\singlelineedits\prefixed.py
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText

class PrefixedSingleLineEdit(SingleLineEditText):

    def ApplyAttributes(self, attributes):
        self.prefix = attributes.prefix or ''
        setvalue = attributes.setvalue or ''
        if not setvalue:
            setvalue = self.prefix
        elif setvalue and not setvalue.startswith(self.prefix):
            setvalue = self.prefix + setvalue
        attributes.setvalue = setvalue
        super(PrefixedSingleLineEdit, self).ApplyAttributes(attributes)
        self._OnChange = self.OnChange
        self.OnChange = self.OnNameEditEdited
        self.SetHistoryVisibility(False)
        self.RefreshCaretPosition()

    def UpdatePrefix(self, newPrefix):
        oldPrefix = self.prefix
        currentText = self.GetValue()
        self.prefix = newPrefix
        newText = currentText.replace(oldPrefix, newPrefix, 1)
        self.SetValue(newText)

    def OnNameEditEdited(self, *args):
        args2 = list(args)
        newText = args[0]
        caretpos = self.caretIndex[0]
        if caretpos < len(self.prefix):
            text = self.prefix
            if len(newText) > caretpos:
                text += newText[caretpos:].lstrip()
            newText = text
            self.SetText(newText)
            self.caretIndex = self.GetCursorFromIndex(len(self.prefix))
            self.RefreshCaretPosition()
            args2[0] = newText
        if self._OnChange:
            self._OnChange(*args2)

    def GetSelectionBounds(self):
        selFrom, selTo = super(PrefixedSingleLineEdit, self).GetSelectionBounds()
        if selFrom and selFrom[0] < len(self.prefix):
            newFrom = len(self.prefix)
            selFrom = (newFrom, self.textLabel.GetWidthToIndex(newFrom)[1])
            newTo = max(newFrom, selTo[0])
            selTo = (newTo, self.textLabel.GetWidthToIndex(newTo)[1])
        if getattr(self, 'prefix', None) and self.caretIndex[0] < len(self.prefix):
            self.caretIndex = self.GetCursorFromIndex(len(self.prefix))
            self.RefreshCaretPosition()
        return (selFrom, selTo)
