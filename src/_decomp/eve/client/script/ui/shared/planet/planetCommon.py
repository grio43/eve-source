#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\planetCommon.py
import math
import blue
import evetypes
import localization
import log
import trinity
import utillib
from carbon.common.script.util.format import FmtTime
from carbonui.uicore import uicore
from carbonui.util.color import Color
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui.camera import cameraUtil
from eve.common.lib import appConst
from eve.common.script.planet.surfacePoint import SurfacePoint
from eve.common.script.util import planetCommon
from eve.common.script.util.eveFormat import FmtISKAndRound
from fsdBuiltData.common.planet import get_schematic, get_schematic_ids_for_pin_type_id, get_schematic_info_for_type_id, get_schematic_name, get_schematic_types
from inventorycommon import typeHelpers
from localization import GetByLabel
PLANET_SCALE = 1000.0
PLANET_TEXTURE_SIZE = 2048
PLANET_RESOURCE_TEX_WIDTH = 2048
PLANET_RESOURCE_TEX_HEIGHT = 1024
PLANET_HEATMAP_COLORS = ((0, 0, 0.5, 0.5),
 (0, 0, 1, 1),
 (0, 0.5, 1, 1),
 (0, 1, 1, 1),
 (0, 1, 0.5, 1),
 (0, 1, 0, 1),
 (0.5, 1, 0, 1),
 (1, 1, 0, 1),
 (1, 0.5, 0, 1),
 (1, 0, 0, 1))
PANEL_STATS = 1
PANEL_LINKS = 2
PANEL_DECOMMISSION = 3
PANEL_STORAGE = 4
PANEL_INCOMING = 5
PANEL_OUTGOING = 6
PANEL_LAUNCH = 7
PANEL_PRODUCTS = 8
PANEL_SURVEYFORDEPOSITS = 9
PANEL_SCHEMATICS = 10
PANEL_UPGRADELINK = 11
PANEL_UPGRADE = 12
PANEL_ROUTES = 13
PANEL_CREATEROUTE = 14
PANEL_TRANSFER = 15
PANELDATA = {PANEL_STATS: ('res:/UI/Texture/Icons/44_32_24.png', 'UI/PI/Common/Stats'),
 PANEL_LINKS: ('res:/UI/Texture/Icons/77_32_31.png', 'UI/PI/Common/Links'),
 PANEL_DECOMMISSION: ('res:/UI/Texture/Icons/77_32_22.png', 'UI/PI/Common/Decommission'),
 PANEL_STORAGE: ('res:/UI/Texture/Icons/77_32_18.png', 'UI/PI/Common/Storage'),
 PANEL_INCOMING: ('res:/UI/Texture/Icons/77_32_21.png', 'UI/PI/Common/Incoming'),
 PANEL_OUTGOING: ('res:/UI/Texture/Icons/77_32_20.png', 'UI/PI/Common/Outgoing'),
 PANEL_LAUNCH: ('res:/UI/Texture/Icons/77_32_19.png', 'UI/PI/Common/Launch'),
 PANEL_PRODUCTS: ('res:/UI/Texture/Icons/77_32_24.png', 'UI/PI/Common/Products'),
 PANEL_SURVEYFORDEPOSITS: ('res:/UI/Texture/Icons/77_32_23.png', 'UI/PI/Common/InstallExtractionProgram'),
 PANEL_SCHEMATICS: ('res:/UI/Texture/Icons/77_32_17.png', 'UI/PI/Common/Schematics'),
 PANEL_UPGRADELINK: ('res:/UI/Texture/Icons/77_32_36.png', 'UI/PI/Common/UpgradeLink'),
 PANEL_UPGRADE: ('res:/UI/Texture/Icons/77_32_37.png', 'UI/PI/Common/Upgrade'),
 PANEL_ROUTES: ('res:/UI/Texture/Icons/77_32_32.png', 'UI/PI/Common/Routes'),
 PANEL_CREATEROUTE: ('', 'UI/PI/Common/CreateRoute'),
 PANEL_TRANSFER: ('', 'UI/PI/Common/SelectTransferDestination')}
