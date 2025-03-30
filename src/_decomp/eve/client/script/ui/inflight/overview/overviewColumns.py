#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\overview\overviewColumns.py
from eve.client.script.ui.inflight.overview import overviewConst
from localization import GetByLabel
from overviewPresets import overviewSettingsConst

def GetColumnLabel(columnID, addFormatUnit = False):
    localizedID = overviewConst.NAME_BY_COLUMN.get(columnID, None)
    if localizedID:
        retString = GetByLabel(localizedID)
        if addFormatUnit:
            unitLabelID = overviewConst.COLUMN_UNITS.get(columnID, None)
            if unitLabelID:
                retString = '%s (%s)' % (retString, GetByLabel(unitLabelID))
        return retString
    return columnID


def GetColumnOrder(tabID = None):
    if tabID is not None:
        columnIDs = sm.GetService('overviewPresetSvc').GetTabColumnOrder(tabID)
    else:
        columnIDs = settings.user.overview.Get(overviewSettingsConst.SETTING_COLUMN_ORDER, None)
    if columnIDs is None:
        return overviewConst.ALL_COLUMNS
    return columnIDs


def GetColumns(tabID = None):
    if tabID is not None:
        columnIDs = sm.GetService('overviewPresetSvc').GetTabVisibleColumnIDs(tabID)
    else:
        columnIDs = settings.user.overview.Get(overviewSettingsConst.SETTING_COLUMNS, None)
        if columnIDs is None:
            columnIDs = overviewConst.DEFAULT_COLUMNS
    userSetOrder = GetColumnOrder(tabID)
    return [ columnID for columnID in userSetOrder if columnID in columnIDs ]
