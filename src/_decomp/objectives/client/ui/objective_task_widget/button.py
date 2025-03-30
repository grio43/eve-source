#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\client\ui\objective_task_widget\button.py
import eveui
from carbonui import ButtonFrameType, ButtonStyle, Density
import localization
import eveicon
import uthread2

class ButtonTaskWidget(eveui.Button):
    default_name = 'ObjectiveWidget'
    default_density = Density.COMPACT
    default_frame_type = ButtonFrameType.CUT_BOTTOM_LEFT_RIGHT
    default_opacity = 0
    __notifyevents__ = []

    def __init__(self, objective_task, *args, **kwargs):
        kwargs.setdefault('name', 'objective_task_{}'.format(objective_task.task_id))
        kwargs['func'] = self.click
        self._objective_task = objective_task
        super(ButtonTaskWidget, self).__init__(*args, **kwargs)
        self._register()
        self._on_state_changed()
        self.update()

    def Close(self):
        self._unregister()
        super(ButtonTaskWidget, self).Close()
        self._objective_task = None

    def _register(self):
        self._objective_task.on_update.connect(self.update)
        self._objective_task.on_state_changed.connect(self._on_state_changed)
        self._objective_task.on_button_state_changed.connect(self._on_button_state_changed)
        sm.RegisterNotify(self)

    def _unregister(self):
        sm.UnregisterNotify(self)
        if self._objective_task:
            self._objective_task.on_update.disconnect(self.update)
            self._objective_task.on_state_changed.disconnect(self._on_state_changed)
            self._objective_task.on_button_state_changed.disconnect(self._on_button_state_changed)

    @property
    def task_id(self):
        return self._objective_task.task_id

    @property
    def completed(self):
        return self._objective_task.completed

    @property
    def tooltip(self):
        return self._objective_task.button_tooltip

    def close(self):
        self.state = eveui.State.disabled
        self._unregister()
        self._objective_task.disable_highlight()
        if self.opacity < 1:
            self.Close()
        else:
            eveui.fade_out(self, duration=1)
            eveui.animate(self, 'padBottom', time_offset=0.5, duration=1, end_value=-self.GetAbsoluteSize()[1], on_complete=self.Close)

    def update(self, **kwargs):
        if not self._objective_task:
            return
        self.label = self._objective_task.button_label
        self.icon = self._objective_task.button_icon

    def hide(self):
        if not self.display:
            return
        if self.opacity == 0:
            self.padBottom = -self.GetAbsoluteSize()[1]
            self.Hide()
        else:
            eveui.fade_out(self, time_offset=0.5, duration=1)
            eveui.animate(self, 'padBottom', time_offset=1.5, duration=1, end_value=-self.GetAbsoluteSize()[1], on_complete=self.Hide)

    def show(self):
        eveui.fade_in(self, duration=0.5)
        eveui.animate(self, 'padBottom', duration=0, end_value=0)
        self.Show()

    def _on_state_changed(self, **kwargs):
        if not self._objective_task:
            return
        self.disabled = self._objective_task.completed
        if self._objective_task.hidden or self._objective_task.is_button_hidden:
            self.hide()
        else:
            self.show()

    def _on_button_state_changed(self):
        self._on_state_changed()

    def OnMouseEnter(self, *args):
        super(ButtonTaskWidget, self).OnMouseEnter(*args)
        self._objective_task.enable_highlight()

    def OnMouseExit(self, *args):
        super(ButtonTaskWidget, self).OnMouseExit(*args)
        self._objective_task.disable_highlight()

    def GetMenu(self, *args):
        return self._objective_task.get_context_menu()

    def GetHint(self):
        return self._objective_task.tooltip

    def click(self, *args):
        uthread2.start_tasklet(self._objective_task.button_click)


class TravelStateButtonTaskWidget(ButtonTaskWidget):
    __notifyevents__ = ['OnTravelStateChanged']

    def __init__(self, *args, **kwargs):
        super(TravelStateButtonTaskWidget, self).__init__(*args, **kwargs)
        self._travel_state = sm.GetService('tacticalNavigation').travel_state
        self._update_button_state()

    @property
    def button_action(self):
        return getattr(self._objective_task, 'button_action', None)

    @property
    def button_target(self):
        return getattr(self._objective_task, 'button_target', None)

    def OnTravelStateChanged(self, *args, **kwargs):
        self._update_button_state()

    def _update_button_state(self):
        if not self._objective_task:
            return
        if self.completed:
            self.style = ButtonStyle.SUCCESS
            self.disabled = True
            self.busy = True
            return
        action = self._travel_state.action
        target = self._travel_state.target
        self.disabled = bool(action)
        self.busy = bool(action)
        correct_action = self.button_action is None or action == self.button_action
        correct_target = True
        if correct_action and self.button_target:
            for key, value in self.button_target.iteritems():
                if key in target and target[key] != value:
                    correct_target = False
                    break

        if correct_action and correct_target:
            self.style = ButtonStyle.SUCCESS
        else:
            self.style = ButtonStyle.NORMAL


class TravelToLocationButtonTaskWidget(ButtonTaskWidget):
    __notifyevents__ = ['OnTravelStateChanged', 'OnClientEvent_DestinationSet', 'OnDestinationCleared']
    _action_label = {'jump': 'UI/Inflight/Jump',
     'dock': 'UI/Inflight/DockInStation',
     'undock': 'UI/Neocom/UndockBtn'}
    _action_icon = {'jump': eveicon.jump_to,
     'dock': eveicon.dock,
     'undock': None}

    def __init__(self, *args, **kwargs):
        self._is_destination_set = False
        self._travel_state = sm.GetService('tacticalNavigation').travel_state
        self._click_func = self._default_action
        super(TravelToLocationButtonTaskWidget, self).__init__(*args, **kwargs)

    def click(self, *args):
        if self._click_func:
            self._click_func()

    def update(self, **kwargs):
        self._update_button_state()

    def OnTravelStateChanged(self, *args, **kwargs):
        self._update_button_state()

    def OnClientEvent_DestinationSet(self, location_id):
        self._update_button_state()

    def OnDestinationCleared(self):
        self._update_button_state()

    def _update_button_state(self):
        if not self._objective_task:
            return
        if self.completed:
            self.Hide()
            return
        busy = False
        self._click_func = self._default_action
        next_action = self._objective_task.next_travel_action()
        is_destination_set = sm.GetService('starmap').GetDestination() == self._objective_task.location_id
        if not is_destination_set and self._objective_task.current_jumps:
            label = localization.GetByLabel('UI/Inflight/SetDestination')
            icon = eveicon.set_destination
            self._click_func = self._set_destination
        elif self._travel_state.action:
            label = self._travel_state.get_label()
            icon = self._travel_state.get_icon()
            busy = True
        else:
            label = self._action_label.get(next_action, '')
            if label:
                label = localization.GetByLabel(label)
            icon = self._action_icon.get(next_action, None)
        if not label:
            self.Hide()
        else:
            self.disabled = busy
            self.busy = busy
            self.label = label
            self.icon = icon
            self.Show()

    def _set_destination(self):
        sm.GetService('starmap').SetWaypoint(self._objective_task.location_id, clearOtherWaypoints=True)

    def _default_action(self):
        self._objective_task.button_click()
