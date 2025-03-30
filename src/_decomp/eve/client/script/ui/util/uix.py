#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\util\uix.py
import math
import sys
import types
import blue
import caching
import dogma.data
import dogma.units
import eveicon
import evetypes
import localization
import log
import metaGroups
import telemetry
import trinity
import utillib
from carbon.common.script.util.format import FmtAmt
from carbonui import fontconst, uiconst
from carbonui.control.scroll_const import GetHiddenColumnsKey
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from carbonui.util.bunch import Bunch
from carbonui.util.various_unsorted import MapIcon
from dogma.attributes.format import GetFormatAndValue
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.eveIcon import GetLogoIcon, Icon
from carbonui.control.window import Window
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.common.lib import appConst as const
from eve.common.script.sys import idCheckers
from eve.common.script.sys.idCheckers import IsSolarSystem, IsKnownSpaceSystem
from eve.common.script.util.eveFormat import FmtISK, GetAveragePrice
from fsdBuiltData.common.iconIDs import GetIconFile
from inventorycommon.const import VIEWMODE_ICONS, VIEWMODE_DETAILS, VIEWMODE_LIST, VIEWMODE_CARDS
from inventorycommon.util import GetItemVolume
from spacecomponents.common.helper import HasDeployComponent, HasNpcPilotComponent
from inventorycommon.typeHelpers import GetAveragePrice as GetAverageTypePrice
isTakeTimeEnabled = True
slotTextByEffect = {const.effectRigSlot: 'UI/Inventory/SlotRigs',
 const.effectHiPower: 'UI/Inventory/SlotHigh',
 const.effectMedPower: 'UI/Inventory/SlotMedium',
 const.effectLoPower: 'UI/Inventory/SlotLow'}
categoryGroupTypeStringForTypeID = {}

def TakeTime(label, func, *args, **kw):
    if isTakeTimeEnabled:
        t = blue.pyos.taskletTimer.EnterTasklet(label)
        try:
            return func(*args, **kw)
        finally:
            blue.pyos.taskletTimer.ReturnFromTasklet(t)

    else:
        return func(*args, **kw)


@telemetry.ZONE_FUNCTION
def GetItemData(rec, viewMode, viewOnly = 0, container = None, scrollID = None, *args, **kw):
    attribs = {}
    for attribute in sm.GetService('godma').GetType(rec.typeID).displayAttributes:
        attribs[attribute.attributeID] = attribute.value

    sort_slotsize = 0
    for effect in dogma.data.get_type_effects(rec.typeID):
        if effect.effectID in (const.effectHiPower, const.effectMedPower, const.effectLoPower):
            sort_slotsize = 1
            break

    data = Bunch()
    data.__guid__ = 'listentry.InvItem'
    data.item = rec
    data.rec = rec
    data.itemID = rec.itemID
    data.godmaattribs = attribs
    data.invtype = rec.typeID
    data.container = container
    data.viewMode = viewMode
    data.viewOnly = viewOnly
    data.locked = rec.flagID == const.flagLocked
    data.sublevel = kw.get('sublevel', 0)
    if not data.locked and rec.flagID != const.flagUnlocked and container and container.invController.isLockable:
        if hasattr(container, 'invController'):
            containerItem = container.invController.GetInventoryItem()
            if containerItem:
                maybeLocked = containerItem.groupID in (const.groupAuditLogSecureContainer, const.groupStation)
                maybeLocked = maybeLocked or evetypes.GetCategoryID(data.invtype) == const.categoryBlueprint and containerItem.typeID in (const.typeOffice, const.typeAssetSafetyWrap)
                if maybeLocked:
                    data.locked = sm.GetService('lockedItems').IsItemLocked(rec)
    data.factionID = sm.GetService('faction').GetCurrentFactionID()
    if rec.singleton or rec.typeID in (const.typeBookmark,):
        data.Set('sort_%s' % localization.GetByLabel('UI/Common/Quantity'), 0)
    else:
        data.Set('sort_%s' % localization.GetByLabel('UI/Common/Quantity'), rec.stacksize)
    ml = evetypes.GetMetaLevel(data.invtype)
    if not ml:
        metaLevel = ''
    else:
        metaLevel = FmtAmt(ml)
    data.metaLevel = metaLevel
    data.groupName = evetypes.GetGroupName(rec.typeID)
    data.categoryName = evetypes.GetCategoryName(rec.typeID)
    estPrice = GetAveragePrice(rec)
    data.estPrice = rec.stacksize * estPrice if estPrice and rec.stacksize else None
    data.sort_ammosizeconstraints = attribs.has_key(const.attributeChargeSize)
    data.sort_slotsize = sort_slotsize
    data.Set('sort_%s' % localization.GetByLabel('UI/Common/Name'), GetItemName(rec, data).lower())
    data.Set('sort_%s' % localization.GetByLabel('UI/Common/Type'), GetCategoryGroupTypeStringForItem(rec).lower())
    data.Set('sort_%s' % localization.GetByLabel('UI/Inventory/ItemMetaLevel'), ml or 0.0)
    data.Set('sort_%s' % localization.GetByLabel('UI/Inventory/ItemGroup'), data.groupName.lower())
    data.Set('sort_%s' % localization.GetByLabel('UI/Inventory/ItemCategory'), data.categoryName.lower())
    data.Set('sort_%s' % localization.GetByLabel('UI/Contracts/ContractsWindow/EstPrice'), data.estPrice or 0)
    if data.rec.typeID == const.typePlasticWrap:
        data.volume = ''
        data.Set('sort_%s' % localization.GetByLabel('UI/Inventory/ItemVolume'), 0)
    else:
        volume = GetItemVolume(rec)
        unit = dogma.units.get_display_name(const.unitVolume)
        decimalPlaces = 2 if abs(volume - int(volume)) > const.FLOAT_TOLERANCE else 0
        data.volume = localization.GetByLabel('UI/InfoWindow/ValueAndUnit', value=FmtAmt(volume, showFraction=decimalPlaces), unit=unit)
        data.Set('sort_%s' % localization.GetByLabel('UI/Inventory/ItemVolume'), volume)
    data.scrollID = scrollID
    return data


