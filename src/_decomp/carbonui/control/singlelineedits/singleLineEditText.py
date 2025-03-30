#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\singlelineedits\singleLineEditText.py
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from menu import MenuLabel
from carbonui.control.singlelineedits.baseSingleLineEdit import BaseSingleLineEdit
import carbonui.const as uiconst

class SingleLineEditText(BaseSingleLineEdit):
    default_name = 'SingleLineEditText'
    default_maxLength = None
    default_showLetterCounter = False

    def ApplyAttributes(self, attributes):
        self.maxletters = None
        self.charCounterLabel = None
        self.showLetterCounter = attributes.get('showLetterCounter', self.default_showLetterCounter)
        self.SetMaxLength(attributes.get('maxLength', self.default_maxLength))
        super(SingleLineEditText, self).ApplyAttributes(attributes)

    def SetValue(self, text, docallback = 1):
        isString = isinstance(text, basestring)
        if not isString:
            return
        text = text.replace('&lt;', '<').replace('&gt;', '>')
        if self.maxletters:
            text = text[:self.maxletters]
        super(SingleLineEditText, self).SetValue(text, docallback)

    def SetText(self, text):
        super(SingleLineEditText, self).SetText(text)
        self.UpdateLetterCounter()

    def GetValue(self, registerHistory = True, raw = 0):
        if registerHistory:
            self.RegisterHistory()
        if not raw:
            return self.text.replace('<', '&lt;').replace('>', '&gt;')
        else:
            return self.text

    def SetMaxLength(self, maxLength):
        self.maxletters = maxLength

    def _ValidateInsert(self, insert):
        if self.maxletters and len(insert) > self.maxletters:
            return insert[:self.maxletters]
        return insert

    def GetMenu(self):
        m = super(SingleLineEditText, self).GetMenu()
        if self.displayHistory:
            m += [(MenuLabel('/Carbon/UI/Controls/Common/ClearHistory'), self.ClearHistory, (None,))]
        return m

    def ConstructLetterCounter(self):
        if self.charCounterLabel is None or self.charCounterLabel.destroyed:
            self.charCounterLabel = EveLabelSmall(parent=self, name='charCounterLabel', align=uiconst.TOPRIGHT, text=' ', maxLines=1, left=2)
            self.charCounterLabel.top = -self.charCounterLabel.textheight - 3

    def OnTextChange(self, docallback = True):
        super(SingleLineEditText, self).OnTextChange(docallback)
        self.UpdateLetterCounter()

    def UpdateLetterCounter(self):
        if self.showLetterCounter and self.maxletters:
            self.ConstructLetterCounter()
            self.charCounterLabel.text = '%s/%s' % (len(self.text), self.maxletters)
            self.charCounterLabel.display = True
        elif self.charCounterLabel:
            self.charCounterLabel.display = False
