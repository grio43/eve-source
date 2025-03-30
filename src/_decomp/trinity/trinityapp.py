#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\trinity\trinityapp.py
import logging
import sys
try:
    import devenv
except ImportError:
    devenv = None

import uthread2
import blue
import trinity
import windowsutilities.windowsEvents as winevents
import trinity.windowsVirtualKeyCodes as winkeycodes
import threadutils
log = logging.getLogger(__name__)
__all__ = ['TrinityApp']
if devenv:
    _DEFAULT_RES_PATHS = (devenv.EVECLIENTRES, devenv.CARBONCLIENTRES, 'resBin:')
else:
    _DEFAULT_RES_PATHS = ()

def _on_paused_frame(*_):
    pass


class SimpleSettings(object):

    def __init__(self):
        self._d = {}

    def Get(self, key, default = None):
        return self._d.get(key, default)

    def Set(self, key, val):
        self._d[key] = val


def _set_search_paths(res):
    if isinstance(res, basestring):
        res = [res]
    if res:
        blue.paths.SetSearchPath('res', u';'.join(res))


class KeyEvent(object):

    def __init__(self, key, altKey, ctrlKey, shiftKey):
        self.key = key
        self.shiftKey = shiftKey
        self.ctrlKey = ctrlKey
        self.altKey = altKey


def _create_key_event(wParam):
    evt = KeyEvent(trinity.app.GetKeyNameText(wParam), altKey=trinity.app.Key(winkeycodes.VK_MENU), ctrlKey=trinity.app.Key(winkeycodes.VK_LCONTROL) or trinity.app.Key(winkeycodes.VK_RCONTROL), shiftKey=trinity.app.Key(winkeycodes.VK_LSHIFT) or trinity.app.Key(winkeycodes.VK_RSHIFT))
    return evt


class TrinityApp(object):

    def __init__(self, w = 320, h = 240, left = 100, top = 100, sm = 'SM_3_0_DEPTH', res = _DEFAULT_RES_PATHS, flushOnPump = True, windowed = True, pauseOnDeactivate = True, adapter = 0, back_buffer_format = trinity.PIXEL_FORMAT.B8G8R8A8_UNORM, present_interval = trinity.PRESENT_INTERVAL.IMMEDIATE, fixedWindow = False):
        self.flushOnPump = flushOnPump
        self.pauseOnDeactivate = pauseOnDeactivate
        self.width = w
        self.height = h
        self.windowed = windowed
        self.fixedWindow = fixedWindow
        self.adapter = adapter
        self.back_buffer_format = back_buffer_format
        self.present_interval = present_interval
        self.on_mouse_move = threadutils.Signal()
        self.on_close = threadutils.Signal()
        self.on_activate = threadutils.Signal()
        self.on_deactivate = threadutils.Signal()
        self.on_resize = threadutils.Signal()
        self.on_key_down = threadutils.Signal()
        self.on_key_up = threadutils.Signal()
        _set_search_paths(res)
        trinity.SetShaderModel(sm)
        trinity.device.tickInterval = 0
        trinity.mainWindow.onMouseMove = self._on_mouse_move
        trinity.mainWindow.onKeyDown = self._on_key_down
        trinity.mainWindow.onKeyUp = self._on_key_up
        trinity.mainWindow.onClose = self._on_close
        trinity.mainWindow.onSwapChainChange = self._on_app_resize_event
        self._is_active = True
        self._create_device(left, top)

    def _create_device(self, left, top):
        state = trinity.Tr2MainWindowState()
        state.windowMode = trinity.Tr2WindowMode.WINDOWED if self.windowed else trinity.Tr2WindowMode.FULL_SCREEN
        state.adapter = self.adapter
        state.width = self.width
        state.height = self.height
        state.presentInterval = self.present_interval
        state.left = left
        state.top = top
        while True:
            try:
                trinity.mainWindow.SetWindowState(state)
                break
            except:
                pass

    def update(self):
        pass

    def update_after_pump(self):
        pass

    def _process_loop(self):
        trinity.app.ProcessMessages()
        processedFrame = False
        active = trinity.app.IsActive()
        if active != self._is_active:
            self._is_active = active
            if active:
                self.on_activate.emit()
            else:
                self.on_deactivate.emit()
        if not self.pauseOnDeactivate or active:
            self.update()
            blue.os.Pump()
            if self.flushOnPump:
                sys.stdout.flush()
                sys.stderr.flush()
            self.update_after_pump()
            processedFrame = True
        try:
            uthread2.Yield()
        except:
            blue.os.Pump()

        return processedFrame

    def run_frames(self, frame_count, on_paused_frame = _on_paused_frame):
        while frame_count != 0:
            if self._process_loop():
                frame_count -= 1
            else:
                on_paused_frame(self)

    def exec_(self):
        while True:
            self._process_loop()

    def _on_mouse_move(self, left, top):
        self.on_mouse_move.emit(left, top)

    def _on_key_down(self, key, _):
        evt = _create_key_event(key)
        self.on_key_down.emit(evt)

    def _on_key_up(self, key, _):
        evt = _create_key_event(key)
        self.on_key_up.emit(evt)

    def _on_close(self):
        log.debug('Closing.')
        self.on_close.emit()
        blue.os.Terminate(0)

    def _on_app_resize_event(self, *_):
        if not self.windowed:
            return
        self.on_resize.emit()

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(TrinityApp, '_instance'):
            TrinityApp._instance = TrinityApp(*args, **kwargs)
        return TrinityApp._instance


def create_windowless_device(respath = _DEFAULT_RES_PATHS):
    blue.paths.SetSearchPath('res', u';'.join(respath))
    trinity.device.deviceType = trinity.TriDeviceType.SOFTWARE
    try:
        trinity.device.CreateWindowlessDevice()
    except trinity.ALError:
        log.exception('Failed to create windowless trinity device, trying a normal one')
        TrinityApp()


if __name__ == '__main__':
    logging.root.setLevel(logging.DEBUG)
    TrinityApp.instance().exec_()
