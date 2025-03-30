#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\invPanelSettings.py
from carbonui.util.various_unsorted import GetAttrs

def _GetComboPrefsKey():
    return ('char', 'ui', 'fittingInvCombo')


def GetInvComboSettingValue():
    config, prefstype = _GetPrefsTypeAndConfig()
    s = GetAttrs(settings, *prefstype)
    try:
        return s.Get(config, None)
    except:
        pass


def _GetPrefsTypeAndConfig():
    prefsKey = _GetComboPrefsKey()
    config = prefsKey[-1]
    prefstype = prefsKey[:-1]
    return (config, prefstype)
