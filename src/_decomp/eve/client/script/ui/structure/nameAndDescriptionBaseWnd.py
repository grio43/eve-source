#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\nameAndDescriptionBaseWnd.py
from carbonui import const as uiconst
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from carbonui.control.window import Window
from localization import GetByLabel
from carbonui.uicore import uicore

class NameAndDescBaseWnd(Window):
    default_name = 'nameAndDescBaseWnd'
    default_windowID = 'NameAndDescBaseWnd'
    default_width = 300
    default_height = 300
    confirmLabelPath = ''
    nameLabelPath = ''
    descriptionLabelPath = ''

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        self.btnGroup = ButtonGroup(parent=self.sr.main, idx=0)
        self.btnGroup.AddButton(GetByLabel(self.confirmLabelPath), self.OnConfirmClicked)
        self.btnGroup.AddButton(GetByLabel('UI/Commands/Cancel'), self.Cancel)
        self.groupNameField = SingleLineEditText(parent=self.sr.main, align=uiconst.TOTOP, label=GetByLabel(self.nameLabelPath), padding=4, top=10, maxLength=30)
        EveLabelSmall(name='titleHeader', parent=self.sr.main, text=GetByLabel(self.descriptionLabelPath), align=uiconst.TOTOP, top=6, padLeft=4)
        self.groupDescField = EditPlainText(parent=self.sr.main, padding=(4, 0, 4, 4), maxLength=200)
        self.PopulateFields()

    def PopulateFields(self):
        pass

    def OnConfirmClicked(self, *args):
        name = self.groupNameField.GetValue().strip()
        desc = self.groupDescField.GetValue().strip()
        if name:
            self.Confirm(name, desc)
            self.CloseByUser()
        else:
            uicore.Message('uiwarning03')

    def Confirm(self, name, desc):
        pass

    def Cancel(self, *args):
        self.CloseByUser()