PANEL_MIN_MAX_HEIGHT = {PANEL_STATS: (100, 200),
 PANEL_LINKS: (200, None),
 PANEL_DECOMMISSION: (100, 150),
 PANEL_STORAGE: (200, None),
 PANEL_INCOMING: (200, None),
 PANEL_OUTGOING: (200, None),
 PANEL_LAUNCH: (300, None),
 PANEL_PRODUCTS: (200, None),
 PANEL_SURVEYFORDEPOSITS: (200, None),
 PANEL_SCHEMATICS: (300, None),
 PANEL_UPGRADELINK: (250, None),
 PANEL_UPGRADE: (180, 180),
 PANEL_ROUTES: (200, None),
 PANEL_CREATEROUTE: (155, 155),
 PANEL_TRANSFER: (30, 30)}
PLANET_COLOR_POWER = (236 / 255.0, 28 / 255.0, 36 / 255.0)
PLANET_COLOR_CPU = (0.0, 255 / 255.0, 212 / 255.0)
PLANET_COLOR_CYCLE = (1.0, 1.0, 1.0)
PLANET_COLOR_BANDWIDTH = (1.0, 1.0, 1.0)
PLANET_COLOR_LINKEDITMODE = (255 / 255.0,
 205 / 255.0,
 0.0,
 1.0)
PLANET_COLOR_PINEDITMODE = (255 / 255.0, 205 / 255.0, 0.0)
PLANET_COLOR_STORAGE = (10 / 255.0,
 67 / 255.0,
 102 / 255.0,
 1.0)
PLANET_COLOR_EXTRACTOR = (0 / 255.0,
 153 / 255.0,
 153 / 255.0,
 1.0)
PLANET_COLOR_PROCESSOR = (178 / 255.0,
 98 / 255.0,
 45 / 255.0,
 1.0)
PLANET_COLOR_PROCESSOR_ADVANCED = (0.929, 0.859, 0.207, 1.0)
PLANET_COLOR_PROCESSOR_HIGHTECH = (0.739, 0.929, 0.207, 1.0)
PLANET_COLOR_CURRLEVEL = (0.247, 0.745, 0.165, 1.0)
PLANET_COLOR_UPGRADELEVEL = (0.271, 0.494, 0.137, 1.0)
PLANET_COLOR_POWERUPGRADE = (0.671, 0.047, 0.071, 1.0)
PLANET_COLOR_CPUUPGRADE = (0.278, 0.655, 0.592, 1.0)
PLANET_COLOR_EXTRACTIONLINK = (0.4, 1.0, 1.0, 1.0)
PLANET_COLOR_USED_STORAGE = (0 / 255.0, 169 / 255.0, 244 / 255.0)
PLANET_COLOR_USED_PROCESSOR = (237 / 255.0, 153 / 255.0, 53 / 255.0)
PLANET_COLOR_NEEDSATTENTION = (1.0, 0.0, 0.0, 1.0)
PLANET_COLOR_ICON_COMMANDCENTER = (171 / 255.0, 243 / 255.0, 255 / 255.0)
PLANET_COLOR_ICON_STORAGE = (2 / 255.0, 106 / 255.0, 147 / 255.0)
PLANET_COLOR_ICON_SPACEPORT = (3 / 255.0, 178 / 255.0, 239 / 255.0)
PLANET_COLOR_ICON_EXTRACTOR = (48 / 255.0, 239 / 255.0, 216 / 255.0)
PLANET_COLOR_ICON_PROCESSOR = (237 / 255.0, 153 / 255.0, 53 / 255.0)
PLANET_COLOR_ICON_PROCESSOR_ADVANCED = (0.929, 0.859, 0.207, 1.0)
PLANET_COLOR_ICON_PROCESSOR_HIGHTECH = (0.739, 0.929, 0.207, 1.0)
PINTYPE_NOPICK = 0
PINTYPE_NORMAL = 1
PINTYPE_NORMALEDIT = 2
PINTYPE_EXTRACTIONHEAD = 3
PINTYPE_OTHERS = 4
PINTYPE_DEPLETION = 5
PLANET_2PI = math.pi * 2
PLANET_PI_DIV_2 = math.pi / 2
PLANET_COMMANDCENTERMAXLEVEL = 5
DARKPLANETS = (appConst.typePlanetPlasma, appConst.typePlanetLava, appConst.typePlanetSandstorm)

