#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\util\defaultRangeUtils.py
_RANGE_BY_TYPE_SETTING_FORMAT = 'defaultType%sDist'
WARP_TO_SETTING = 'WarpTo'
ORBIT_SETTING = 'Orbit'
KEEP_AT_RANGE_SETTING = 'KeepAtRange'
_GENERIC_TYPE_ID = 0
DEFAULT_RANGES = {WARP_TO_SETTING: const.minWarpEndDistance,
 ORBIT_SETTING: 1000,
 KEEP_AT_RANGE_SETTING: 1000}
RANGES_THAT_APPLY_TO_ALL_SHIP_TYPES = [WARP_TO_SETTING]

def _GetCurrentShipTypeID():
    if session.shipid and session.solarsystemid:
        shipItem = sm.GetService('godma').GetItem(session.shipid)
        if shipItem:
            return shipItem.typeID


def UpdateRangeSetting(key, newRange):
    typeRangeSettings = _GetRangeSetting(key)
    if key not in RANGES_THAT_APPLY_TO_ALL_SHIP_TYPES:
        typeID = _GetCurrentShipTypeID()
        if typeID is not None:
            typeRangeSettings[typeID] = newRange
    typeRangeSettings[_GENERIC_TYPE_ID] = newRange
    _UpdateRangeSetting(key, typeRangeSettings)


def UpdateRangeSettingForShipType(typeID, key, newRange):
    typeRangeSettings = _GetRangeSetting(key)
    if key not in RANGES_THAT_APPLY_TO_ALL_SHIP_TYPES:
        typeRangeSettings[typeID] = newRange
    _UpdateRangeSetting(key, typeRangeSettings)


def _GetRangeSetting(key):
    return settings.char.ui.Get(_RANGE_BY_TYPE_SETTING_FORMAT % key, {})


def _UpdateRangeSetting(key, typeRangeSettings):
    settings.char.ui.Set(_RANGE_BY_TYPE_SETTING_FORMAT % key, typeRangeSettings)
    sm.ScatterEvent('OnDistSettingsChange')


def FetchRangeSetting(key):
    if key not in DEFAULT_RANGES:
        return
    typeRangeSettings = _GetRangeSetting(key)
    if key not in RANGES_THAT_APPLY_TO_ALL_SHIP_TYPES:
        typeID = _GetCurrentShipTypeID()
        if typeID is not None and typeID in typeRangeSettings:
            return typeRangeSettings[typeID]
    if _GENERIC_TYPE_ID in typeRangeSettings:
        return typeRangeSettings[_GENERIC_TYPE_ID]
    return DEFAULT_RANGES[key]


def SetDefaultKeepAtRangeDist(newRange, *args):
    UpdateRangeSetting('KeepAtRange', newRange)


def SetDefaultOrbitDist(newRange, *args):
    UpdateRangeSetting('Orbit', newRange)


def SetDefaultWarpToDist(newRange, *args):
    UpdateRangeSetting('WarpTo', newRange)
