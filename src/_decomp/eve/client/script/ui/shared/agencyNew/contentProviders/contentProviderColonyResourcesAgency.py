#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentProviders\contentProviderColonyResourcesAgency.py
import log
import telemetry
import uthread2
from eve.common.lib import appConst
from caching import Memoize
from eve.common.script.sys import idCheckers
from collections import namedtuple
from eve.client.script.ui.shared.agencyNew import agencyConst, agencyFilters, agencySignals
from eve.client.script.ui.shared.agencyNew.agencyUtil import GetNumberOfJumps
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentProviders.baseContentProvider import BaseContentProvider
from eve.client.script.ui.shared.agencyNew.contentPieces.colonyResourcesAgencySystemContentPiece import ColonyResourcesAgencySystemContentPiece
import orbitalSkyhook.resourceRichness as resourceRichness
from locks import TempLock

class ContentProviderColonyResourcesAgency(BaseContentProvider):
    contentType = agencyConst.CONTENTTYPE_COLONYRESOURCESAGENCY
    contentGroup = contentGroupConst.contentGroupColonyResourcesAgency
    __notifyevents__ = BaseContentProvider.__notifyevents__ + ['OnSessionChanged']

    def __init__(self):
        self.sovereigntyResourceSvc = sm.GetService('sovereigntyResourceSvc')
        self.starMapSvc = sm.GetService('starmap')
        self.validSolarSystemIDs = []
        self.allianceSolarSystems = None
        self._solarSystemAndPlanetValues = {}
        self.nullSecSolarsystems = None
        super(ContentProviderColonyResourcesAgency, self).__init__()
        agencySignals.on_content_pieces_invalidated.connect(self.OnContentPiecesInvalidated)

    def __del__(self):
        sm.UnregisterNotify(self)

    def OnContentPiecesInvalidated(self, *args):
        self.validSolarSystemIDs = []
        self.allianceSolarSystems = None
        self._solarSystemAndPlanetValues.clear()

    def InvalidateSystemCache(self, *args):
        self.validSolarSystemIDs = []

    def OnSessionChanged(self, isRemote, sess, change):
        if 'solarsystemid' in change:
            self.InvalidateSystemCache()

    def OnAgencyFilterChanged(self, contentGroupID, filterType, value):
        if contentGroupID != self.contentGroup:
            return
        self.InvalidateFilter()
        super(ContentProviderColonyResourcesAgency, self).OnAgencyFilterChanged(contentGroupID, filterType, value)

    def InvalidateFilter(self):
        self.validSolarSystemIDs = []
        for _, planetLoookup in self._solarSystemAndPlanetValues.itervalues():
            planetLoookup.ClearMeetCriteria()

    @Memoize
    def GetPlanetItemIDsInSystem(self, solarSystemID):
        solarSystemInfo = cfg.mapSystemCache.Get(solarSystemID)
        return solarSystemInfo.planetItemIDs

    def _GetValidSolarSystemIDs(self):
        self.PrimeNullSecSystems()
        self.PrimeAllianceSolarsystems()
        theftVulnerableSystemIDs = self.sovereigntyResourceSvc.GetSolarSystemsWithTheftVulnerableSkyhooks()
        validSolarSystems = []
        distanceFilter = agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_DISTANCE)
        regionFilter = agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_REGION)
        skyhookFilter = agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_SKYHOOK_THEFT_VULNERABILITY)
        if distanceFilter == agencyConst.DISTANCE_CURRSYSTEM:
            currentSystemID = session.solarsystemid2
            if currentSystemID in self.nullSecSolarsystems and self.CheckSystemCriteria(currentSystemID):
                return [currentSystemID]
            return []
        for ssID, solarSystem in self.nullSecSolarsystems.iteritems():
            if distanceFilter == agencyConst.DISTANCE_REGION and solarSystem.regionID != regionFilter:
                continue
            if skyhookFilter == agencyConst.SKYHOOKS_THEFT_VULNERABLE and ssID not in theftVulnerableSystemIDs:
                continue
            if self.CheckSystemCriteria(ssID):
                validSolarSystems.append(ssID)

        return validSolarSystems

    @telemetry.ZONE_METHOD
    def PrimeNullSecSystems(self):
        if self.nullSecSolarsystems is None:
            factionService = sm.GetService('faction')
            self.nullSecSolarsystems = {ssID:solarSystem for ssID, solarSystem in cfg.mapSystemCache.iteritems() if factionService.GetFactionOfSolarSystem(ssID) is None and not idCheckers.IsWormholeSystem(ssID) and idCheckers.IsKnownSpaceSystem(ssID)}

    def GetValidSolarSystemIDs(self):
        self.validSolarSystemIDs = sorted(self._GetValidSolarSystemIDs(), key=lambda systemID: GetNumberOfJumps(systemID))
        return self.validSolarSystemIDs

    @telemetry.ZONE_METHOD
    def GetColonyResources(self, solarSystemID):
        if solarSystemID in self._solarSystemAndPlanetValues:
            return self._solarSystemAndPlanetValues[solarSystemID]
        with TempLock('GetColonyResources_%s' % solarSystemID):
            if solarSystemID in self._solarSystemAndPlanetValues:
                return self._solarSystemAndPlanetValues[solarSystemID]
            systemResourceValues, planetResourceValues = self._GetReasourceValuesForSystemAndPlanets(solarSystemID)
            planetLoookup = PlanetLookupPerSolarSystem(self, solarSystemID, planetResourceValues)
            self._solarSystemAndPlanetValues[solarSystemID] = (systemResourceValues, planetLoookup)
            return (systemResourceValues, planetLoookup)

    @telemetry.ZONE_METHOD
    def _GetColonyResources(self, solarSystemID):
        systemResourceValues, planetResourceValues = self._GetReasourceValuesForSystemAndPlanets(solarSystemID)
        if systemResourceValues is None:
            return
        return (systemResourceValues, planetResourceValues)

    @telemetry.ZONE_METHOD
    def _GetReasourceValuesForSystemAndPlanets(self, solarSystemID):
        planetIDs = self.GetPlanetItemIDsInSystem(solarSystemID)
        if not planetIDs:
            return (None, None)
        accumulatedMagmaticGas = 0
        accumulatedSuperionicIce = 0
        accumulatedPowerOuput = 0
        accumulatedWorkforce = 0
        hasSuperionicIce = False
        hasMagmaticGas = False
        planetValuesInSystem = []
        starResourceValues = self.GetResourceValuesForStar(solarSystemID)
        if starResourceValues:
            planetValuesInSystem.append(starResourceValues)
            accumulatedPowerOuput += starResourceValues.powerOutput
        for planetID in planetIDs:
            planetResourceValues = self.GetResourceValuesForPlanet(planetID)
            accumulatedPowerOuput += planetResourceValues.powerOutput
            accumulatedWorkforce += planetResourceValues.workforceOutput
            if planetResourceValues.reagentsTypes:
                if planetResourceValues.reagentsTypes.hasMagmaticGas:
                    hasMagmaticGas = True
                    accumulatedMagmaticGas += planetResourceValues.reagentsTypes.magmaticGasAmount
                if planetResourceValues.reagentsTypes.hasSuperionicIce:
                    hasSuperionicIce = True
                    accumulatedSuperionicIce += planetResourceValues.reagentsTypes.superionicIceAmount
            planetValuesInSystem.append(planetResourceValues)

        lavaRichnessSystem = resourceRichness.GetLavaRichnessForSystem(accumulatedMagmaticGas)
        iceRichnessSystem = resourceRichness.GetIceRichnessForSystem(accumulatedSuperionicIce)
        powerRichnessSystem = resourceRichness.GetPowerRichnessForSystem(accumulatedPowerOuput)
        workforceRichnessSystem = resourceRichness.GetWorkforceRichnessForSystem(accumulatedWorkforce)
        systemResourceValues = ColonyResourcesValues(itemID=solarSystemID, powerOutput=accumulatedPowerOuput, powerRichness=powerRichnessSystem, workforceOutput=accumulatedWorkforce, workforceRichness=workforceRichnessSystem, reagentsTypes=ReagentsTypes(hasMagmaticGas=hasMagmaticGas, magmaticGasAmount=accumulatedMagmaticGas, magmaticGasRichness=lavaRichnessSystem, hasSuperionicIce=hasSuperionicIce, superionicIceAmount=accumulatedSuperionicIce, superionicIceRichness=iceRichnessSystem))
        return (systemResourceValues, planetValuesInSystem)

    def GetResourceValuesForStar(self, solarSystemID):
        starID = cfg.mapSolarSystemContentCache[solarSystemID].star.id
        starPower = self.sovereigntyResourceSvc.planetProductionStaticData.get_power_production_for_star(starID)
        if not starPower:
            return
        starPowerMax = max(starPower, 0)
        powerRichnessPlanet = resourceRichness.GetPowerRichnessForPlanet(starPowerMax)
        colonyResourcesValues = ColonyResourcesValues(itemID=starID, powerOutput=starPowerMax, powerRichness=powerRichnessPlanet, workforceOutput=None, workforceRichness=resourceRichness.RICHNESS_NONE, reagentsTypes=None)
        return colonyResourcesValues

    def GetResourceValuesForPlanet(self, planetID):
        planetHasSuperionicIce = False
        planetHasMagmaticGas = False
        reagentType, reagentAmountsInfo, powerOutput, workforceOutput = self.sovereigntyResourceSvc.GetPlanetResourceInfo(planetID)
        powerOutput = powerOutput or 0
        workforceOutput = workforceOutput or 0
        hourlyPerPlanet = 0
        magmaticGasHourly = 0
        superionicIceHourly = 0
        if reagentAmountsInfo:
            amountPerPeriod, period = reagentAmountsInfo
            secsInHour = 3600
            amountPerHour = round(float(amountPerPeriod) / (float(period) / secsInHour), 1)
            hourlyPerPlanet = amountPerHour
        if reagentType == agencyConst.REAGENTS_MAGMATIC_GAS:
            planetHasMagmaticGas = True
            magmaticGasHourly = hourlyPerPlanet
        elif reagentType == agencyConst.REAGENTS_SUPERIONIC_ICE:
            planetHasSuperionicIce = True
            superionicIceHourly = hourlyPerPlanet
        lavaRichnessPlanet = resourceRichness.GetLavaRichnessForPlanet(magmaticGasHourly)
        iceRichnessPlanet = resourceRichness.GetIceRichnessForPlanet(superionicIceHourly)
        powerRichnessPlanet = resourceRichness.GetPowerRichnessForPlanet(powerOutput)
        workforceRichnessPlanet = resourceRichness.GetWorkforceRichnessForPlanet(workforceOutput)
        reagentsTypes = ReagentsTypes(hasMagmaticGas=planetHasMagmaticGas, magmaticGasAmount=magmaticGasHourly, magmaticGasRichness=lavaRichnessPlanet, hasSuperionicIce=planetHasSuperionicIce, superionicIceAmount=superionicIceHourly, superionicIceRichness=iceRichnessPlanet)
        planetColonyResourcesValues = ColonyResourcesValues(itemID=planetID, powerOutput=powerOutput, powerRichness=powerRichnessPlanet, workforceOutput=workforceOutput, workforceRichness=workforceRichnessPlanet, reagentsTypes=reagentsTypes)
        return planetColonyResourcesValues

    def CheckSystemCriteria(self, solarSystemID):
        systemResourceValues, planetLookupPerSolarSystem = self.GetColonyResources(solarSystemID)
        distance = self.CheckDistanceCriteria(solarSystemID)
        if not distance:
            return False
        sovereignty = self.CheckSystemSovereignty(solarSystemID)
        if not sovereignty:
            return False
        perSystemPlanetFilter = self.GetPerSystemPlanetFilter()
        if perSystemPlanetFilter == agencyConst.OPTION_PER_PLANET_VALUE:
            if planetLookupPerSolarSystem.CheckSomePlanetMeetsCriteria():
                return True
            return False
        powerOutput = self.CheckSystemPowerOutput(systemResourceValues)
        if not powerOutput:
            return False
        workforceOutput = self.CheckSystemWorkforceoutput(systemResourceValues)
        if not workforceOutput:
            return False
        reagentsMagmaticGasRichness = self.CheckSystemMagmaticGasRichness(systemResourceValues)
        if not reagentsMagmaticGasRichness:
            return False
        reagentsSuperionicIceRichness = self.CheckSystemSuperionicIceRichness(systemResourceValues)
        if not reagentsSuperionicIceRichness:
            return False
        return True

    def GetPerSystemPlanetFilter(self):
        perSystemPlanetFilter = agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_PER_SYSTEM_PLANET)
        return perSystemPlanetFilter

    def CheckSystemSovereignty(self, solarSystemID):
        sovereigntyFilter = agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_SOVEREIGNTY)
        if sovereigntyFilter == agencyConst.SOVEREIGNTY_ALL:
            return True
        if sovereigntyFilter == agencyConst.SOVEREIGNTY_CLAIMED and not self.allianceSolarSystems.get(solarSystemID):
            return False
        if sovereigntyFilter == agencyConst.SOVEREIGNTY_UNCLAIMED and self.allianceSolarSystems.get(solarSystemID):
            return False
        return True

    def PrimeAllianceSolarsystems(self):
        if self.allianceSolarSystems is None:
            self.allianceSolarSystems = self.starMapSvc.GetAllianceSolarSystems()

    def CheckSystemMagmaticGasRichness(self, systemResourceValues):
        reagentsMagmaticGasFilter = agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_REAGENTS_MAGMATIC_GAS_RICHNESS)
        if reagentsMagmaticGasFilter == agencyConst.REAGENTS_RICHNESS_ALL:
            return True
        return systemResourceValues.reagentsTypes.IsSameIceRicheness(reagentsMagmaticGasFilter)

    def CheckSystemSuperionicIceRichness(self, systemResourceValues):
        reagentsSuperionicIceFilter = agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_REAGENTS_SUPERIONIC_ICE_RICHNESS)
        if reagentsSuperionicIceFilter == agencyConst.REAGENTS_RICHNESS_ALL:
            return True
        return systemResourceValues.reagentsTypes.IsSameIceRicheness(reagentsSuperionicIceFilter)

    def CheckSystemPowerOutput(self, systemResourceValues):
        powerOutputFilter = agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_POWEROUTPUT)
        return systemResourceValues.powerOutput >= powerOutputFilter

    def CheckSystemWorkforceoutput(self, systemResourceValues):
        workforceOutputFilter = agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_WORKFORCEOUTPUT)
        return systemResourceValues.workforceOutput >= workforceOutputFilter

    def CheckPlanetCriteria(self, colonyResourcesValues):
        if not self.CheckPlanetWorkforceOutput(colonyResourcesValues.workforceOutput):
            return False
        if not self.CheckPlanetPowerOutput(colonyResourcesValues.powerOutput):
            return False
        if not self.CheckPlanetMagmaticGasRichness(colonyResourcesValues.reagentsTypes):
            return False
        if not self.CheckPlanetSuperionicIceRichness(colonyResourcesValues.reagentsTypes):
            return False
        return True

    def CheckPlanetSovereignty(self, sovereignty):
        sovereigntyFilter = agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_SOVEREIGNTY)
        if sovereigntyFilter == agencyConst.SOVEREIGNTY_ALL:
            return True
        if sovereigntyFilter == agencyConst.SOVEREIGNTY_CLAIMED:
            return sovereignty
        if sovereigntyFilter == agencyConst.SOVEREIGNTY_UNCLAIMED:
            if sovereignty:
                return False
            else:
                return True

    def CheckPlanetWorkforceOutput(self, workforceOutput):
        workforceFilter = agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_WORKFORCEOUTPUT)
        if not workforceFilter:
            return True
        return workforceOutput >= workforceFilter

    def CheckPlanetPowerOutput(self, powerOutput):
        powerOutputFilter = agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_POWEROUTPUT)
        if not powerOutputFilter:
            return True
        return powerOutput >= powerOutputFilter

    def CheckPlanetMagmaticGasRichness(self, reagentsTypes):
        magmaticGasRichnessFilter = agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_REAGENTS_MAGMATIC_GAS_RICHNESS)
        if magmaticGasRichnessFilter == agencyConst.REAGENTS_RICHNESS_ALL:
            return True
        if reagentsTypes is None:
            return False
        return reagentsTypes.IsSameMagmaRicheness(magmaticGasRichnessFilter)

    def CheckPlanetSuperionicIceRichness(self, reagentsTypes):
        superionicIceRichnessFilter = agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_REAGENTS_SUPERIONIC_ICE_RICHNESS)
        if superionicIceRichnessFilter == agencyConst.REAGENTS_RICHNESS_ALL:
            return True
        if reagentsTypes is None:
            return False
        return reagentsTypes.IsSameIceRicheness(superionicIceRichnessFilter)

    def CheckPlanetReagentsType(self, planetID, reagentsTypes):
        reagentsTypeFilter = agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_REAGENTS_TYPE)
        if reagentsTypeFilter == agencyConst.REAGENTS_ALL:
            return True
        if reagentsTypeFilter == agencyConst.REAGENTS_MAGMATIC_GAS:
            return reagentsTypes.hasMagmaticGas
        if reagentsTypeFilter == agencyConst.REAGENTS_SUPERIONIC_ICE:
            return reagentsTypes.hasSuperionicIce

    def CheckPlanetReagentsRichness(self, planetID, reagentsTypes):
        reagentsTypeFilter = agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_REAGENTS_TYPE)
        reagentsRichnessFilter = agencyFilters.GetFilterValue(self.contentGroup, agencyConst.FILTERTYPE_REAGENTS_RICHNESS)
        if reagentsRichnessFilter == agencyConst.REAGENTS_RICHNESS_ALL:
            return True
        if reagentsRichnessFilter == agencyConst.REAGENTS_RICHNESS_MODEST:
            if reagentsTypeFilter == agencyConst.REAGENTS_ALL:
                return reagentsTypes.magmaticGasRichness.modest or reagentsTypes.superionicIceRichness.modest
            if reagentsTypeFilter == agencyConst.REAGENTS_MAGMATIC_GAS:
                return reagentsTypes.magmaticGasRichness.modest
            if reagentsTypeFilter == agencyConst.REAGENTS_SUPERIONIC_ICE:
                return reagentsTypes.superionicIceRichness.modest
        elif reagentsRichnessFilter == agencyConst.REAGENTS_RICHNESS_AVERAGE:
            if reagentsTypeFilter == agencyConst.REAGENTS_ALL:
                return reagentsTypes.magmaticGasRichness.average or reagentsTypes.superionicIceRichness.average
            if reagentsTypeFilter == agencyConst.REAGENTS_MAGMATIC_GAS:
                return reagentsTypes.magmaticGasRichness.average
            if reagentsTypeFilter == agencyConst.REAGENTS_SUPERIONIC_ICE:
                return reagentsTypes.superionicIceRichness.average
        elif reagentsRichnessFilter == agencyConst.REAGENTS_RICHNESS_ABUNDANT:
            if reagentsTypeFilter == agencyConst.REAGENTS_ALL:
                return reagentsTypes.magmaticGasRichness.abundant or reagentsTypes.superionicIceRichness.abundant
            if reagentsTypeFilter == agencyConst.REAGENTS_MAGMATIC_GAS:
                return reagentsTypes.magmaticGasRichness.abundant
            if reagentsTypeFilter == agencyConst.REAGENTS_SUPERIONIC_ICE:
                return reagentsTypes.superionicIceRichness.abundant

    @telemetry.ZONE_METHOD
    def _ConstructContentPieces(self):
        if not self.validSolarSystemIDs:
            self.validSolarSystemIDs = self.GetValidSolarSystemIDs()[:agencyConst.COLONY_RESOURCE_AGENCY_PIECES_MAX]
        self.ExtendContentPieces([ self.ConstructSystemContentPiece(solarSystemID) for solarSystemID in self.validSolarSystemIDs ])

    def ConstructSystemContentPiece(self, solarSystemID):
        systemResourceValues, planetLookupPerSolarSystem = self.GetColonyResources(solarSystemID)
        self.PrimeAllianceSolarsystems()
        sovAllianceID = self.allianceSolarSystems.get(solarSystemID, None)
        return ColonyResourcesAgencySystemContentPiece(planetLookupPerSolarSystem, systemResourceValues, sovAllianceID=sovAllianceID, solarSystemID=solarSystemID, typeID=appConst.typeSolarSystem, itemID=solarSystemID)


