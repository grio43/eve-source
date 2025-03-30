#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\sofpreviewer\model.py
import blue
import evetypes
from fsdBuiltData.client.groupGraphics import GetGraphicIdsFromTypeID
from sofDnaLibrary.query import GetDnaStringsMatchingQuery
from modelconst import ModelConst

class SofPreviewerModel(object):

    def __init__(self):
        sofDB = blue.resMan.LoadObject('res:/dx9/model/spaceobjectfactory/data.red')
        self.const = ModelConst()
        self.sofFactions = []
        for faction in sofDB.faction:
            self.sofFactions.append(faction.name)

        self.sofFactions.sort()
        self.sofHulls = []
        self.multihulls = {}
        for hull in sofDB.hull:
            hull = hull.name
            if self.IsMultiHull(hull):
                baseHullName, subpart, variation = self.GetMultiHullInfo(hull)
                if baseHullName not in self.multihulls:
                    self.multihulls[baseHullName] = []
                self.multihulls[baseHullName].append((hull, subpart, variation))
                if subpart == 1:
                    self.sofHulls.append(hull)
            else:
                self.sofHulls.append(hull)

        self.sofHulls.sort()
        self.sofRaces = []
        for race in sofDB.race:
            self.sofRaces.append(race.name)

        self.sofRaces.sort()
        self.sofMaterials = []
        for material in sofDB.material:
            self.sofMaterials.append(material.name)

        self.sofMaterials.sort()
        self.sofMaterials.insert(0, 'None')
        self.sofVariants = []
        for i in xrange(len(sofDB.generic.variants)):
            self.sofVariants.append(sofDB.generic.variants[i].name)

        self.sofVariants.sort()
        self.sofVariants.insert(0, 'None')
        self.sofPatterns = []
        self.patternToHulls = {}
        for pattern in sofDB.pattern:
            self.sofPatterns.append(pattern.name)
            self.patternToHulls[pattern.name] = [ hull.name for hull in pattern.projections ]

        self.sofPatterns.sort()
        self.sofPatterns.insert(0, 'None')
        self._hullToTurretCount = self.CreateHullToTurretLocatorCountMap(sofDB)
        self._hiSlotItems = None

    def CreateHullToTurretLocatorCountMap(self, sofDB):
        hullToTurretCount = {}
        hulls = sofDB.hull
        for hull in hulls:
            uniqueTurretLocations = set()
            for turret in hull.locatorTurrets:
                turretNumber = int(filter(str.isdigit, turret.name))
                uniqueTurretLocations.add(turretNumber)

            hullToTurretCount[hull.name] = len(uniqueTurretLocations)

        return hullToTurretCount

    def IsMultiHull(self, hull):
        return len(self.const.MULTI_HULL_REGEX.findall(hull)) > 0

    def GetMultiHullInfo(self, hull):
        results = self.const.MULTI_HULL_REGEX.findall(hull)
        if len(results) > 0:
            return (hull.replace(results[0], ''), self.GetMultiHullSpecification(hull), self.GetMultiHullVariation(hull))
        return (None, None, None)

    def GetMultiHullVariation(self, hull):
        return int(self.const.MULTI_HULL_VARIATION_REGEX.findall(hull)[0].replace('v', ''))

    def GetMultiHullSpecification(self, hull):
        return int(self.const.MULTI_HULL_SPECIFICATION_REGEX.findall(hull)[0].replace('_s', ''))

    def GetMultiHullBaseName(self, hull):
        results = self.const.MULTI_HULL_REGEX.findall(hull)
        if len(results) > 0:
            result = results[0]
            return hull.replace(result, '')
        return ''

    @staticmethod
    def _GetDefaultFactionForT1Hull(hullName):
        dnaList = GetDnaStringsMatchingQuery(hullName)
        if len(dnaList) == 0:
            return ''
        race = dnaList[0].split(':')[2]
        return race + 'base'

    def _GetDefaultFactionForT2Hull(self, hullName):
        for factionName, hullList in self.const.DEFAULT_FACTION_FOR_T2HULLS.iteritems():
            if hullName in hullList:
                return factionName

        return ''

    @staticmethod
    def GetDnaFromPlayerShip():
        michelle = sm.GetService('michelle')
        ship = michelle.GetBall(session.shipid)
        if ship is None:
            return 'ab1_t1:amarrbase:amarr'
        dna = ship.GetDNA()
        if dna is None:
            return 'ab1_t1:amarrbase:amarr'
        return dna

    @property
    def highSlotTypeIDs(self):
        dogmalocation = sm.GetService('clientDogmaIM').GetFittingDogmaLocation(force=True)
        dogmastaticMgr = dogmalocation.dogmaStaticMgr
        typeIds = evetypes.GetAllTypeIDs()
        if self._hiSlotItems is not None:
            return self._hiSlotItems
        self._hiSlotItems = []
        for type in typeIds:
            effectTypes = dogmastaticMgr.TypeGetEffects(type)
            for effectType in effectTypes:
                if effectType == const.effectHiPower:
                    self._hiSlotItems.append(type)

        return self._hiSlotItems

    def GetHighSlotItemName(self, typeID):
        return evetypes.GetNameOrNone(typeID)

    def GetGraphicIdFromTypeId(self, typeID):
        return GetGraphicIdsFromTypeID(typeID)

    def GetTurretLocatorCountFromName(self, hullName):
        return self._hullToTurretCount.get(hullName, 0)

    def GetTurretLocatorCount(self, dna):
        try:
            from platformtools.compatibility.exposure import dnahelper
            parts = dnahelper.DNAParts(dna)
            hullName = parts.hull
            return self.GetTurretLocatorCountFromName(hullName)
        except ImportError:
            if ':' in dna:
                return self.GetTurretLocatorCountFromName(dna.split(':')[0])
            else:
                return 0