@telemetry.ZONE_FUNCTION
def GetItemLabel(rec, data, new = 0):
    if getattr(data, 'label', None) and data.viewMode == VIEWMODE_ICONS and not new:
        return data.label
    name = GetItemName(rec, data)
    if data.viewMode in (VIEWMODE_LIST, VIEWMODE_DETAILS):
        label = GetItemLabelForListOrDetails(rec, data, name)
        data.label = label
    elif data.viewMode == VIEWMODE_CARDS:
        data.label = name
    else:
        data.label = '<center>%s' % name
    return data.label


class Column(object):
    NAME = 0
    QUANTITY = 1
    GROUP = 2
    CATEGORY = 3
    SIZE = 4
    SLOT = 5
    VOLUME = 6
    META_LEVEL = 7
    TECH_LEVEL = 8
    ESTIMATED_PRICE = 9
    _COLUMN_BY_LABEL = {'UI/Common/Name': NAME,
     'UI/Common/Quantity': QUANTITY,
     'UI/Inventory/ItemGroup': GROUP,
     'UI/Inventory/ItemCategory': CATEGORY,
     'UI/Inventory/ItemSize': SIZE,
     'UI/Inventory/ItemSlot': SLOT,
     'UI/Inventory/ItemVolume': VOLUME,
     'UI/Inventory/ItemMetaLevel': META_LEVEL,
     'UI/Inventory/ItemTechLevel': TECH_LEVEL,
     'UI/Contracts/ContractsWindow/EstPrice': ESTIMATED_PRICE}
    _cached_column_localized_labels_by_language_id = {}

    @classmethod
    def from_localized_label(cls, text):
        language_id = session.languageID
        if language_id not in cls._cached_column_localized_labels_by_language_id:
            Column._cache_localized_labels_for_language(session.languageID)
        return cls._cached_column_localized_labels_by_language_id[language_id][text]

    @classmethod
    def _cache_localized_labels_for_language(cls, language_id):
        cls._cached_column_localized_labels_by_language_id[language_id] = {localization.GetByLabel(label, languageID=language_id):header for label, header in cls._COLUMN_BY_LABEL.items()}


def _get_item_size(rec, data, name):
    attribs = getattr(data, 'godmaattribs', {})
    if const.attributeChargeSize in attribs:
        return GetFormatAndValue(attributeType=utillib.KeyVal(unitID=const.unitSizeclass, attributeID=const.attributeChargeSize, dataType=const.attributeDataTypeTypeInteger), value=attribs[const.attributeChargeSize])
    else:
        return ''