class ColonyResourcesValues(object):

    def __init__(self, itemID, powerOutput, powerRichness, workforceOutput, workforceRichness, reagentsTypes):
        self._itemID = itemID
        self._powerOutput = powerOutput
        self._powerRichness = powerRichness
        self._workforceOutput = workforceOutput
        self._workforceRichness = workforceRichness
        self._reagentsTypes = reagentsTypes

    @property
    def itemID(self):
        return self._itemID

    @property
    def powerOutput(self):
        return self._powerOutput

    @property
    def powerRichness(self):
        return self._powerRichness

    @property
    def workforceOutput(self):
        return self._workforceOutput

    @property
    def workforceRichness(self):
        return self._workforceRichness

    @property
    def reagentsTypes(self):
        return self._reagentsTypes

    def __repr__(self):
        return '<ColonyResourcesValues %s>, %s' % (self.__dict__, id(self))


class ReagentsTypes(object):

    def __init__(self, hasMagmaticGas, magmaticGasAmount, magmaticGasRichness, hasSuperionicIce, superionicIceAmount, superionicIceRichness):
        self._hasMagmaticGas = hasMagmaticGas
        self._magmaticGasAmount = magmaticGasAmount
        self._magmaticGasRichness = magmaticGasRichness
        self._hasSuperionicIce = hasSuperionicIce
        self._superionicIceAmount = superionicIceAmount
        self._superionicIceRichness = superionicIceRichness

    @property
    def hasMagmaticGas(self):
        return self._hasMagmaticGas

    @property
    def magmaticGasAmount(self):
        return self._magmaticGasAmount

    @property
    def magmaticGasRichness(self):
        return self._magmaticGasRichness

    @property
    def hasSuperionicIce(self):
        return self._hasSuperionicIce

    @property
    def superionicIceAmount(self):
        return self._superionicIceAmount

    @property
    def superionicIceRichness(self):
        return self._superionicIceRichness

    @property
    def magmaIsModest(self):
        return self.magmaticGasRichness == resourceRichness.RICHNESS_MODEST

    @property
    def magmaIsAverage(self):
        return self.magmaticGasRichness == resourceRichness.RICHNESS_AVG

    @property
    def magmaIsAbundant(self):
        return self.magmaticGasRichness == resourceRichness.RICHNESS_ABUNDANT

    @property
    def iceIsModest(self):
        return self.superionicIceRichness == resourceRichness.RICHNESS_MODEST

    @property
    def iceIsAverage(self):
        return self.superionicIceRichness == resourceRichness.RICHNESS_AVG

    @property
    def iceIsAbundant(self):
        return self.superionicIceRichness == resourceRichness.RICHNESS_ABUNDANT

    def IsSameMagmaRicheness(self, richnessToCheck):
        return self.magmaticGasRichness == richnessToCheck

    def IsSameIceRicheness(self, richnessToCheck):
        return self.superionicIceRichness == richnessToCheck

    def __repr__(self):
        return '<ReagentsTypes %s>, %s' % (self.__dict__, id(self))


