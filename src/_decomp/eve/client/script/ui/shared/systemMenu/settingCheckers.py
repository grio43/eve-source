#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\systemMenu\settingCheckers.py
SMALL_STATION_BUTTONS_SETTING = 'stationservicebtns'
SMALL_STATION_BUTTONS_DEFAULT = 1
SMALL_STATION_BUTTONS_LABEL = 'UI/SystemMenu/GeneralSettings/Station/SmallButtons'

def get_small_station_buttons_setting(use_default = False):
    return get_setting(settings.user.ui.Get, SMALL_STATION_BUTTONS_SETTING, SMALL_STATION_BUTTONS_DEFAULT, use_default)


def get_setting(getter, setting, default, use_default = False):
    if use_default:
        default = str(default) + ' (default)'
    return getter(setting, default)
