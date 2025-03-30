#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\dockedUI\controlButton.py
import weakref
import localization
from carbon.common.script.sys.serviceManager import ServiceManager
from carbonui.control.button import Button
from eve.client.script.ui import eveColor
from eve.client.script.ui.control import primaryButton
from eve.client.script.ui.shared.dockedUI.inControlCont import ConfirmTakeControl

class ControlButton(Button):

    def __init__(self, docked_ui_controller, **kwargs):
        self._controller = ControlButtonController(docked_ui_controller)
        self._docked_ui_controller = docked_ui_controller
        super(ControlButton, self).__init__(name='takeControlBtn', label=localization.GetByLabel('UI/Commands/TakeStructureControl'), func=self._execute, args=(), **kwargs)
        self._controller.connect(self)

    def Close(self):
        self._controller.close()
        super(ControlButton, self).Close()

    def LoadTooltipPanel(self, panel, owner):
        self._controller.load_tooltip_panel(panel, owner)

    def _execute(self):
        with self.busy_context:
            self._controller.execute()


class ControlButtonController(object):
    _button_ref = None

    def __init__(self, docked_ui_controller):
        self._docked_ui_controller = docked_ui_controller

    def connect(self, button):
        self._button_ref = weakref.ref(button)
        self._update_enabled(button)
        ServiceManager.Instance().RegisterForNotifyEvent(self, 'OnDockingProgressChanged')

    def close(self):
        ServiceManager.Instance().UnregisterForNotifyEvent(self, 'OnDockingProgressChanged')

    def execute(self):
        pilot_id = self._docked_ui_controller.GetStructurePilot(self._get_structure_id())
        if pilot_id is not None:
            if pilot_id != session.charid:
                confirm_override_control(self._docked_ui_controller)
        else:
            self._docked_ui_controller.TakeControl()

    def load_tooltip_panel(self, panel, owner):
        panel.LoadGeneric1ColumnTemplate()
        panel.AddLabelMedium(text=localization.GetByLabel('UI/Station/TakeControlHint'), wrapWidth=220)
        error_hint = None
        if not self._may_take_control():
            error_hint = localization.GetByLabel('UI/Station/MayNotTakeControlHint')
        elif self._is_undocking():
            error_hint = localization.GetByLabel('UI/Station/UndockingInProgressHint')
        if error_hint:
            panel.AddSpacer(height=8)
            panel.AddLabelMedium(text=error_hint, wrapWidth=220, color=eveColor.DANGER_RED)

    def _get_button(self):
        if self._button_ref is not None:
            return self._button_ref()

    def _get_structure_id(self):
        return self._docked_ui_controller.GetItemID()

    def _is_undocking(self):
        return self._docked_ui_controller.IsExiting() or self._docked_ui_controller.InProcessOfUndocking()

    def _may_take_control(self):
        return self._docked_ui_controller.MayTakeControl(self._get_structure_id())

    def _get_enabled(self):
        return self._may_take_control() and not self._is_undocking()

    def _update_enabled(self, button):
        button.enabled = self._get_enabled()

    def OnDockingProgressChanged(self, progress):
        button = self._get_button()
        if button:
            self._update_enabled(button)


def confirm_override_control(docked_ui_controller):
    structure_id = docked_ui_controller.GetItemID()
    current_pilot_id = docked_ui_controller.GetStructurePilot(structure_id)
    ConfirmTakeControl.Open(controller=docked_ui_controller, charInControl=current_pilot_id)
