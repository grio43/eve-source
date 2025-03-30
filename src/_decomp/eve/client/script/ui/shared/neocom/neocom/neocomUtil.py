#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\neocomUtil.py
from carbonui import uiconst
from carbonui.uicore import uicore
from eve.client.script.ui.shared.neocom.neocom import neocomConst, neocomSignals, neocomSettings
from utillib import KeyVal

def GetSideOffset():
    width = neocomSettings.neocom_width_setting.get()
    align = neocomSettings.neocom_align_setting.get()
    if align == uiconst.TOLEFT:
        return (width, 0)
    else:
        return (0, width)


def ConvertOldTypeOfRawData(rawData):
    if isinstance(rawData, tuple):
        if len(rawData) == 3:
            btnType, id, children = rawData
        else:
            btnType, id, iconPath, children = rawData
        return KeyVal(btnType=btnType, id=id, children=children)
    return rawData


def ConvertOldButtonTypes(oldButtons):
    newButtons = []
    isInventoryAvailable = False
    for oldButton in oldButtons:
        newButton = ConvertOldTypeOfRawData(oldButton)
        if newButton.id == 'inventory':
            newButton.btnType = neocomConst.BTNTYPE_INVENTORY
            isInventoryAvailable = True
        newButtons.append(newButton)

    if not isInventoryAvailable:
        newButtons.append(KeyVal(btnType=neocomConst.BTNTYPE_INVENTORY, id='inventory', children=None))
    return newButtons


def EnableAllButtonBlinking():
    neocomSettings.neocom_allow_blink_setting.enable()
    settings.char.ui.Set('neoblinkByID', {})
    neocomSignals.on_all_button_blinking_setting_changed()


def DisableAllButtonBlinking():
    neocomSettings.neocom_allow_blink_setting.disable()
    neocomSignals.on_all_button_blinking_setting_changed()


def IsBlinkingEnabled():
    return neocomSettings.neocom_allow_blink_setting.is_enabled()


def IsInventoryBadgingEnabled():
    return neocomSettings.neocom_allow_badges_setting.is_enabled()


def ToggleInventoryBadgingEnabledInClient():
    neocomSettings.neocom_allow_badges_setting.toggle()
    neocomSignals.on_show_badging_setting_changed()


def GetNeocomAlign():
    return neocomSettings.neocom_align_setting.get()


def ResetNeocomButtons():
    if uicore.Message('AskRestartNeocomButtons', {}, uiconst.YESNO) == uiconst.ID_YES:
        settings.char.ui.Set('neocomButtonRawData', None)
        neocomSettings.neocom_width_setting.set(neocomConst.NEOCOM_DEFAULT_WIDTH)
        neocomSignals.on_reset_buttons()