def GetContrastColorForCurrPlanet():
    if not sm.GetService('viewState').IsViewActive('planet'):
        return None
    else:
        planetTypeID = sm.GetService('planetUI').planet.planetTypeID
        if planetTypeID in DARKPLANETS:
            return Color.WHITE
        return Color.BLACK


def GetPickIntersectionPoint(x = None, y = None, scale = 1.0):
    if None in (x, y):
        x, y = int(uicore.uilib.x * uicore.desktop.dpiScaling), int(uicore.uilib.y * uicore.desktop.dpiScaling)
    device = trinity.device
    proj, view, vp = cameraUtil.GetFullscreenProjectionViewAndViewport()
    ray, start = device.GetPickRayFromViewport(x, y, vp, view.transform, proj.transform)
    lineVec = trinity.TriVector(*ray)
    lineP0 = trinity.TriVector(*start)
    sphereP0 = trinity.TriVector(0.0, 0.0, 0.0)
    sphereRad = 1000.0 * scale
    pInt = GetSphereLineIntersectionPoint(lineP0, lineVec, sphereP0, sphereRad)
    if not pInt:
        return
    ret = SurfacePoint(pInt.x, pInt.y, pInt.z)
    ret.SetRadius(1.0)
    return ret


def GetSphereLineIntersectionPoint(lineP0, lineVec, sphereP0, sphereRad):
    a = 1
    b = (lineVec * 2).DotProduct(lineP0 - sphereP0)
    c = (lineP0 - sphereP0).Length() ** 2 - sphereRad ** 2
    d = b ** 2.0 - 4.0 * a * c
    if d < 0:
        return None
    elif d == 0:
        t = -b / (2 * a)
        return lineP0 + lineVec * t / lineVec.Length()
    d = math.sqrt(d)
    t1 = (-b + d) / (2 * a)
    t2 = (-b - d) / (2 * a)
    lineLength = lineVec.Length()
    P1 = lineP0 + lineVec * t1 / lineLength
    P2 = lineP0 + lineVec * t2 / lineLength
    l1 = (lineP0 - P1).LengthSq()
    l2 = (lineP0 - P2).LengthSq()
    if l1 < l2:
        return P1
    else:
        return P2


def NormalizeLatitude(angle):
    while angle < -PLANET_PI_DIV_2:
        angle += math.pi

    while angle > PLANET_PI_DIV_2:
        angle -= math.pi

    return angle


def NormalizeLongitude(angle):
    while angle <= -math.pi:
        angle += PLANET_2PI

    while angle > math.pi:
        angle -= PLANET_2PI

    return angle


def FmtGeoCoordinates(latitude, longitude):
    latitude = math.degrees(NormalizeLatitude(latitude))
    longitude = math.degrees(NormalizeLongitude(longitude))
    d1, m1, s1 = ConvertToDMS(latitude)
    d2, m2, s2 = ConvertToDMS(longitude)
    dir1 = 'N' if d1 >= 0 else 'S'
    dir2 = 'E' if d2 >= 0 else 'W'
    return "%d %d' %d'' %s, %d %d' %d'' %s" % (d1,
     m1,
     s1,
     dir1,
     d2,
     m2,
     s2,
     dir2)


def ConvertToDMS(value):
    degrees = int(value)
    minPart = abs(value - degrees)
    secPart = minPart - int(minPart)
    return (degrees, int(minPart * 60), int(round(secPart * 60)))