def _get_item_slot(rec, data, name):
    attribs = getattr(data, 'godmaattribs', {})
    if const.attributeImplantness in attribs:
        return GetFormatAndValue(attributeType=utillib.KeyVal(unitID=int, attributeID=const.attributeImplantness, dataType=const.attributeDataTypeTypeInteger), value=attribs[const.attributeImplantness])
    elif const.attributeBoosterness in attribs:
        return GetFormatAndValue(attributeType=utillib.KeyVal(unitID=int, attributeID=const.attributeBoosterness, dataType=const.attributeDataTypeTypeInteger), value=attribs[const.attributeBoosterness])
    else:
        return GetPowerSlotSizeSymbol(rec.typeID) or ''


def _get_item_tech_level(rec, data, name):
    techLevel = evetypes.GetTechLevel(rec.typeID)
    if techLevel:
        techLevel = FmtAmt(techLevel)
    return '<right>%s' % techLevel


_item_column_value_getter_by_column = {Column.NAME: lambda rec, data, name: name,
 Column.QUANTITY: lambda rec, data, name: '<right>%s' % GetItemQty(data, 'ln'),
 Column.GROUP: lambda rec, data, name: data.groupName,
 Column.CATEGORY: lambda rec, data, name: data.categoryName,
 Column.SIZE: _get_item_size,
 Column.SLOT: _get_item_slot,
 Column.VOLUME: lambda rec, data, name: '<right>%s' % data.volume,
 Column.META_LEVEL: lambda rec, data, name: '<right>%s' % data.metaLevel,
 Column.TECH_LEVEL: _get_item_tech_level,
 Column.ESTIMATED_PRICE: lambda rec, data, name: ('<right>%s' % FmtISK(data.estPrice) if data.estPrice else '')}

def GetImplantsCostForCharacter():
    try:
        godma = sm.GetService('godma')
        godmaItem = godma.GetItem(session.charid)
        if godmaItem:
            implantCost = sum((GetAverageTypePrice(x.typeID) or 0 for x in godmaItem.implants))
            return implantCost
        return None
    except StandardError as e:
        log.LogException('Failing to get implant cost')


def GetItemLabelForListOrDetails(rec, data, name):
    column_values = []
    for header in GetVisibleItemHeaders(data.scrollID):
        getter = _item_column_value_getter_by_column[Column.from_localized_label(header)]
        column_values.append(getter(rec, data, name))

    return u'<t>'.join(column_values)


@telemetry.ZONE_FUNCTION
def GetPowerSlotSizeSymbol(recTypeID):
    fType = None
    for effect in dogma.data.get_type_effects(recTypeID):
        labelPath = slotTextByEffect.get(effect.effectID)
        if labelPath:
            fType = localization.GetByLabel(labelPath)
            break

    return fType


@telemetry.ZONE_FUNCTION
def GetItemQty(data, fmt = 'ln'):
    ret = getattr(data, 'qty_%s' % fmt, None)
    if ret is not None and ret[0] == data.item.stacksize:
        return ret[1]
    ret = ''
    if not (data.item.singleton or data.item.typeID in (const.typeBookmark,)):
        ret = FmtAmt(data.item.stacksize, fmt)
    setattr(data, 'qty_%s' % fmt, (data.item.stacksize, ret))
    return ret


NAMEABLE_GROUPS = (const.groupWreck,
 const.groupCargoContainer,
 const.groupSecureCargoContainer,
 const.groupAuditLogSecureContainer,
 const.groupFreightContainer,
 const.groupBiomass)

def IsValidNamedItem(invItem):
    if not invItem.singleton:
        return False
    elif invItem.categoryID == const.categoryShip:
        return True
    elif invItem.groupID in NAMEABLE_GROUPS:
        return True
    elif HasDeployComponent(invItem.typeID):
        return True
    else:
        return False


def PrimeEveLocationsBeforeGetItemName(invItems):
    itemIDsToPrime = {x.itemID for x in invItems if IsValidNamedItem(x)}
    if itemIDsToPrime:
        cfg.evelocations.Prime(itemIDsToPrime)


@telemetry.ZONE_FUNCTION
def GetItemName(invItem, data = None):
    if data and getattr(data, 'name', None):
        return data.name
    name = evetypes.GetName(invItem.typeID)
    if invItem.categoryID == const.categoryStation and invItem.groupID == const.groupStation:
        try:
            name = localization.GetByLabel('UI/Station/StationInSolarSystem', station=invItem.itemID, solarsystem=invItem.locationID)
        except KeyError:
            sys.exc_clear()

    elif IsValidNamedItem(invItem):
        locationName = cfg.evelocations.Get(invItem.itemID).name
        if locationName:
            name = locationName
    elif invItem.typeID == const.typeAssetSafetyWrap:
        name = sm.GetService('assetSafety').GetWrapName(invItem.itemID)
    elif invItem.categoryID == const.categoryStructure and invItem.singleton and IsSolarSystem(invItem.locationID):
        try:
            locationName = cfg.evelocations.Get(invItem.itemID).name
            if locationName:
                name = locationName
        except KeyError:
            pass

    if data:
        data.name = name
    if name is None:
        name = '%s %s' % (evetypes.GetName(invItem.typeID), invItem.itemID)
    return name


