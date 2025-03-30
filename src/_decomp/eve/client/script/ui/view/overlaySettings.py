#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\overlaySettings.py
from eve.client.script.ui.view.viewStateConst import ViewOverlay
SETTING_ID = 'viewStateHiddenOverlays'
DEFAULT_DISABLED = {ViewOverlay.Target, ViewOverlay.ShipUI}

def GetOverlaysDisabledInFullscreen():
    return settings.user.ui.Get(SETTING_ID, DEFAULT_DISABLED)


def IsFullscreenOverlayModeEnabled(viewOverlay):
    return viewOverlay not in GetOverlaysDisabledInFullscreen()


def ToggleFullscreenOverlayMode(viewOverlay):
    if IsFullscreenOverlayModeEnabled(viewOverlay):
        DisableFullscreenOverlayMode(viewOverlay)
    else:
        EnableFullscreenOverlayMode(viewOverlay)


def DisableFullscreenOverlayMode(viewOverlay):
    hiddenOverlays = GetOverlaysDisabledInFullscreen()
    hiddenOverlays.add(viewOverlay)
    _PersistSettings(hiddenOverlays)


def EnableFullscreenOverlayMode(viewOverlay):
    hiddenOverlays = GetOverlaysDisabledInFullscreen()
    hiddenOverlays.remove(viewOverlay)
    _PersistSettings(hiddenOverlays)


def _PersistSettings(hiddenOverlays):
    settings.user.ui.Set(SETTING_ID, hiddenOverlays)
