#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\singlelineedits\singleLineEditPassword.py
from carbonui.control.singlelineedits.baseSingleLineEdit import BaseSingleLineEdit
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText

class SingleLineEditPassword(SingleLineEditText):
    default_name = 'SingleLineEditPassword'
    default_passwordCharacter = u'\u2022'

    def ApplyAttributes(self, attributes):
        self.SetPasswordChar(attributes.get('passwordCharacter', self.default_passwordCharacter))
        super(SingleLineEditPassword, self).ApplyAttributes(attributes)

    def SetPasswordChar(self, char):
        self.passwordchar = char

    def SetDisplayText(self, text):
        self.textLabel.SetText(self.passwordchar * len(text.replace('<br>', '')))

    def Copy(self, selectStart = None, selectEnd = None):
        return self.passwordchar * len(self.text)

    def RegisterHistory(self, value = None):
        pass

    def CheckHistory(self):
        pass

    def GetMenu(self):
        return BaseSingleLineEdit.GetMenu(self)