@telemetry.ZONE_FUNCTION
def GetCategoryGroupTypeStringForItem(invItem):
    try:
        return categoryGroupTypeStringForTypeID[invItem.typeID]
    except KeyError:
        try:
            retString = '%s %s %s' % (evetypes.GetCategoryNameByCategory(invItem.categoryID), evetypes.GetGroupNameByGroup(invItem.groupID), evetypes.GetName(invItem.typeID))
            categoryGroupTypeStringForTypeID[invItem.typeID] = retString
            return retString
        except (IndexError,
         TypeError,
         evetypes.CategoryNotFoundException,
         evetypes.GroupNotFoundException,
         evetypes.TypeNotFoundException):
            return GetFallbackCategoryGroupTypeStringForItem(invItem)


def GetFallbackCategoryGroupTypeStringForItem(invItem):
    if invItem is None:
        log.LogTraceback('None is not an invItem')
        sys.exc_clear()
        return 'Unknown Unknown Unknown'
    log.LogTraceback('InvalidItem Report')
    sys.exc_clear()
    log.LogError('--------------------------------------------------')
    log.LogError('Invalid Item Report')
    log.LogError('Item: ', invItem)
    reason = ''
    typeName = 'Unknown'
    groupName = 'Unknown'
    categoryName = 'Unknown'
    try:
        typeID = getattr(invItem, 'typeID', None)
    except IndexError:
        typeID = None
        sys.exc_clear()

    try:
        groupID = getattr(invItem, 'groupID', None)
    except IndexError:
        groupID = None
        sys.exc_clear()

    try:
        categoryID = getattr(invItem, 'categoryID', None)
    except IndexError:
        categoryID = None
        sys.exc_clear()

    if typeID is None:
        log.LogError('typeID is missing. Probably caused by a coding mistake.')
        reason += 'item attribute typeID is missing (Probably a coding mistake). '
    else:
        typeExists = evetypes.Exists(typeID)
        if not typeExists:
            log.LogError('THERE IS NO type info FOR typeID:', typeID)
            log.LogError('THE DATABASE REQUIRES CLEANUP FOR THIS TYPE')
            reason += 'The type %s no longer exists. Database requires cleanup. ' % typeID
    if groupID is None:
        log.LogError('groupID is missing. Probably caused by a coding mistake.')
        reason += 'item attribute groupID is missing (Probably a coding mistake?). '
        typeExists = evetypes.Exists(typeID)
        if typeExists:
            log.LogWarn('Extracting groupID from type')
            groupID = evetypes.GetGroupID(typeID)
    groupExists = evetypes.GroupExists(groupID)
    if groupID is not None:
        if not groupExists:
            log.LogError('THERE IS NO group info FOR groupID:', groupID)
            log.LogError('THE DATABASE REQUIRES CLEANUP FOR THIS GROUP')
            reason += 'The group %s no longer exists. Database requires cleanup. ' % groupID
    if categoryID is None:
        log.LogError('categoryID is missing. Probably caused by a coding mistake.')
        reason += 'item attribute categoryID is missing (Probably a coding mistake?). '
        if groupExists:
            log.LogWarn('Extracting categoryID from group')
            categoryID = evetypes.GetCategoryIDByGroup(groupID)
    if categoryID is not None:
        if not evetypes.CategoryExists(categoryID):
            log.LogError('THERE IS NO category info FOR categoryID:', categoryID)
            log.LogError('THE DATABASE REQUIRES CLEANUP FOR THIS CATEGORY')
            reason += 'The category %s no longer exists. Database requires cleanup. ' % categoryID
    if typeExists:
        typeName = evetypes.GetName(typeID)
    if groupExists:
        groupName = evetypes.GetGroupNameByGroup(groupID)
    if evetypes.CategoryExists(categoryID):
        categoryName = evetypes.GetCategoryNameByCategory(categoryID)
    log.LogError('--------------------------------------------------')
    eve.Message('CustomInfo', {'info': 'Invalid item detected:<br>Item:%s<br>CGT:%s %s %s<br>Reason: %s' % (invItem,
              categoryName,
              groupName,
              typeName,
              reason)})
    return '%s %s %s' % (categoryName, groupName, typeName)