def GetPinCycleInfo(pin, cycleTime = None):
    if cycleTime is None:
        cycleTime = pin.GetCycleTime()
    if pin.IsActive() and not pin.IsInEditMode():
        currCycle = min(blue.os.GetWallclockTime() - pin.lastRunTime, cycleTime)
        currCycleProportion = currCycle / float(cycleTime)
    else:
        currCycle = currCycleProportion = 0
    if cycleTime is None:
        cycleText = localization.GetByLabel('UI/PI/Common/InactivePin')
    else:
        cycleText = '%s / %s' % (FmtTime(currCycle), FmtTime(cycleTime))
    return (cycleText, currCycleProportion)


def GetSchematicData(processorTypeID):
    schematicsIDs = get_schematic_ids_for_pin_type_id(processorTypeID)
    if len(schematicsIDs) == 0:
        log.LogTraceback('Authoring error: No schematics found for processor pin with typeID %s' % processorTypeID)
    schematics = []
    for schematicID in schematicsIDs:
        sData = GetSchematicDataForID(schematicID)
        schematics.append((sData.name, sData))

    return SortListOfTuples(schematics)


def GetSchematicDataForID(schematicID):
    schematic = get_schematic(schematicID)
    if not schematic:
        log.LogTraceback('Authoring error: No schematic found with id=%s' % schematicID)
        raise KeyError('RecordNotFound', schematicID)
    inputs, outputs = GetSchematicInputsAndOutputs(schematicID, schematic)
    outputsDict = {}
    for o in outputs:
        outputsDict[o.typeID] = o.quantity

    volumePerCycle = planetCommon.GetCommodityTotalVolume(outputsDict)
    volumePerHour = planetCommon.GetBandwidth(volumePerCycle, schematic.cycleTime * appConst.SEC)
    sData = utillib.KeyVal(name=get_schematic_name(schematicID, schematic), schematicID=schematicID, cycleTime=schematic.cycleTime, outputs=outputs, inputs=inputs, outputVolume=volumePerHour)
    return sData


def GetSchematicInputsAndOutputs(schematicID, schematic):
    inputs = []
    outputs = []
    if not schematic.types:
        log.LogTraceback('Authoring error: No inputs/outputs defined for schematic with id=%s' % schematicID)
    for typeID, typeInfo in schematic.types.iteritems():
        data = utillib.KeyVal(name=evetypes.GetName(typeID), typeID=typeID, quantity=typeInfo.quantity)
        if typeInfo.isInput:
            inputs.append(data)
        else:
            outputs.append(data)

    return (inputs, outputs)


def GetSchematicOutput(schematicID):
    for typeID, typeInfo in get_schematic_types(schematicID).iteritems():
        if not typeInfo.isInput:
            return typeID


def GetSchematicByOutput(typeID):
    for schematicID, isInput in get_schematic_info_for_type_id(typeID):
        if not isInput:
            return schematicID


def GetSchematicDataByGroupID():
    schematics = GetSchematicData()
    ret = {}
    for schematic in schematics:
        groupID = evetypes.GetGroupID(schematic.output.typeID)
        if groupID not in ret:
            ret[groupID] = []
        ret[groupID].append(schematic)

    return ret


def PinHasBeenBuilt(pinID):
    if isinstance(pinID, tuple):
        return False
    return True


def _AddSchematicIconAndLabel(item, tooltipPanel):
    label = localization.GetByLabel('UI/PI/Common/ItemAmount', amount=int(item.quantity), itemName=GetProductNameAndTier(item.typeID))
    icon = typeHelpers.GetIconFile(item.typeID)
    tooltipPanel.AddIconLabel(icon=icon, label=label, iconSize=28)


