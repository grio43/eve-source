#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\forms\formContainer.py
from carbonui import uiconst
from carbonui.button.group import ButtonGroup
from carbonui.control.forms import formFields
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.message import ShowQuickMessage

class FormContainer(ContainerAutoSize):
    default_components = None
    default_align = uiconst.TOTOP

    def ApplyAttributes(self, attributes):
        super(FormContainer, self).ApplyAttributes(attributes)
        self.form = attributes.form
        self.ConstructFields()
        self.ConstructButtonGroup()
        self.form.on_submit_failed.connect(self.OnSubmitFailed)

    def ConstructFields(self):
        formFields.ConstructFields(self, self.form)

    def ConstructButtonGroup(self):
        buttonGroup = ButtonGroup(parent=self, align=uiconst.TOTOP, padTop=16)
        for submit_action in self.form.actions:
            buttonGroup.AddButton(submit_action.label, lambda button, s = submit_action: self._execute_submit_action(s, button))

    def _execute_submit_action(self, submit_action, button):
        button.Disable()
        button.busy = True
        try:
            submit_action.execute(self.form)
        finally:
            button.Enable()
            button.busy = False

    def OnSubmitFailed(self, action):
        ShowQuickMessage(self.form.get_submit_failed_reasons_text())