def GetSlimItemName(slimItem):
    if slimItem.categoryID == const.categoryShip or HasNpcPilotComponent(slimItem.typeID):
        if not slimItem.charID or slimItem.charID == session.charid and slimItem.itemID != session.shipid:
            return evetypes.GetName(slimItem.typeID)
        if idCheckers.IsCharacter(slimItem.charID):
            return cfg.eveowners.Get(slimItem.charID).name
    else:
        if slimItem.groupID == const.groupHarvestableCloud:
            return localization.GetByLabel('UI/Inventory/SlimItemNames/SlimHarvestableCloud', cloudType=evetypes.GetName(slimItem.typeID))
        if slimItem.categoryID == const.categoryAsteroid:
            return localization.GetByLabel('UI/Inventory/SlimItemNames/SlimAsteroid', asteroidType=evetypes.GetName(slimItem.typeID))
        if slimItem.categoryID == const.categoryOrbital:
            return localization.GetByLabel('UI/Inventory/SlimItemNames/SlimOrbital', typeID=slimItem.typeID, planetID=slimItem.planetID, corpName=cfg.eveowners.Get(slimItem.ownerID).name)
        if slimItem.groupID == const.groupDisruptedGate:
            return localization.GetByLabel('UI/Inventory/SlimItemNames/SlimDisruptedGate', solarSystemID=slimItem.targetSolarSystemID)
    locationname = cfg.evelocations.Get(slimItem.itemID).name
    if locationname and locationname[0] != '@':
        if slimItem.groupID == const.groupBeacon:
            dungeonNameID = getattr(slimItem, 'dungeonNameID', None)
            if dungeonNameID:
                translatedName = localization.GetByMessageID(dungeonNameID)
                return translatedName
        return locationname
    else:
        return evetypes.GetName(slimItem.typeID)


def EditStationName(stationname, compact = 0, usename = 0):
    if compact:
        longForm = localization.GetByLabel('UI/Locations/LocationMoonLong') + ' '
        shortForm = localization.GetByLabel('UI/Locations/LocationMoonShort')
        stationname = stationname.replace(longForm, shortForm).replace(longForm.lower(), shortForm.lower())
    _stationname = stationname.split(' - ')
    if len(_stationname) >= 2 and usename:
        stationname = _stationname[-1]
    return stationname


def GetTextHeight(strng, width = 0, fontsize = fontconst.EVE_MEDIUM_FONTSIZE, linespace = None, hspace = 0, uppercase = 0, specialIndent = 0, getTextObj = 0, tabs = [], maxLines = None, fontStyle = None, bold = False, **kwds):
    return uicore.font.GetTextHeight(strng, width=width, font=None, fontStyle=fontStyle, fontsize=fontsize, linespace=linespace, letterspace=hspace, uppercase=uppercase, specialIndent=specialIndent, getTextObj=getTextObj, tabs=tabs, maxLines=maxLines, bold=bold)


def GetTextWidth(strng, fontsize = fontconst.EVE_MEDIUM_FONTSIZE, hspace = 0, uppercase = 0, fontStyle = None, bold = False):
    return uicore.font.GetTextWidth(strng, fontsize=fontsize, letterspace=hspace, uppercase=uppercase, fontStyle=fontStyle, bold=bold)


def GetStanding(standing, type = 0):
    if standing > 5:
        return localization.GetByLabel('UI/Standings/Excellent')
    elif standing > 0:
        return localization.GetByLabel('UI/Standings/Good')
    elif standing == 0:
        return localization.GetByLabel('UI/Standings/Neutral')
    elif standing < -5:
        return localization.GetByLabel('UI/Standings/Terrible')
    elif standing < 0:
        return localization.GetByLabel('UI/Standings/Bad')
    else:
        return localization.GetByLabel('UI/Standings/Unknown')


def GetMappedRankBase(rank, warFactionID, align):
    logo = Sprite(align=align)
    if rank < 0:
        logo.texture = None
    else:
        iconNum = '%s_%s' % (rank / 4 + 1, rank % 4 + 1)
        MapLogo(iconNum, logo, root='res:/UI/Texture/Medals/Ranks/%s_' % warFactionID)
    if align != uiconst.TOALL:
        logo.width = logo.height = 128
    else:
        logo.width = logo.height = 0
    return logo


