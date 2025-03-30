#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\ledger\ledgerUtil.py
import collections
import blue
from collections import defaultdict
import evetypes
import gametime
from carbonui.util.color import Color
from eveservices.ledger import GetLedgerService
import inventorycommon.const as invConst
from localization import GetByLabel
NUM_DAYS_BACK = 90
REST_ORE = -1
SCROLL_HEADERS_PERSONAL = [GetByLabel('UI/Ledger/TimestampHeader'),
 GetByLabel('UI/Ledger/OreTypeHeader'),
 GetByLabel('UI/Ledger/OreQtyHeader'),
 GetByLabel('UI/Ledger/OreWasteHeader'),
 GetByLabel('UI/Common/Volume'),
 GetByLabel('UI/Ledger/VolumeWastedHeader'),
 GetByLabel('UI/Inventory/EstPrice'),
 GetByLabel('UI/Ledger/WastedPriceHeader'),
 GetByLabel('UI/Ledger/SolarSystemHeader')]
SCROLL_HEADERS_CORP = [GetByLabel('UI/Ledger/TimestampHeader'),
 GetByLabel('UI/Ledger/CorpNameHeader'),
 GetByLabel('UI/Ledger/PilotHeader'),
 GetByLabel('UI/Ledger/OreTypeHeader'),
 GetByLabel('UI/Ledger/OreQtyHeader'),
 GetByLabel('UI/Common/Volume'),
 GetByLabel('UI/Inventory/EstPrice')]
MOON_ORE_GROUPS = [invConst.groupUbiquitousMoonAsteroids,
 invConst.groupCommonMoonAsteroids,
 invConst.groupUncommonMoonAsteroids,
 invConst.groupRareMoonAsteroids,
 invConst.groupExceptionalMoonAsteroids]
DEFAULT_COLOR = (0.5, 0.5, 0.5, 1.0)

class OreInfoHelper(object):

    def __init__(self):
        self.metaLevelByOreTypeID = None
        self.basicOreTypeByOreTypeID = None
        self.moonBasicTypeIDs = None
        self.colorsByMoonOreTypeID = None

    def GetBasicOreForTypeID(self, typeID):
        if self.basicOreTypeByOreTypeID is None:
            self.basicOreTypeByOreTypeID = {}
            for eachTypeID in evetypes.GetTypeIDsByCategory(const.categoryAsteroid):
                basicOre = sm.GetService('clientDogmaStaticSvc').GetTypeAttribute(eachTypeID, 2711, None)
                if basicOre:
                    self.basicOreTypeByOreTypeID[eachTypeID] = int(basicOre)

        return self.basicOreTypeByOreTypeID.get(typeID, None)

    def GetMetaLevelByTypeID(self, typeID):
        if self.metaLevelByOreTypeID is None:
            self.metaLevelByOreTypeID = {}
            for eachTypeID in evetypes.GetTypeIDsByCategory(const.categoryAsteroid):
                metaLevel = sm.GetService('clientDogmaStaticSvc').GetTypeAttribute(eachTypeID, 2699, None)
                if metaLevel is not None:
                    self.metaLevelByOreTypeID[eachTypeID] = int(metaLevel)

        return self.metaLevelByOreTypeID.get(typeID, 1)


oreInfoHelper = OreInfoHelper()

def GetBasicOreForTypeID(typeID):
    return oreInfoHelper.GetBasicOreForTypeID(typeID)


def GetMetaLevelByTypeID(typeID):
    return oreInfoHelper.GetMetaLevelByTypeID(typeID)


def GetMiniMapRange():
    now = gametime.GetWallclockTime()
    endTime = GetMaxDayTimeStamp(now)
    startTime = endTime - NUM_DAYS_BACK * const.DAY
    startTime = GetMinDayTimeStamp(startTime)
    return (startTime, endTime)


def GetDataForPersonaMinimap():
    data, _ = GetLedgerService().GetPersonalData()
    return GetDataForMinimap(data)


def GetDataForCorpMinimap(structureID):
    data = GetLedgerService().GetCorpData(structureID)
    return GetDataForMinimap(data)


def GetDataForMinimap(data):
    now = gametime.GetWallclockTime()
    minedByDay = defaultdict(int)
    for each in data:
        year, month, wd, day, hour, min, sec, ms = blue.os.GetTimeParts(each.eventDate)
        timeTuple = (year, month, day)
        minedByDay[timeTuple] += each.quantity

    startTime = now - NUM_DAYS_BACK * const.DAY
    nextTime = startTime
    summaryData = []
    while nextTime < now + const.DAY:
        year, month, wd, day, hour, min, sec, ms = blue.os.GetTimeParts(nextTime)
        mined = minedByDay.get((year, month, day), 0)
        timestamp = GetMaxDayTimeStamp(nextTime)
        summaryData.append([timestamp, mined])
        nextTime += const.DAY

    return summaryData


