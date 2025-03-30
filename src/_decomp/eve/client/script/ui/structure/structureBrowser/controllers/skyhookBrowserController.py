#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\structureBrowser\controllers\skyhookBrowserController.py
import datetimeutils
import eveformat
import evetypes
import gametime
from evePathfinder.core import IsUnreachableJumpCount
from eve.client.script.ui.structure.structureBrowser import browserUIConst
from eve.client.script.ui.eveColor import CHERRY_RED_HEX, CRYO_BLUE_HEX
from localization import GetByLabel
from localization.formatters import FormatTimeIntervalShortWritten
from orbitalSkyhook.const import STATE_LABELS, STATE_VULNERABILITY
import logging
from sovereignty.resource.shared.planetary_resources_cache import DataUnavailableError
from sovereignty.skyhook.shared.skyhook_type_inference import get_skyhook_type_and_amount, is_non_reagent_skyhook, get_skyhook_product_type
logger = logging.getLogger(__name__)

class SkyhookBrowserController(object):

    def __init__(self):
        self.mySkyhooks = {}

    def GetMySkyhooks(self):
        mySkyhooks = sm.GetService('sovereigntyResourceSvc').GetMyCorporationSkyhooksMemoized()
        skyhookControllers = self._GetControllersFromSkyhookList(mySkyhooks)
        return skyhookControllers

    def _GetControllersFromSkyhookList(self, skyhooks):
        self.mySkyhooks.clear()
        skyhookControllers = []
        idsToPrime = {x.skyhookID for x in skyhooks}
        idsToPrime.union({x.solarSystemID for x in skyhooks})
        idsToPrime.union({x.planetID for x in skyhooks})
        cfg.evelocations.Prime(idsToPrime)
        sovResourceSvc = sm.GetService('sovereigntyResourceSvc')
        try:
            sovResourceSvc.PrimeStaticDataForPlanets()
            planetDataWasPrimed = True
        except Exception:
            planetDataWasPrimed = False

        try:
            skyhooks_details = sovResourceSvc.GetMyCorporationsSkyhookDetailsMemoized()
        except DataUnavailableError as e:
            skyhooks_details = None
            logger.error('Failed to get Skyhooks Details: %s', e)

        for eachSkyhook in skyhooks:
            skyhook_detail = skyhooks_details.get(eachSkyhook.skyhookID, None) if skyhooks_details is not None else None
            reagentTypeID = None
            resourceVersion = None
            if skyhook_detail:
                reagentDefinition = skyhook_detail.get_first_reagent_data()
                reagentTypeID = reagentDefinition.type_id if reagentDefinition is not None else None
                resourceVersion = skyhook_detail.resource_version
            product = None
            if planetDataWasPrimed:
                power = sovResourceSvc.GetPlanetPowerProduction(eachSkyhook.planetID, resourceVersion)
                workforce = sovResourceSvc.GetPlanetWorkforceProduction(eachSkyhook.planetID, resourceVersion)
                product = get_skyhook_product_type(reagentTypeID, power, workforce)
            sController = SkyhookEntryController(eachSkyhook, skyhook_detail, product, planetDataWasPrimed)
            self.mySkyhooks[eachSkyhook.skyhookID] = sController
            skyhookControllers.append(sController)

        return skyhookControllers