def GetRankSprite(rank, warFactionID, align):
    texturePath = _GetRankTexturePath(rank, warFactionID)
    if align != uiconst.TOALL:
        size = 128
    else:
        size = 0
    logo = Sprite(name='rankSprite', align=align, pos=(0,
     0,
     size,
     size), texturePath=texturePath)
    return logo


def _GetRankTexturePath(rank, warFactionID):
    if rank < 0:
        return None
    texturePath = 'res:/UI/Texture/Medals/Ranks/%s_%s.png' % (warFactionID, rank)
    return texturePath


def MapLogo(iconNum, sprite, root = 'res:/UI/Texture/Corps/corps'):
    texpix, num = iconNum.split('_')
    while texpix.find('0') == 0:
        texpix = texpix[1:]

    sprite.texturePath = '%s%s%s.dds' % (root, ['', '0'][int(texpix) < 10], texpix)
    num = int(num)
    sprite.rectWidth = sprite.rectHeight = 128
    sprite.rectLeft = [0, 128][num in (2, 4)]
    sprite.rectTop = [0, 128][num > 2]


def GetTechLevelIconPathAndHint(typeID = None):
    icon = None
    hint = None
    if typeID is None:
        return (icon, hint)
    try:
        if evetypes.GetCategoryID(typeID) in (const.categoryBlueprint, const.categoryAncientRelic):
            ptID = cfg.blueprints.Get(typeID).productTypeID
            if ptID is not None:
                typeID = ptID
    except Exception:
        pass

    metaGroupID = evetypes.GetMetaGroupID(typeID)
    if metaGroupID:
        icon = GetIconFile(metaGroups.get_icon_id(metaGroupID))
        hint = metaGroups.get_name(metaGroupID)
    return (icon, hint)


def GetTechLevelColor(typeID = None):
    if typeID is None:
        return
    metaGroupID = evetypes.GetMetaGroupID(typeID)
    return metaGroups.get_color(metaGroupID)


def GetTechLevelIcon(tlicon = None, offset = 0, typeID = None):
    icon, hint = GetTechLevelIconPathAndHint(typeID)
    if icon:
        if tlicon is None:
            tlicon = Icon(icon=icon, parent=None, width=16, height=16, align=uiconst.TOPLEFT, idx=0, hint=hint)
        else:
            MapIcon(tlicon, icon)
            tlicon.hint = hint
        if offset:
            tlicon.top = offset
        tlicon.state = uiconst.UI_NORMAL
    elif tlicon:
        tlicon.state = uiconst.UI_HIDDEN
    return tlicon


def GetBallparkRecord(itemID):
    bp = sm.GetService('michelle').GetBallpark()
    if bp and hasattr(bp, 'GetInvItem'):
        return bp.GetInvItem(itemID)
    else:
        return None


def Close(owner, wndNames):
    for each in wndNames:
        if getattr(owner, each, None):
            wnd = getattr(owner, each, None)
            setattr(owner, each, None)
            if not wnd.destroyed:
                wnd.Close()


def GetContainerHeader(caption, where, bothlines = 1, padHorizontal = 0, padTop = 0):
    container = ContainerAutoSize(name='headercontainer', parent=where, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padding=(padHorizontal,
     padTop,
     padHorizontal,
     2))
    FillThemeColored(bgParent=container, colorType=uiconst.COLORTYPE_UIHILIGHT, align=uiconst.TOALL, opacity=0.15)
    t = eveLabel.EveLabelLarge(text=caption, name='header1', parent=container, padding=(8, 4, 8, 4), align=uiconst.TOTOP)
    return container


def ListWnd(lst, listtype = None, caption = None, hint = None, ordered = 0, minw = 200, minh = 256, minChoices = 1, maxChoices = 1, initChoices = [], validator = None, isModal = 1, scrollHeaders = [], iconMargin = 0, windowName = 'listwindow', lstDataIsGrouped = 0, unstackable = 0, noContentHint = None):
    from eve.client.script.ui.control.listwindow import ListWindow
    return ListWindow.ShowList(lst, listtype, caption, hint, ordered, minw, minh, minChoices, maxChoices, initChoices, validator, isModal, scrollHeaders, iconMargin, windowName, lstDataIsGrouped, unstackable, noContentHint)


