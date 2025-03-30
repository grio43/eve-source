#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\dockedUI\undockButton.py
import weakref
import localization
from carbon.common.script.sys.serviceManager import ServiceManager
from carbonui.control.button import Button
from eve.client.script.ui.control import primaryButton
from carbonui import ButtonVariant, Density
from uihighlighting.uniqueNameConst import UNIQUE_NAME_UNDOCK_BTN

class UndockButton(Button):

    def __init__(self, docked_ui_controller, **kwargs):
        self._controller = UndockButtonController(docked_ui_controller)
        super(UndockButton, self).__init__(name='undockButton', density=Density.EXPANDED, variant=ButtonVariant.PRIMARY, func=docked_ui_controller.Undock, args=(), uniqueUiName=UNIQUE_NAME_UNDOCK_BTN, **kwargs)
        self._controller.connect(self)

    def Close(self):
        if self._controller:
            self._controller.close()
        super(UndockButton, self).Close()


class UndockButtonController(object):
    _button_ref = None

    def __init__(self, docked_ui_controller):
        self._docked_ui_controller = docked_ui_controller

    def connect(self, button):
        self._button_ref = weakref.ref(button)
        self._update_busy(button)
        self._update_button_label(button)
        self._update_enabled(button)
        button.on_hovered_changed.connect(self._on_button_hovered_changed)
        ServiceManager.Instance().RegisterForNotifyEvent(self, 'OnDockingProgressChanged')

    def close(self):
        button = self._get_button()
        if button:
            button.on_hovered_changed.disconnect(self._on_button_hovered_changed)
        ServiceManager.Instance().UnregisterForNotifyEvent(self, 'OnDockingProgressChanged')

    def _get_button(self):
        if self._button_ref is not None:
            return self._button_ref()

    def _is_beyond_point_of_no_return(self):
        return self._docked_ui_controller.InProcessOfUndocking()

    def _is_undocking(self):
        return self._docked_ui_controller.IsExiting() or self._is_beyond_point_of_no_return()

    def _update_button_label(self, button):
        if self._is_beyond_point_of_no_return():
            button.label = localization.GetByLabel('UI/Station/UndockingConfirmed')
        elif self._is_undocking() and button.hovered:
            button.label = localization.GetByLabel('UI/Station/AbortUndock')
        elif self._is_undocking():
            button.label = localization.GetByLabel('UI/Station/Undocking')
        else:
            button.label = localization.GetByLabel('UI/Neocom/UndockBtn')

    def _update_busy(self, button):
        if self._is_undocking():
            button.busy = True
        else:
            button.busy = False

    def _update_enabled(self, button):
        button.enabled = not self._docked_ui_controller.InProcessOfUndocking()

    def _on_button_hovered_changed(self, button):
        self._update_button_label(button)

    def OnDockingProgressChanged(self, progress):
        button = self._get_button()
        if button:
            self._update_busy(button)
            self._update_button_label(button)
            self._update_enabled(button)