class PlanetLookupPerSolarSystem(object):

    def __init__(self, contentProvider, solarSystemID, planetResourceValues):
        self._contentProvider = contentProvider
        self._solarSystemID = solarSystemID
        self._planetResourceValuesByPlanetID = {x.itemID:x for x in planetResourceValues}
        self._meetCriteria = {}

    def CheckSomePlanetMeetsCriteria(self):
        for planetValue in self._planetResourceValuesByPlanetID.itervalues():
            meetsCriteria = self._MeetsPlanetCriteria(planetValue)
            if meetsCriteria:
                return True

        return False

    @telemetry.ZONE_METHOD
    def _MeetsPlanetCriteria(self, planetValue):
        if planetValue.itemID in self._meetCriteria:
            return self._meetCriteria[planetValue.itemID]
        meetsCriteria = self._contentProvider.CheckPlanetCriteria(planetValue)
        self._meetCriteria[planetValue.itemID] = meetsCriteria
        return meetsCriteria

    def GetValidPlanetResourceValues(self):
        perSystemPlanetFilter = self._contentProvider.GetPerSystemPlanetFilter()
        filteringPerSolarSystem = perSystemPlanetFilter == agencyConst.OPTION_PER_SYSTEM_VALUE
        validResourceValues = []
        for planetValue in self._planetResourceValuesByPlanetID.itervalues():
            if filteringPerSolarSystem:
                validResourceValues.append(planetValue)
                continue
            meetsCriteria = self._MeetsPlanetCriteria(planetValue)
            if meetsCriteria:
                validResourceValues.append(planetValue)

        return validResourceValues

    def ClearMeetCriteria(self):
        self._meetCriteria.clear()