def LoadSchematicTooltipPanel(tooltipPanel, schematic):
    tooltipPanel.LoadGeneric2ColumnTemplate()
    tooltipPanel.AddLabelMedium(text=localization.GetByLabel('UI/PI/Common/SchematicInput'), bold=True, colSpan=2, cellPadding=(0, 0, 0, 2))
    for i, item in enumerate(schematic.inputs):
        _AddSchematicIconAndLabel(item, tooltipPanel)

    tooltipPanel.AddLabelMedium(text=localization.GetByLabel('UI/PI/Common/OutputProduct'), bold=True, colSpan=2, cellPadding=(0, 10, 0, 2))
    _AddSchematicIconAndLabel(schematic.outputs[0], tooltipPanel)
    text = GetSchematicCycleTimeText(schematic)
    tooltipPanel.AddLabelMedium(colSpan=2, cellPadding=(0, 10, 0, 0), text=text)
    text = GetSchematicOutputVolumeText(schematic)
    tooltipPanel.AddLabelMedium(colSpan=2, cellPadding=(0, 4, 0, 2), text=text)


def GetSchematicCycleTimeText(schematic):
    return '%s: <b>%s</b>' % (localization.GetByLabel('UI/PI/Common/CycleTime'), localization.GetByLabel('UI/PI/Common/TimeHourMinSec', time=schematic.cycleTime * appConst.SEC))


def GetSchematicOutputVolumeText(schematic):
    return '%s: <b>%s</b>' % (localization.GetByLabel('UI/PI/Common/OutputPerHour'), localization.GetByLabel('UI/PI/Common/CapacityAmount', amount=schematic.outputVolume))


def _AddProductIconAndLabel(typeID, tooltipPanel):
    label = GetProductNameAndTier(typeID)
    icon = typeHelpers.GetIconFile(typeID)
    tooltipPanel.AddIconLabel(icon=icon, label=label, iconSize=28, padBottom=2)


def LoadProductTooltipPanel(tooltipPanel, typeID, amount = None):
    tooltipPanel.LoadGeneric2ColumnTemplate()
    text = GetProductNameAndTier(typeID)
    if amount:
        text = GetByLabel('UI/PI/Common/ItemAmount', amount=int(amount), itemName=text)
    tooltipPanel.AddLabelLarge(colSpan=2, text=text)
    _CheckAddEstPrice(amount, tooltipPanel, typeID)
    _AddRequiredforItems(tooltipPanel, typeID)


def _AddRequiredforItems(tooltipPanel, typeID):
    typeIDs = GetRequiredForItems(typeID)
    if not typeIDs:
        return
    tooltipPanel.AddLabelMedium(colSpan=2, cellPadding=(0, 10, 0, 2), text=GetByLabel('UI/InfoWindow/TabNames/RequiredFor'))
    for typeID in typeIDs:
        _AddProductIconAndLabel(typeID, tooltipPanel)


def _CheckAddEstPrice(amount, tooltipPanel, typeID):
    if amount:
        price = typeHelpers.GetAveragePrice(typeID) or 0.0
        if price is not None:
            text = GetByLabel('UI/Inventory/EstIskPrice', iskString=FmtISKAndRound(price * amount, False))
            tooltipPanel.AddLabelMedium(text=text, colSpan=2, cellPadding=(0, 10, 0, 2))


def GetRequiredForItems(typeID):
    requiredFor = []
    for schematicID, isInput in get_schematic_info_for_type_id(typeID):
        if isInput:
            requiredFor.append(GetSchematicOutput(schematicID))

    return requiredFor


def GetTierByTypeID(typeID):
    categoryID = evetypes.GetCategoryID(typeID)
    if categoryID == appConst.categoryPlanetaryResources:
        return 0
    groupID = evetypes.GetGroupID(typeID)
    if groupID == appConst.groupBasicCommodities:
        return 1
    if groupID == appConst.groupRefinedCommodities:
        return 2
    if groupID == appConst.groupSpecializedCommodities:
        return 3
    if groupID == appConst.groupAdvancedCommodities:
        return 4


def GetTierNameByTypeID(typeID):
    tier = GetTierByTypeID(typeID)
    if tier == 0:
        return GetByLabel('UI/PI/Common/TierRawResource')
    else:
        return GetByLabel('UI/PI/Common/TierX', tier=tier)


def GetProductNameAndTier(typeID):
    return GetByLabel('UI/PI/Common/ProductNameAndTier', name=evetypes.GetName(typeID), tier=GetTierNameByTypeID(typeID))
