#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\forms\formWindow.py
from carbonui import uiconst, AxisAlignment
from carbonui.button.group import ButtonGroup
from carbonui.control.forms import formFields
from carbonui.control.window import Window
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uicore import uicore
from eve.client.script.ui.control.message import ShowQuickMessage

class FormWindow(Window):
    default_windowID = 'FormWindow'
    default_width = 400
    default_isMinimizable = False
    default_isStackable = False
    default_isCollapseable = False
    __notifyevents__ = ['OnEndChangeDevice', 'OnUIScalingChange']

    def ApplyAttributes(self, attributes):
        super(FormWindow, self).ApplyAttributes(attributes)
        self.form = attributes.form
        self.SetCaption(self.form.name)
        if self.form.icon:
            self.icon = self.form.icon
        self.scroll = ScrollContainer(parent=self.content, align=uiconst.TOALL)
        self.formCont = ContainerAutoSize(name='formCont', parent=self.scroll, align=uiconst.TOTOP, callback=self.OnFormContHeightChanged)
        self.ConstructLayout()
        self.ConnectSignals()

    def ConstructLayout(self):
        self.ConstructFields()
        self.ConstructButtons()

    def ConstructFields(self):
        formFields.ConstructFields(self.formCont, self.form)

    def ConstructButtons(self):
        self.button_group = ButtonGroup(parent=self.formCont, align=uiconst.TOTOP, padTop=16, button_alignment=AxisAlignment.END)
        for submit_action in self.form.actions:
            self.button_group.AddButton(submit_action.label, lambda button, s = submit_action: self._execute_submit_action(s, button), hint=submit_action.hint)

    def ConnectSignals(self):
        self.form.on_submitted.connect(self.OnSubmitActionExecuted)
        self.form.on_submit_failed.connect(self.OnSubmitActionFailed)
        self.form.on_canceled.connect(self.CloseByUser)

    def _execute_submit_action(self, submit_action, button):
        button.Disable()
        button.busy = True
        try:
            submit_action.execute(self.form)
        finally:
            button.busy = False
            button.Enable()

    def OnSubmitActionFailed(self, action):
        ShowQuickMessage(self.form.get_submit_failed_reasons_text())

    def OnSubmitActionExecuted(self, action):
        self.Close()

    def CloseByUser(self, *args):
        if self.form.cancel_dialog:
            if uicore.Message(self.form.cancel_dialog, buttons=uiconst.YESNO) != uiconst.ID_YES:
                return
        super(FormWindow, self).CloseByUser(*args)

    def OnFormContHeightChanged(self, *args):
        self.UpdateFixedHeight()

    def UpdateFixedHeight(self):
        max_height = uicore.desktop.height * 0.9
        _, height = self.GetWindowSizeForContentSize(height=self.formCont.height)
        self.SetFixedHeight(min(max_height, height))

    def Confirm(self, *args):
        button = self.button_group.buttons[0]
        self._execute_submit_action(button, self.form.actions[0])

    def OnEndChangeDevice(self, *args, **kwargs):
        self.UpdateFixedHeight()
        self.scroll.ScrollToVertical(0.0)

    def OnUIScalingChange(self, *args, **kwargs):
        self.UpdateFixedHeight()
        self.scroll.ScrollToVertical(0.0)
