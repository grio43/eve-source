#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\scannerFiles\scannerUtil.py
from carbon.common.script.util.format import IntToRoman
from carbonui.control.editPlainText import EditPlainTextCore
from carbonui.control.singlelineedits.baseSingleLineEdit import BaseSingleLineEdit
from carbonui.uicore import uicore
from eve.client.script.ui.shared.mapView.dockPanelUtil import GetPanelAlignMode
import carbonui.const as uiconst
from localization import GetByLabel
COLOR_DSCAN = (0.225, 0.75, 0.5, 1.0)

def IsProbeScanPanelEmbedded():
    return settings.char.ui.Get('mapProbePanelEmbedded', True)


def IsProbeScanEmbeddedPanelOpen():
    return settings.char.ui.Get('probeScanPanelOpen', False)


def SetProbeScanEmbeddedPanelOpen():
    settings.char.ui.Set('probeScanPanelOpen', True)


def SetProbeScanEmbeddedPanelClosed():
    settings.char.ui.Set('probeScanPanelOpen', False)


def SetProbeScanPanelEmbedded():
    settings.char.ui.Set('mapProbePanelEmbedded', True)


def SetProbeScanPanelWindowed():
    settings.char.ui.Set('mapProbePanelEmbedded', False)


def IsDirectionalScanPanelEmbedded():
    return settings.char.ui.Get('mapDirectionPanelEmbedded', True)


def IsDirectionalScanEmbeddedPanelOpen():
    return settings.char.ui.Get('directionalScanPanelOpen', False)


def SetDirectionalScanEmbeddedPanelOpen():
    settings.char.ui.Set('directionalScanPanelOpen', True)


def SetDirectionalScanEmbeddedPanelClosed():
    settings.char.ui.Set('directionalScanPanelOpen', False)


def SetDirectionalScanPanelEmbedded():
    settings.char.ui.Set('mapDirectionPanelEmbedded', True)


def SetDirectionalScanPanelWindowed():
    settings.char.ui.Set('mapDirectionPanelEmbedded', False)


def IsSolarSystemMapFullscreen():
    return GetPanelAlignMode('solar_system_map_panel') == uiconst.TOALL


def GetScanDifficultyText(difficulty):
    if difficulty is None:
        return GetByLabel('UI/Inflight/Scanner/DifficultyUnknown')
    else:
        level = IntToRoman(difficulty)
        return GetByLabel('UI/Agents/AgentEntry/Level', level=level)


def IsShortuctExecutionAllowed(panel):
    return not IsEditFieldInFocus() and not IsModifierKeyPressed()


def IsEditFieldInFocus():
    focus = uicore.registry.GetFocus()
    editFieldHasFocus = focus and isinstance(focus, (EditPlainTextCore, BaseSingleLineEdit))
    return editFieldHasFocus


def IsModifierKeyPressed():
    for key in (uiconst.VK_CONTROL, uiconst.VK_MENU, uiconst.VK_SHIFT):
        if uicore.uilib.Key(key):
            return True

    return False
