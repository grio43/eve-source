#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\overview\overviewUtil.py
import collections
import localization
from carbon.common.script.util.commonutils import StripTags
from carbonui import fontconst
from carbonui.control.comboEntryData import ComboEntryDataCaption, ComboEntryData
from eve.client.script.parklife.overview.default.categories import CATEGORY_NAME_LABELS, CATEGORY_ORDER
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.inflight.overview import overviewColumns
from eve.client.script.ui.inflight.overview.overviewConst import COLUMN_VELOCITY, COLUMN_ANGULARVELOCITY, COLUMN_TRANSVERSALVELOCITY, COLUMN_RADIALVELOCITY, ALLCOLUMNS
from localization import GetByLabel
from overviewPresets import overviewSettingsConst as osConst

def IsFleetMember(slimItem):
    if not session.fleetid or not slimItem or not slimItem.ownerID:
        return False
    return sm.GetService('fleet').IsMember(slimItem.ownerID)


def GetSortValueWhenBroadcastGoToTop(_node, fleetBroadcasts, currentDirection):
    if _node.itemID in fleetBroadcasts:
        toTopValue = 1
    else:
        toTopValue = 2
    if not currentDirection:
        toTopValue *= -1
    return (toTopValue, _node.sortValue)


def GetAllianceTickerName(slimItem):
    return '[' + cfg.allianceshortnames.Get(slimItem.allianceID).shortName + ']'


def GetCorpTickerName(slimItem):
    return '[' + cfg.corptickernames.Get(slimItem.corpID).tickerName + ']'


def PrepareLocalizationTooltip(text):
    localizedTags = Label.ExtractLocalizedTags(text)
    if localizedTags:
        hint = localizedTags[0].get('hint', None)
        text = StripTags(text)
    else:
        hint = None
    return (text, hint)


def GetSlimItemForCharID(charID):
    ballpark = sm.GetService('michelle').GetBallpark()
    if ballpark:
        for rec in ballpark.slimItems.itervalues():
            if rec.charID == charID:
                return rec


def GetEntryFontSize():
    useSmallText = sm.GetService('overviewPresetSvc').GetSettingValueOrDefaultFromName(osConst.SETTING_NAME_SMALL_TEXT, False)
    if useSmallText:
        fontSize = fontconst.EVE_SMALL_FONTSIZE
    else:
        fontSize = fontconst.EVE_MEDIUM_FONTSIZE
    return fontSize


def GetEntryHeight(isCompact):
    useSmallText = sm.GetService('overviewPresetSvc').GetSettingValueOrDefaultFromName(osConst.SETTING_NAME_SMALL_TEXT, False)
    if useSmallText:
        return 17
    elif not isCompact:
        return 24
    else:
        return 19


def GetColumnValuesToCalculate(columns):
    calculateRadialVelocity = False
    calculateCombinedVelocity = False
    calculateRadialNormal = False
    calculateTransveralVelocity = False
    calculateAngularVelocity = False
    calculateVelocity = False
    showVelocityCombined = False
    if COLUMN_VELOCITY in columns:
        calculateVelocity = True
        showVelocityCombined = True
    if COLUMN_ANGULARVELOCITY in columns:
        calculateRadialVelocity = True
        calculateCombinedVelocity = True
        calculateRadialNormal = True
        calculateTransveralVelocity = True
        calculateAngularVelocity = True
        showVelocityCombined = True
    if COLUMN_TRANSVERSALVELOCITY in columns:
        calculateRadialVelocity = True
        calculateCombinedVelocity = True
        calculateRadialNormal = True
        calculateTransveralVelocity = True
        showVelocityCombined = True
    if COLUMN_RADIALVELOCITY in columns:
        calculateRadialVelocity = True
        calculateCombinedVelocity = True
        calculateRadialNormal = True
        showVelocityCombined = True
    return (calculateAngularVelocity,
     calculateCombinedVelocity,
     calculateRadialNormal,
     calculateRadialVelocity,
     calculateTransveralVelocity,
     calculateVelocity,
     showVelocityCombined)


def GetColumnSettingsAndSortKeys(currentActive = None, tabID = None):
    columns = overviewColumns.GetColumns(tabID)
    if currentActive:
        sortKeys = columns[columns.index(currentActive):]
    else:
        sortKeys = []
    columnSettings = {}
    for columnID in ALLCOLUMNS:
        if columnID in columns:
            if columnID in sortKeys:
                columnSettings[columnID] = (True, sortKeys.index(columnID))
            else:
                columnSettings[columnID] = (True, None)
        else:
            columnSettings[columnID] = (False, None)

    return (columnSettings, sortKeys)


def GetFilterComboOptions():
    ret = []
    customFilters = GetCustomFiltersSorted()
    if customFilters:
        ret += [ComboEntryDataCaption(GetByLabel('UI/Overview/CustomFilters'))] + GetComboEntries(customFilters)
    ret += [ComboEntryDataCaption(GetByLabel('UI/Overview/DefaultFilters'))] + GetComboEntries(GetDefaultFiltersSorted())
    return ret


def GetComboEntries(presetNames):
    presetSvc = sm.GetService('overviewPresetSvc')
    return [ ComboEntryData(presetSvc.GetPresetDisplayName(presetName), presetName, hint=presetSvc.GetDefaultOverviewDescription(presetName)) for presetName in presetNames ]


def GetCustomFiltersSorted():
    presetSvc = sm.GetService('overviewPresetSvc')
    return GetFiltersSorted(presetSvc.GetCustomPresetNames())


def GetFiltersSorted(preset_names):
    presetSvc = sm.GetService('overviewPresetSvc')
    return localization.util.Sort(preset_names, key=lambda p: presetSvc.GetPresetDisplayName(p))


def GetDefaultFiltersSorted():
    ret = []
    for preset_names in GetDefaultFiltersByCategory().values():
        ret.extend(preset_names)

    return ret


def GetDefaultFiltersByCategory():
    presetSvc = sm.GetService('overviewPresetSvc')
    ret = collections.defaultdict(list)
    for preset_name in presetSvc.GetDefaultOverviewPresetNames():
        category_id = presetSvc.GetDefaultOverviewCategoryID(preset_name)
        ret[category_id].append(preset_name)

    return _GetFiltersByCategorySorted(ret)


def _GetFiltersByCategorySorted(preset_names_by_category_id):
    ret = collections.OrderedDict()
    for category_id in CATEGORY_ORDER:
        if category_id in preset_names_by_category_id:
            ret[category_id] = GetFiltersSorted(preset_names_by_category_id[category_id])

    return ret