def HybridWnd(format, caption, windowID, modal = 1, buttons = None, location = None, minW = 256, minH = 256, blockconfirm = 0, icon = None, unresizeAble = 0, ignoreCurrent = 1):
    if windowID is None:
        raise ValueError('Created Hybrid window without a windowID', caption)
    else:
        wnd = Window.GetIfOpen(windowID=windowID)
        if wnd:
            return
    if buttons is None:
        buttons = uiconst.OK
    from eve.client.script.ui.control.hybridWindow import HybridWindow
    wnd = HybridWindow.Open(ignoreCurrent=ignoreCurrent, format=format, caption=caption, modal=modal, windowID=windowID, buttons=buttons, location=location, minW=minW, minH=minH, icon=icon, blockconfirm=blockconfirm)
    wnd.MakeUnstackable()
    if unresizeAble:
        wnd.MakeUnResizeable()
    import uthread
    uthread.new(wnd.OnScale_)
    if modal == 1:
        if wnd.ShowModal() == uiconst.ID_OK:
            return wnd.result
        else:
            return
    return wnd


def GetDialogIconTexturePath(icon):
    if isinstance(icon, (types.StringType, eveicon.IconData)):
        return icon
    else:
        mapping = {uiconst.INFO: 'res:/ui/Texture/WindowIcons/info.png',
         uiconst.WARNING: 'res:/ui/Texture/WindowIcons/warning.png',
         uiconst.QUESTION: 'res:/ui/Texture/WindowIcons/question.png',
         uiconst.ERROR: 'res:/ui/Texture/WindowIcons/stop.png',
         uiconst.FATAL: 'res:/UI/Texture/WindowICons/criminal.png'}
        return mapping.get(icon, 'res:/ui/Texture/WindowIcons/warning.png')


def TextBox(header, txt, modal = 0, windowID = 'generictextbox2', tabs = [], preformatted = 0, scrolltotop = 1):
    wnd = Window.GetIfOpen(windowID=windowID)
    if wnd is None or wnd.destroyed or uicore.uilib.Key(uiconst.VK_SHIFT):
        format = [{'type': 'textedit',
          'readonly': 1,
          'label': '_hide',
          'key': 'text'}]
        wnd = HybridWnd(format, header, windowID, modal, buttons=uiconst.CLOSE, location=None, minW=256, minH=128)
        if wnd:
            wnd.form.align = uiconst.TOALL
            wnd.form.left = wnd.form.width = 3
            wnd.form.top = -2
            wnd.form.height = 6
            wnd.form.sr.text.parent.align = uiconst.TOALL
            wnd.form.sr.text.parent.left = wnd.form.sr.text.parent.top = wnd.form.sr.text.parent.width = wnd.form.sr.text.parent.height = 0
            wnd.form.sr.text.parent.children[0].height = 0
            wnd.form.sr.text.autoScrollToBottom = 0
    if wnd is not None:
        i = 1
        for t in tabs:
            setattr(wnd.form.sr.text.content.control, 'tabstop%s' % i, t)
            i = i + 1

        wnd.form.sr.text.SetValue(txt, scrolltotop=scrolltotop, preformatted=preformatted)
        if wnd.state == uiconst.UI_NORMAL:
            wnd.SetOrder(0)
        else:
            wnd.Maximize()


def QtyPopup(maxvalue = None, minvalue = 0, setvalue = '', hint = None, caption = None, label = '', digits = 0):
    if caption is None:
        caption = localization.GetByLabel('UI/Common/SetQuantity')
    if maxvalue is not None and hint is None:
        hint = localization.GetByLabel('UI/Common/SetQtyBetween', min=FmtAmt(minvalue), max=FmtAmt(maxvalue))
        if setvalue == 0:
            setvalue = maxvalue
    maxvalue = maxvalue or min(maxvalue, sys.maxint)
    format = []
    if hint is not None:
        format += [{'type': 'text',
          'text': hint,
          'frame': 0}]
    if label is not None:
        format += [{'type': 'labeltext',
          'label': label,
          'text': '',
          'frame': 0,
          'labelwidth': 240}]
    if digits:
        format += [{'type': 'edit',
          'setvalue': setvalue,
          'floatonly': [minvalue, maxvalue, digits],
          'key': 'qty',
          'label': '_hide',
          'required': 1,
          'frame': 0,
          'setfocus': 1,
          'selectall': 1}]
    else:
        format += [{'type': 'edit',
          'setvalue': setvalue,
          'intonly': [minvalue, maxvalue],
          'key': 'qty',
          'label': '_hide',
          'required': 1,
          'frame': 0,
          'setfocus': 1,
          'selectall': 1}]
    return HybridWnd(format, caption, windowID='setQuantityPopup', modal=1, buttons=uiconst.OKCANCEL, location=None, minW=300, minH=120)


