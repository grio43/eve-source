#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\neocomGroupNamePopup.py
import localization
import utillib
from carbonui import ButtonVariant, uiconst
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.button.group import ButtonGroup
from carbonui.control.window import Window

class NeocomGroupNamePopup(Window):
    default_windowID = 'NeocomGroupNamePopup'
    default_fixedWidth = 320
    default_fixedHeight = 230
    default_caption = 'UI/Neocom/NeocomGroup'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.btnData = attributes.get('btnData', None)
        groupName = attributes.get('groupName', '')
        groupAbbrev = attributes.get('groupAbbrev', '')
        self.labelEdit = SingleLineEditText(name='labelEdit', label=localization.GetByLabel('UI/Neocom/NeocomGroupName'), parent=self.content, align=uiconst.TOTOP, padTop=20, setvalue=groupName, OnReturn=self.Confirm)
        self.labelEdit.SetMaxLength(30)
        self.labelAbbrevEdit = SingleLineEditText(name='labelAbbrevEdit', label=localization.GetByLabel('UI/Neocom/NeocomGroupNameAbbrev'), parent=self.content, align=uiconst.TOTOP, padTop=20, setvalue=groupAbbrev, OnReturn=self.Confirm)
        self.labelAbbrevEdit.SetMaxLength(2)
        button_group = ButtonGroup(parent=self.content)
        button_group.AddButton(label=localization.GetByLabel('UI/Common/Confirm'), func=self.Confirm, variant=ButtonVariant.PRIMARY)
        button_group.AddButton(label=localization.GetByLabel('UI/Commands/Cancel'), func=self.Close, args=())

    def Confirm(self, *args):
        kv = utillib.KeyVal(label=self.labelEdit.GetValue(), labelAbbrev=self.labelAbbrevEdit.GetValue())
        self.SetModalResult(kv)