class SkyhookEntryController(object):

    def __init__(self, skyhook, skyhookData, product, planetDataWasPrimed):
        self.skyHookInfo = skyhook
        self.skyhookData = skyhookData
        self.systemAndSkyhookName = None
        self.filterText = None
        self.planetDataWasPrimed = planetDataWasPrimed
        self.product = product

    def GetNumJumps(self):
        jumps = sm.GetService('clientPathfinderService').GetJumpCountFromCurrent(self.GetSolarSystemID())
        return jumps

    def GetNumJumpsText(self):
        jumps = self.GetNumJumps()
        if IsUnreachableJumpCount(jumps):
            return '-'
        else:
            return jumps

    def GetSecurity(self):
        return sm.GetService('map').GetSecurityStatus(self.GetSolarSystemID())

    def GetSolarSystemID(self):
        return self.skyHookInfo.solarSystemID

    def GetSecurityWithColor(self):
        return eveformat.client.solar_system_security_status(self.GetSolarSystemID())

    def GetSolarSystemName(self):
        return cfg.evelocations.Get(self.GetSolarSystemID()).name

    def GetName(self):
        if self.systemAndSkyhookName:
            return self.systemAndSkyhookName
        locationName = cfg.evelocations.Get(self.GetSolarSystemID()).name
        typeName = evetypes.GetName(self.GetTypeID())
        skyhookName = '%s - %s' % (typeName, cfg.evelocations.Get(self.skyHookInfo.planetID).name)
        systemAndSkyhookName = '<br>'.join([locationName, skyhookName])
        self.systemAndSkyhookName = systemAndSkyhookName
        return self.systemAndSkyhookName

    def GetFilterText(self):
        if self.filterText is not None:
            return self.filterText
        regionID = self.GetRegionID()
        regionText = cfg.evelocations.Get(regionID).name if regionID else ''
        textList = [self.GetCleanName(),
         self.GetHarvestText(),
         self.GetSystemName(),
         evetypes.GetName(self.GetTypeID()),
         regionText,
         self.GetStateText()]
        text = ' '.join(textList)
        text = text.lower()
        self.filterText = text
        return text

    def GetCleanName(self):
        typeName = evetypes.GetName(self.GetTypeID())
        skyhookName = '%s - %s' % (typeName, cfg.evelocations.Get(self.skyHookInfo.planetID).name)
        return skyhookName

    def GetSystemName(self):
        return cfg.evelocations.Get(self.GetSolarSystemID()).name

    def GetTypeID(self):
        return self.skyHookInfo.typeID

    def GetItemID(self):
        return self.skyHookInfo.skyhookID

    def GetRegionID(self):
        regionID = sm.GetService('map').GetRegionForSolarSystem(self.GetSolarSystemID())
        return regionID

    def IsVulnerable(self):
        return STATE_VULNERABILITY.get(self.skyHookInfo.state, False)

    def IsTheftVulnerable(self):
        if is_non_reagent_skyhook(self.product):
            return False
        vulnerabilityData = self.skyhookData.vulnerability_data
        if vulnerabilityData is None:
            return False
        return vulnerabilityData.vulnerable

    def GetStateText(self):
        labelPath = STATE_LABELS.get(self.skyHookInfo.state, None)
        if labelPath:
            return GetByLabel(labelPath)
        return ''

    def GetHarvestText(self):
        if not self.planetDataWasPrimed:
            return '-'
        if self.skyhookData is None:
            reagentTypeID, reagentAmountsInfo, power, workforce = sm.GetService('sovereigntyResourceSvc').GetPlanetResourceInfo(self.skyHookInfo.planetID)
        else:
            reagentDefinition = self.skyhookData.get_first_reagent_data()
            reagentTypeID = reagentDefinition.type_id if reagentDefinition is not None else None
            reagentAmountsInfo = (reagentDefinition.configuration.amount_per_period, reagentDefinition.configuration.period) if reagentDefinition is not None else None
            power = sm.GetService('sovereigntyResourceSvc').GetPlanetPowerProduction(self.skyHookInfo.planetID, self.skyhookData.resource_version)
            workforce = sm.GetService('sovereigntyResourceSvc').GetPlanetWorkforceProduction(self.skyHookInfo.planetID, self.skyhookData.resource_version)
        if reagentTypeID and reagentAmountsInfo:
            amount, period = reagentAmountsInfo
            amountPerMin = float(amount) / (float(period) / 60)
            amountText = GetByLabel('UI/Sovereignty/AmountPerMinute', value=float(amountPerMin))
            return '%s (%s)' % (evetypes.GetName(reagentTypeID), amountText)
        if power:
            return '%s (%s)' % (GetByLabel('UI/Sovereignty/Power'), power)
        if workforce:
            if self.skyhookData.workforce is not None:
                percentage_difference = round((self.skyhookData.workforce - workforce) / float(workforce) * 100)
                color = CHERRY_RED_HEX if percentage_difference < 0 else CRYO_BLUE_HEX
                return "%s (%s <color='%s'>(%s%%)</color>)" % (GetByLabel('UI/Sovereignty/Workforce'),
                 self.skyhookData.workforce,
                 color,
                 percentage_difference)
            return '%s (%s)' % (GetByLabel('UI/Sovereignty/Workforce'), workforce)
        return ''

    def GetTheftVulnerabilityText(self):
        if is_non_reagent_skyhook(self.product):
            return GetByLabel('UI/StructureBrowser/NotApplicable')
        else:
            vulnerabilityData = self.skyhookData.vulnerability_data
            if vulnerabilityData is None:
                return GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/NoDataAvailable')
            now = gametime.GetWallclockTime()
            start_blue = datetimeutils.datetime_to_filetime(vulnerabilityData.start)
            end_blue = datetimeutils.datetime_to_filetime(vulnerabilityData.end)
            if end_blue <= now:
                return GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/NoDataAvailable')
            if vulnerabilityData.vulnerable:
                countdown = FormatTimeIntervalShortWritten(end_blue - now, 'day', 'minute')
                return GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/VulnerableToTheft', countdown=countdown)
            countdown = FormatTimeIntervalShortWritten(max(0, start_blue - now), 'day', 'minute')
            return GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/SecureFromTheft', countdown=countdown)

    def GetTheftVulnerabilitySortValue(self):
        vulnerabilityData = self.skyhookData.vulnerability_data
        if is_non_reagent_skyhook(self.product) or vulnerabilityData is None:
            return (3, GetByLabel('UI/StructureBrowser/NotApplicable'))
        elif vulnerabilityData.vulnerable:
            end_blue = datetimeutils.datetime_to_filetime(vulnerabilityData.end)
            return (1, end_blue)
        else:
            start_blue = datetimeutils.datetime_to_filetime(vulnerabilityData.start)
            return (2, start_blue)