def IsInRange(timestamp, start, end):
    if start and timestamp < start:
        return False
    if end and timestamp > end:
        return False
    return True


def GetGroupingsForOreFromData(data):
    normalOreGroupIDs = set()
    moonTypeIDsByGroupID = defaultdict(set)
    for each in data:
        groupID = evetypes.GetGroupID(each.typeID)
        if groupID in MOON_ORE_GROUPS:
            moonTypeIDsByGroupID[groupID].add(each.typeID)
        else:
            normalOreGroupIDs.add(groupID)

    return (normalOreGroupIDs, moonTypeIDsByGroupID)


def GetGroupsForData(data):
    allCorps = set()
    allCharIDs = set()
    for each in data:
        allCorps.add(each.corporationID)
        allCharIDs.add(each.characterID)

    return (allCorps, allCharIDs)


def GetMaxDayTimeStamp(timestamp):
    year, month, wd, day, _, _, _, _ = blue.os.GetTimeParts(timestamp)
    return blue.os.GetTimeFromParts(year, month, day, 23, 59, 59, 99)


def GetMinDayTimeStamp(timestamp):
    year, month, wd, day, _, _, _, _ = blue.os.GetTimeParts(timestamp)
    return blue.os.GetTimeFromParts(year, month, day, 0, 0, 0, 0)


def GetColorForBaseTypeID(typeID):
    color = colorsByTypeID.get(typeID, None)
    if color:
        return color
    groupID = evetypes.GetGroupID(typeID)
    return colorsByGroupID.get(groupID, DEFAULT_COLOR)


colorsByGroupID = {invConst.groupArkonor: (0.957, 0.263, 0.212, 1.0),
 invConst.groupBistot: (0.298, 0.686, 0.314, 1.0),
 invConst.groupCrokite: (1.0, 0.792, 0.157, 1.0),
 invConst.groupDarkOchre: (0.329, 0.431, 0.478, 1.0),
 invConst.groupHedbergite: (0.0, 0.737, 0.831, 1.0),
 invConst.groupHemorphite: (0.247, 0.318, 0.71, 1.0),
 invConst.groupJaspet: (0.62, 0.62, 0.62, 1.0),
 invConst.groupKernite: (0.949, 0.659, 0.439, 1.0),
 invConst.groupPlagioclase: (0.38, 0.38, 0.38, 1.0),
 invConst.groupPyroxeres: (0.62, 0.792, 0.247, 1.0),
 invConst.groupScordite: (0.365, 0.251, 0.216, 1.0),
 invConst.groupSpodumain: (0.0, 0.588, 0.533, 1.0),
 invConst.groupVeldspar: (0.886, 0.808, 0.231, 1.0),
 invConst.groupGneiss: (0.773, 0.882, 0.647, 1.0),
 invConst.groupMercoxit: (0.957, 0.263, 0.196, 1.0),
 invConst.groupOmber: (0.753, 0.365, 0.82, 1.0),
 invConst.groupExceptionalMoonAsteroids: (0.776, 0.31, 0.251, 1.0),
 invConst.groupRareMoonAsteroids: (0.431, 0.604, 0.718, 1.0),
 invConst.groupUncommonMoonAsteroids: (0.776, 0.475, 0.247, 1.0),
 invConst.groupCommonMoonAsteroids: (0.478, 0.686, 0.184, 1.0),
 invConst.groupUbiquitousMoonAsteroids: (0.718, 0.659, 0.529, 1.0)}