@caching.Memoize
def GetInvItemDefaultHiddenHeaders():
    return [localization.GetByLabel('UI/Inventory/ItemMetaLevel'), localization.GetByLabel('UI/Inventory/ItemTechLevel'), localization.GetByLabel('UI/Inventory/ItemCategory')]


@telemetry.ZONE_FUNCTION
@caching.Memoize
def GetInvItemDefaultHeaders():
    return [localization.GetByLabel('UI/Common/Name'),
     localization.GetByLabel('UI/Common/Quantity'),
     localization.GetByLabel('UI/Inventory/ItemGroup'),
     localization.GetByLabel('UI/Inventory/ItemCategory'),
     localization.GetByLabel('UI/Inventory/ItemSize'),
     localization.GetByLabel('UI/Inventory/ItemSlot'),
     localization.GetByLabel('UI/Inventory/ItemVolume'),
     localization.GetByLabel('UI/Inventory/ItemMetaLevel'),
     localization.GetByLabel('UI/Inventory/ItemTechLevel'),
     localization.GetByLabel('UI/Contracts/ContractsWindow/EstPrice')]


@telemetry.ZONE_FUNCTION
def GetVisibleItemHeaders(scrollID):
    key = GetHiddenColumnsKey(scrollID)
    defaultHeaders = GetInvItemDefaultHeaders()
    hiddenColumns = settings.user.ui.Get('filteredColumns_%s' % uiconst.SCROLLVERSION, {}).get(key, [])
    allHiddenColumns = hiddenColumns + settings.user.ui.Get('filteredColumnsByDefault_%s' % uiconst.SCROLLVERSION, {}).get((key, session.languageID), [])
    filterColumns = filter(lambda x: x not in allHiddenColumns, defaultHeaders)
    return filterColumns


def GetLightYearDistance(fromSystem, toSystem, fraction = True):
    for system in (fromSystem, toSystem):
        if type(system) not in (types.IntType, types.InstanceType, types.LongType):
            return None
        if not IsKnownSpaceSystem(system):
            return None

    def GetLoc(system):
        if type(system) in (types.IntType, types.LongType):
            return cfg.evelocations.Get(system)
        if type(system) == types.InstanceType:
            return system

    fromSystem = GetLoc(fromSystem)
    toSystem = GetLoc(toSystem)
    dist = math.sqrt((toSystem.x - fromSystem.x) ** 2 + (toSystem.y - fromSystem.y) ** 2 + (toSystem.z - fromSystem.z) ** 2) / const.LIGHTYEAR
    if fraction:
        dist = float(int(dist * 10)) / 10
    return dist


def HideButtonFromGroup(btns, label, button = None):
    if label:
        btn = btns.FindChild('%s_Btn' % label)
        if btn:
            btn.state = uiconst.UI_HIDDEN
    if button:
        btn.state = uiconst.UI_HIDDEN


def ShowButtonFromGroup(btns, label, button = None):
    if label:
        btn = btns.FindChild('%s_Btn' % label)
        if btn:
            btn.state = uiconst.UI_NORMAL
    if button:
        btn.state = uiconst.UI_NORMAL


def FormatMedalData(data):
    from eve.client.script.ui.shared.medalribbonranks import Ribbon
    from eve.client.script.ui.shared.medalribbonranks import Medal
    fdata = []
    for part in (1, 2):
        dpart = {1: Ribbon,
         2: Medal}.get(part, None)
        pdata = []
        for row in data.Filter('part').get(part):
            label, icon = row.graphic.split('.')
            color = row.color
            pdata.append((label, icon, color))

        fdata.append([dpart, pdata])

    return fdata


def GetFullscreenProjectionViewAndViewport():
    viewport = trinity.device.viewport
    camera = sm.GetService('sceneManager').GetActiveCamera()
    return (camera.projectionMatrix, camera.viewMatrix, viewport)


def GetOwnerLogo(parent, ownerID, size = 64, noServerCall = False):
    if idCheckers.IsCharacter(ownerID):
        logo = Icon(icon=None, parent=parent, pos=(0,
         0,
         size,
         size), ignoreSize=True)
        if size < 64:
            fetchSize = 64
        else:
            fetchSize = size
        sm.GetService('photo').GetPortrait(ownerID, fetchSize, logo)
    elif idCheckers.IsCorporation(ownerID) or idCheckers.IsAlliance(ownerID) or idCheckers.IsFaction(ownerID):
        GetLogoIcon(itemID=ownerID, parent=parent, pos=(0,
         0,
         size,
         size), ignoreSize=True)
    else:
        raise RuntimeError('ownerID %d is not of an owner type!!' % ownerID)
