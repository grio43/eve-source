#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveaudio\immersiveoverlay.py


class Manager(object):

    def __init__(self, send_audio_event):
        self._send_audio_event_func = send_audio_event
        self._full_screen_overlays = set()
        self._window_overlays = set()
        self._last_event = None

    def create(self, name):
        return ImmersiveOverlay(name=name, on_state_changed=self._on_overlay_state_changed)

    def _update(self):
        if len(self._full_screen_overlays) > 0:
            self._send_audio_event(AudioEvent.full_screen)
        elif len(self._window_overlays) > 0:
            self._send_audio_event(AudioEvent.window)
        else:
            self._send_audio_event(AudioEvent.off)

    def _send_audio_event(self, event):
        if event != self._last_event:
            self._send_audio_event_func(event)
            self._last_event = event

    def _on_overlay_state_changed(self, overlay):
        if overlay.state == State.full_screen:
            self._full_screen_overlays.add(id(overlay))
            self._window_overlays.discard(id(overlay))
        elif overlay.state == State.windowed:
            self._full_screen_overlays.discard(id(overlay))
            self._window_overlays.add(id(overlay))
        elif overlay.state in (State.minimized, State.closed):
            self._full_screen_overlays.discard(id(overlay))
            self._window_overlays.discard(id(overlay))
        self._update()


class AudioEvent(object):
    full_screen = 'ui_immersive_overlay_fullscreen'
    window = 'ui_immersive_overlay_window'
    off = 'ui_immersive_overlay_off'


class ImmersiveOverlay(object):

    def __init__(self, name, on_state_changed):
        self._name = name
        self._on_state_changed = on_state_changed
        self._state = State.initialized

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if self._state == State.closed:
            return
        if value != self._state:
            self._state = value
            self._on_state_changed(self)

    def close(self):
        self.state = State.closed

    def set_full_screen(self):
        self.state = State.full_screen

    def set_windowed(self):
        self.state = State.windowed

    def set_minimized(self):
        self.state = State.minimized

    def __del__(self):
        if self._state != State.closed:
            self.close()


class State(object):
    initialized = 0
    full_screen = 1
    windowed = 2
    minimized = 3
    closed = 4