colorsByTypeID = {invConst.typeClearIcicle: (0.694, 0.953, 1.0, 1.0),
 invConst.typeGlacialMass: (0.306, 0.773, 0.808, 1.0),
 invConst.typeBlueIce: (0.396, 0.902, 1.0, 1.0),
 invConst.typeWhiteGlaze: (0.753, 1.0, 1.0, 1.0),
 invConst.typeGlareCrust: (0.8, 0.843, 1.0, 1.0),
 invConst.typeAzureIce: (0.725, 0.894, 0.953, 1.0),
 invConst.typeCrystallineIcicle: (0.729, 0.898, 0.953, 1.0),
 invConst.typeDarkGlitter: (0.494, 0.824, 0.929, 1.0),
 invConst.typeEnrichedClearIcicle: (0.694, 0.953, 1.0, 1.0),
 invConst.typeGelidus: (0.808, 0.839, 0.929, 1.0),
 invConst.typeKrystallos: (0.725, 0.894, 0.953, 1.0),
 invConst.typePristineWhiteGlaze: (0.753, 1.0, 1.0, 1.0),
 invConst.typeSmoothGlacialMass: (0.306, 0.773, 0.808, 1.0),
 invConst.typeThickBlueIce: (0.396, 0.902, 1.0, 1.0),
 invConst.typeAmberCytoserocin: (1.0, 0.671, 0.251, 1.0),
 invConst.typeAmberMykoserocin: (1.0, 0.671, 0.251, 1.0),
 invConst.typeGoldenCytoserocin: (0.992, 0.847, 0.208, 1.0),
 invConst.typeGoldenMykoserocin: (0.992, 0.847, 0.208, 1.0),
 invConst.typeViridianCytoserocin: (0.149, 0.776, 0.855, 1.0),
 invConst.typeViridianMykoserocin: (0.149, 0.776, 0.855, 1.0),
 invConst.typeCeladonCytoserocin: (0.482, 0.122, 0.635, 1.0),
 invConst.typeCeladonMykoserocin: (0.482, 0.122, 0.635, 1.0),
 invConst.typeMalachiteCytoserocin: (0.4, 0.733, 0.416, 1.0),
 invConst.typeMalachiteMykoserocin: (0.4, 0.733, 0.416, 1.0),
 invConst.typeLimeCytoserocin: (0.831, 0.882, 0.341, 1.0),
 invConst.typeLimeMykoserocin: (0.831, 0.882, 0.341, 1.0),
 invConst.typeVermillionCytoserocin: (0.898, 0.451, 0.451, 1.0),
 invConst.typeVermillionMykoserocin: (0.898, 0.451, 0.451, 1.0),
 invConst.typeAzureCytoserocin: (0.012, 0.663, 0.957, 1.0),
 invConst.typeAzureMykoserocin: (0.012, 0.663, 0.957, 1.0),
 invConst.typeGambogeCytoserocin: (1.0, 0.596, 0.0, 1.0),
 invConst.typeChartreuseCytoserocin: (0.612, 0.153, 0.69, 1.0),
 invConst.typeFulleriteC50: (0.424, 0.188, 0.447, 1.0),
 invConst.typeFulleriteC60: (0.71, 0.318, 0.749, 1.0),
 invConst.typeFulleriteC70: (0.129, 0.588, 0.953, 1.0),
 invConst.typeFulleriteC72: (0.247, 0.514, 0.698, 1.0),
 invConst.typeFulleriteC84: (0.839, 0.357, 0.145, 1.0),
 invConst.typeFulleriteC28: (0.949, 0.373, 0.173, 1.0),
 invConst.typeFulleriteC32: (0.035, 0.718, 0.0, 1.0),
 invConst.typeFulleriteC320: (0.035, 0.478, 0.0, 1.0),
 invConst.typeFulleriteC540: (0.063, 0.639, 0.0, 1.0),
 invConst.typeDysprosium: (0.776, 0.31, 0.251, 1.0),
 invConst.typeNeodymium: (0.776, 0.31, 0.251, 1.0),
 invConst.typePromethium: (0.776, 0.31, 0.251, 1.0),
 invConst.typeThulium: (0.776, 0.31, 0.251, 1.0),
 invConst.typeMercury: (0.431, 0.604, 0.718, 1.0),
 invConst.typeCaesium: (0.431, 0.604, 0.718, 1.0),
 invConst.typeHafnium: (0.431, 0.604, 0.718, 1.0),
 invConst.typeTechnetium: (0.431, 0.604, 0.718, 1.0),
 invConst.typeChromium: (0.776, 0.475, 0.247, 1.0),
 invConst.typeVanadium: (0.776, 0.475, 0.247, 1.0),
 invConst.typeCadmium: (0.776, 0.475, 0.247, 1.0),
 invConst.typePlatinum: (0.776, 0.475, 0.247, 1.0),
 invConst.typeTungsten: (0.478, 0.686, 0.184, 1.0),
 invConst.typeTitanium: (0.478, 0.686, 0.184, 1.0),
 invConst.typeScandium: (0.478, 0.686, 0.184, 1.0),
 invConst.typeCobalt: (0.478, 0.686, 0.184, 1.0),
 invConst.typeHydrocarbons: (0.718, 0.659, 0.529, 1.0),
 invConst.typeAtmosphericGases: (0.718, 0.659, 0.529, 1.0),
 invConst.typeEvaporiteDeposits: (0.718, 0.659, 0.529, 1.0),
 invConst.typeSilicates: (0.718, 0.659, 0.529, 1.0)}

def GetColorsForTypeIDs(typeIDs):
    colors = []
    for eachTypeID in typeIDs:
        if eachTypeID == REST_ORE:
            colors.append(DEFAULT_COLOR)
            continue
        c = GetColorForBaseTypeID(eachTypeID)
        colors.append(c)

    return colors
