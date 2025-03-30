#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\dockedUI\modeButton.py
import weakref
import caching
import localization
from carbon.common.script.sys.serviceManager import ServiceManager
from carbonui.control.button import Button
from eve.client.script.ui import eveColor
from eve.client.script.ui.control import primaryButton
from eve.client.script.ui.view.viewStateConst import ViewState

class ModeButton(Button):

    def __init__(self, docked_ui_controller, view_state_service, **kwargs):
        self._controller = ModeButtonController(docked_ui_controller, view_state_service)
        self._docked_ui_controller = docked_ui_controller
        self._view_state_service = view_state_service
        super(ModeButton, self).__init__(name='dockedModeBtn', func=self._execute, args=(), **kwargs)
        self._controller.connect(self)

    def Close(self):
        self._controller.close()
        super(ModeButton, self).Close()

    def LoadTooltipPanel(self, panel, owner):
        self._controller.load_tooltip_panel(panel, owner)

    def _execute(self):
        with self.busy_context:
            self._controller.execute()


class ModeButtonController(object):
    _button_ref = None

    def __init__(self, docked_ui_controller, view_state_service):
        self._docked_ui_controller = docked_ui_controller
        self._view_state_service = view_state_service

    def connect(self, button):
        self._button_ref = weakref.ref(button)
        self._update_enabled(button)
        self._update_label(button)
        ServiceManager.Instance().RegisterForNotifyEvent(self, 'OnDockingProgressChanged')
        ServiceManager.Instance().RegisterForNotifyEvent(self, 'OnPrimaryViewChanged')

    def close(self):
        ServiceManager.Instance().UnregisterForNotifyEvent(self, 'OnDockingProgressChanged')
        ServiceManager.Instance().UnregisterForNotifyEvent(self, 'OnPrimaryViewChanged')

    def execute(self):
        self._docked_ui_controller.ChangeDockedMode(self._view_state_service)

    def load_tooltip_panel(self, panel, owner):
        panel.LoadGeneric1ColumnTemplate()
        if self._is_viewing_hangar():
            text = localization.GetByLabel('UI/Station/ViewOutsideHint')
        else:
            text = localization.GetByLabel('UI/Station/ViewHangarHint')
        panel.AddLabelMedium(text=text, wrapWidth=220)
        if not self._get_enabled():
            panel.AddSpacer(height=8)
            panel.AddLabelMedium(text=localization.GetByLabel('UI/Station/UndockingInProgressHint'), wrapWidth=220, color=eveColor.DANGER_RED)

    def _get_button(self):
        if self._button_ref is not None:
            return self._button_ref()

    def _is_undocking(self):
        return self._docked_ui_controller.IsExiting() or self._docked_ui_controller.InProcessOfUndocking()

    def _is_viewing_hangar(self):
        return self._view_state_service.IsPrimaryViewActive(ViewState.Hangar)

    def _get_enabled(self):
        return not self._is_undocking()

    def _update_enabled(self, button):
        button.enabled = self._get_enabled()

    def _get_label(self):
        if self._is_viewing_hangar():
            return localization.GetByLabel('UI/Station/ViewOutside')
        else:
            return localization.GetByLabel('UI/Station/ViewHangar')

    def _update_label(self, button):
        button.label = self._get_label()

    def OnDockingProgressChanged(self, progress):
        button = self._get_button()
        if button:
            self._update_enabled(button)

    def OnPrimaryViewChanged(self, old_view_info, new_view_info):
        button = self._get_button()
        if button:
            self._update_label(button)
