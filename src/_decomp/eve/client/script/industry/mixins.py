#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\industry\mixins.py
import collections
import copy
import numbers
import blue
from caching.memoize import Memoize
from carbon.common.script.util.format import DateToBlue, FmtDate
from clonegrade.const import CLONE_STATE_ALPHA
from eve.client.script.environment.invControllers import POSCorpHangar, StationContainer, StationCorpHangar, StationItems, StructureCorpHangar, StructureItemHangar
from eve.common.lib import appConst as const
from eve.client.script.ui import eveColor
from eve.common.script.sys import idCheckers
from eve.common.script.sys.idCheckers import IsStation, flagCorpSAGs, IsShip
import evetypes
from industry.const import Reference
from inventorycommon.util import GetPackagedVolume
from localization.formatters.timeIntervalFormatters import FormatTimeInterval
import industry
import structures
import localization
import telemetry
import inventorycommon.typeHelpers
from eve.client.script.ui.shared.inventory.invCommon import CONTAINERGROUPS
from industry.const import REACTION_GROUPS
from eve.client.script.ui.shared.industry import industryUIConst, GetGroupName, GetProductGroupAndCategory
from eve.common.script.util import industryCommon
from eve.common.script.util.slimItem import SlimItem
from carbonui.util.color import Color
from utillib import KeyVal
from eveprefs import boot
INSTALLED_TEXT = localization.GetByLabel('UI/Industry/Installed')
IMPOUNTED_TEXT = localization.GetByLabel('UI/Corporations/Assets/Impounded')
NON_FACILITY_TEXT = localization.GetByLabel('UI/Industry/NonFacility')
AVAILABLE_TEXT = localization.GetByLabel('UI/Industry/Available')

@telemetry.ZONE_METHOD
def GetFacilityName(facilityID, typeID = None, solarSystemID = None):
    return _GetFacilityName(facilityID, typeID, solarSystemID)


@Memoize(0.5)
def _GetFacilityName(facilityID, typeID = None, solarSystemID = None):
    try:
        name = cfg.evelocations.Get(facilityID).name
    except (KeyError, AttributeError):
        name = None
        if typeID:
            name = evetypes.GetName(typeID)

    if not idCheckers.IsStation(facilityID) and solarSystemID:
        if name:
            if not (typeID and evetypes.GetCategoryID(typeID) == const.categoryStructure):
                name = localization.GetByLabel('UI/Industry/LocationAndFacility', locationName=cfg.evelocations.Get(solarSystemID).name, facilityName=name)
        else:
            name = cfg.evelocations.Get(solarSystemID).name
    return name


GROUPORDERINDEXES_BY_NUMGROUPS = ((0,),
 (0, 1),
 (1, 0, 2),
 (0,
  3,
  2,
  1),
 (1,
  3,
  0,
  4,
  2),
 (4,
  2,
  0,
  1,
  3,
  5))

def GetMaterialsByGroups(materialsData):
    groups = collections.defaultdict(list)
    for materialData in materialsData:
        if materialData.IsSelectable():
            invGroupID = industryUIConst.GROUP_SELECTABLEITEM
        elif materialData.IsOptional():
            invGroupID = industryUIConst.GROUP_OPTIONALITEM
        else:
            typeID = materialData.typeID
            groupID = evetypes.GetGroupID(typeID)
            categoryID = evetypes.GetCategoryID(typeID)
            invGroupID = industryUIConst.GetIndustryGroupID(typeID, groupID, categoryID)
        groups[invGroupID].append(materialData)

    if not groups:
        return []
    for groupID, materialDataList in groups.iteritems():
        materialDataList.sort(key=lambda x: (-IsShip(evetypes.GetCategoryID(x.typeID)) if x.typeID else 0, x.typeID))

    ret = groups.items()
    ret.sort(key=lambda (groupID, materials): (len(materials), groupID), reverse=True)
    numGroups = max(len(ret) - 1, 0)
    groupOrderIndexes = GROUPORDERINDEXES_BY_NUMGROUPS[numGroups]
    return [ ret[index] for index in groupOrderIndexes ]


class BlueprintMixin(object):

    def GetItem(self):
        return SlimItem(itemID=self.blueprintID, typeID=self.blueprintTypeID, ownerID=self.ownerID)

    def GetName(self):
        return evetypes.GetName(self.blueprintTypeID)

    def GetDescription(self):
        return evetypes.GetDescription(self.blueprintTypeID)

    def GetEstimatedUnitPrice(self):
        try:
            return inventorycommon.typeHelpers.GetAveragePrice(self.blueprintTypeID) or 0.0
        except KeyError:
            return 0.0

    def GetLocationName(self):
        if self.facilityID is None:
            return self.location.GetLocationName()
        return self.location.GetName()

    def GetGroupName(self):
        typeID = self.GetProductOrBlueprintTypeID()
        return GetGroupName(typeID)

    def GetProductOrBlueprintTypeID(self):
        productTypeID = self.productTypeID
        if productTypeID:
            return productTypeID
        else:
            return self.blueprintTypeID

    @telemetry.ZONE_METHOD
    def GetProductGroupAndCategory(self):
        typeID = self.GetProductOrBlueprintTypeID()
        return GetProductGroupAndCategory(typeID)

    def GetDistance(self):
        if self.facility:
            return self.facility.distance

    def GetFacilityName(self):
        if self.facility:
            return self.facility.GetName()

    def GetFacilityType(self):
        if self.facility:
            return self.facility.typeID

    def GetRunsRemainingLabel(self):
        return str(self.runsRemaining)

    def GetLabel(self):
        if self.quantity > 1:
            return '%s x %s' % (self.quantity, self.GetName())
        else:
            return self.GetName()

    def GetAvailabilityText(self):
        if self.IsInstalled():
            return INSTALLED_TEXT
        if self.IsImpounded():
            return IMPOUNTED_TEXT
        if self.facilityID is None:
            return NON_FACILITY_TEXT
        return AVAILABLE_TEXT

    def IsInstalled(self):
        return self.jobID is not None

    def IsImpounded(self):
        return bool(self.isImpounded)

    def IsSameBlueprint(self, bpData):
        if bpData is None:
            return False
        if self.blueprintTypeID != bpData.blueprintTypeID:
            return False
        if self.blueprintID != bpData.blueprintID:
            return False
        if self.locationID != bpData.locationID:
            return False
        if self.flagID != bpData.flagID:
            return False
        if self.ownerID != bpData.ownerID:
            return False
        if self.original != bpData.original:
            return False
        return True

    def IsAncientRelic(self):
        return evetypes.GetCategoryID(self.blueprintTypeID) == const.categoryAncientRelic

    def IsReactionBlueprint(self):
        return evetypes.GetGroupID(self.blueprintTypeID) in REACTION_GROUPS

    def IsWithinRange(self):
        if IsStation(self.facilityID):
            return self.facilityID == session.stationid
        if session.structureid and self.facilityID == session.structureid:
            return True
        if session.solarsystemid:
            bp = sm.GetService('michelle').GetBallpark()
            if bp is None:
                return False
            slimItem = bp.GetInvItem(self.facilityID)
            if slimItem and slimItem.categoryID != const.categoryStructure:
                return True
        return False

    def GetCopy(self):
        bpData = sm.GetService('blueprintSvc').GetBlueprintType(self.blueprintTypeID).copy()
        bpData.original = self.original
        bpData.materialEfficiency = self.materialEfficiency
        bpData.timeEfficiency = self.timeEfficiency
        bpData.runsRemaining = self.runsRemaining
        return bpData

    def GetDragData(self):
        dragData = None
        if self.IsWithinRange():
            try:
                invController = self.location.GetInvController()
            except TypeError:
                pass
            else:
                item = invController.GetItem(self.blueprintID)
                if item:
                    return KeyVal(__guid__='xtriui.InvItem', name=self.GetLabel(), item=item, rec=item)

        return KeyVal(__guid__='uicls.GenericDraggableForTypeID', typeID=self.blueprintTypeID, itemID=self.blueprintID, label=self.GetLabel())


class ActivityMixin(object):

    def GetName(self):
        return localization.GetByLabel(industryUIConst.ACTIVITY_NAMES.get(self.activityID))

    def GetHint(self):
        return self.GetName()

    def GetIcon(self):
        return industryUIConst.ACTIVITY_ICONS_SMALL[self.activityID]

    def GetTime(self, runs = 1):
        return FormatTimeInterval(self.time * runs * const.SEC)

    def GetMaterialsByGroups(self):
        return GetMaterialsByGroups(self.materials)

    def IsOmegaActivity(self):
        return self.IsClonestateRestricted(CLONE_STATE_ALPHA)

    def IsClonestateRestricted(self, clonestate = None):
        for skill in self.skills:
            maxLvl = sm.GetService('cloneGradeSvc').GetMaxSkillLevel(skill.typeID, clonestate)
            if maxLvl < skill.level:
                return True

        return False


class FacilityMixin(object):

    def GetName(self):
        return GetFacilityName(self.facilityID, self.typeID, self.solarSystemID)

    def GetTypeName(self):
        categoryID = evetypes.GetCategoryID(self.typeID)
        if categoryID == const.categoryStation:
            return evetypes.GetCategoryNameByCategory(categoryID)
        elif categoryID == const.categoryStructure:
            nameFunc = evetypes.GetName if boot.region == 'optic' else evetypes.GetEnglishName
            return '%s - %s ' % (nameFunc(self.typeID), evetypes.GetGroupName(self.typeID))
        else:
            return evetypes.GetGroupName(self.typeID)

    def GetFacilityType(self):
        return self.typeID

    def GetOwnerName(self):
        try:
            return cfg.eveowners.Get(self.ownerID).name
        except KeyError:
            return ''

    def GetHint(self):
        return self.GetName()

    def HasFacilityModifiers(self, activityID):
        for modifier in self.modifiers:
            if modifier.reference in (Reference.FACILITY, Reference.HULL, Reference.RIG) and modifier.activity == activityID:
                return True

        if self.rigModifiers:
            for modifierTypeID, activities in self.rigModifiers.iteritems():
                if activityID in activities:
                    return True

        return False

    def GetFacilityModifiersByActivityID(self):
        ret = collections.defaultdict(list)
        for modifier in self.modifiers:
            if modifier.reference in (industry.Reference.FACILITY, industry.Reference.HULL, industry.Reference.RIG) and modifier.groupID is None and modifier.categoryID is None and modifier.invTypeID is None:
                ret[modifier.activity].append(modifier)

        return ret

    def GetCostIndexByActivityID(self):
        ret = {}
        for modifier in self.modifiers:
            if modifier.reference == industry.Reference.SYSTEM:
                ret[modifier.activity] = modifier.GetAsSystemCostIndex(modifier.activity)

        return ret

    def GetCostIndex(self, activityID):
        return self.GetCostIndexByActivityID().get(activityID, 0.0)

    def CanDoActivity(self, activityID, productTypeID):
        if activityID not in self.activities:
            return False
        if evetypes.GetCategoryID(self.GetFacilityType()) == const.categoryStructure:
            accessKey = structures.services.GetServiceID(activityID, productTypeID)
            return self.serviceAccess.get(accessKey, None) is not None
        return True

    def GetServiceTaxes(self):
        if hasattr(self, 'taxRates'):
            return self.taxRates.copy()

        def _GetGroupIDs():
            if activityID in (industry.MANUFACTURING, industry.REACTION):
                for groupID in self.activities[activityID]['groups']:
                    yield groupID

                for groupID in evetypes.GetGroupIDsByCategories(self.activities[activityID]['categories']):
                    yield groupID

            else:
                yield
            raise StopIteration

        taxRates = collections.OrderedDict()
        for serviceID in sorted(structures.INDUSTRY_SERVICES):
            if serviceID in structures.META_SERVICES:
                continue
            activityID = structures.GetActivityID(serviceID)
            if activityID not in self.activities:
                continue
            for groupID in _GetGroupIDs():
                if structures.GetServiceID(activityID, None, groupID) == serviceID:
                    if isinstance(self.tax, numbers.Number):
                        tax = self.tax * 100
                    else:
                        tax = self.serviceAccess.get(serviceID)
                        if tax is not None:
                            tax *= 100
                    taxRates[serviceID] = tax
                    break

        self.taxRates = taxRates.copy()
        return taxRates


class SkillMixin(object):

    def GetName(self):
        return evetypes.GetName(self.typeID)

    def GetHint(self):
        return localization.GetByLabel('UI/InfoWindow/SkillAndLevel', skill=self.typeID, skillLevel=self.level)


class MaterialMixin(object):

    def GetName(self):
        return evetypes.GetName(self.typeID)

    def GetDescription(self):
        return evetypes.GetDescription(self.typeID)

    def GetHint(self):
        return localization.GetByLabel('UI/Common/QuantityAndItem', item=self.typeID, quantity=self.quantity)

    def GetEstimatedUnitPrice(self):
        try:
            return inventorycommon.typeHelpers.GetAveragePrice(self.typeID) or 0.0
        except KeyError:
            return 0.0

    def GetPackagedVolume(self):
        try:
            return GetPackagedVolume(self.typeID) or 0.0
        except KeyError:
            return 0.0

    def IsOptional(self):
        return bool(self.options)

    def IsSelectable(self):
        if not self.IsOptional():
            return False
        typeIDs = [ material.typeID for material in self.options ]
        return None not in typeIDs

    def IsOptionSelected(self):
        return self.typeID is not None


class JobMixin(object):

    def GetStartDateLabel(self):
        return FmtDate(DateToBlue(self.startDate), 'ls')

    def GetEndDateLabel(self):
        return FmtDate(DateToBlue(self.endDate), 'ls')

    def GetJobTimeLeftLabel(self):
        if self.status == industry.STATUS_UNSUBMITTED:
            time = self.time.total_seconds() * const.SEC
        elif self.status == industry.STATUS_INSTALLED:
            time = DateToBlue(self.endDate) - blue.os.GetWallclockTime()
        elif self.status == industry.STATUS_PAUSED:
            time = DateToBlue(self.endDate) - DateToBlue(self.pauseDate)
        elif self.status == industry.STATUS_READY:
            time = 0
        else:
            return '-'
        time = long(max(time, 0L))
        return FormatTimeInterval(time)

    def GetJobStateLabel(self):
        if self.status <= industry.STATUS_READY:
            return self.GetJobTimeLeftLabel()
        elif self.status == industry.STATUS_DELIVERED:
            if self.activityID == industry.INVENTION:
                if self.successfulRuns == 0:
                    return '<color=red>%s' % localization.GetByLabel('UI/Industry/JobFailed')
                else:
                    return localization.GetByLabel('UI/Industry/PartiallySucceeded', numSucceeded=self.successfulRuns, numTotal=self.runs)
            return localization.GetByLabel('UI/Industry/Succeeded')
        elif self.status == industry.STATUS_CANCELLED:
            color = Color.RGBtoHex(*industryUIConst.COLOR_NOTREADY)
            return '<color=%s>%s' % (color, localization.GetByLabel('UI/Industry/Cancelled'))
        elif self.status == industry.STATUS_REVERTED:
            color = Color.RGBtoHex(*industryUIConst.COLOR_NOTREADY)
            return '<color=%s>%s' % (color, localization.GetByLabel('UI/Industry/Reverted'))
        else:
            return ''

    def GetJobProgressRatio(self):
        if self.status == industry.STATUS_INSTALLED:
            timeLeft = blue.os.GetWallclockTime() - DateToBlue(self.startDate)
            totalTime = long(self.time.total_seconds()) * const.SEC
            return float(timeLeft) / totalTime
        elif self.status == industry.STATUS_PAUSED:
            timeLeft = blue.os.GetWallclockTime() - DateToBlue(self.startDate)
            totalTime = long(self.time.total_seconds()) * const.SEC
            return float(timeLeft) / totalTime
        elif self.status > industry.STATUS_COMPLETED:
            return 1.0
        else:
            return 0.0

    def GetProductTypeID(self):
        if self.product:
            return self.product.typeID
        return self.productTypeID

    def GetProductLabel(self):
        if self.activityID == industry.MANUFACTURING:
            return self.product.GetName()
        if self.activityID in (industry.RESEARCH_MATERIAL, industry.RESEARCH_TIME):
            return localization.GetByLabel('UI/Industry/ResearchedBlueprint')
        if self.activityID == industry.COPYING:
            return localization.GetByLabel('UI/Industry/BlueprintCopy')
        if self.activityID == industry.INVENTION:
            if self.product:
                return self.product.GetName()
            else:
                return localization.GetByLabel('UI/Industry/NoOutcomeSelected')

    def GetProductAmountLabel(self):
        if self.activityID in (industry.MANUFACTURING, industry.INVENTION, industry.REACTION):
            return 'x %s' % self.product.quantity
        if self.activityID == industry.RESEARCH_MATERIAL:
            diff = self.product.materialEfficiency - self.blueprint.materialEfficiency
            return '+%s%%' % diff
        if self.activityID == industry.RESEARCH_TIME:
            diff = self.product.timeEfficiency - self.blueprint.timeEfficiency
            return '+%s%%' % diff
        if self.activityID == industry.COPYING:
            return 'x %s' % self.product.quantity

    def GetProductNewBlueprint(self):
        if isinstance(self.product, industry.Blueprint) and self.product.blueprintID is None:
            return self.product

    def GetRunsRemainingCaption(self):
        if self.activityID in (industry.MANUFACTURING, industry.INVENTION):
            if self.blueprint.original:
                return localization.GetByLabel('UI/Industry/MaximumRuns')
            else:
                return localization.GetByLabel('UI/Industry/RunsRemaining')
        else:
            if self.activityID in (industry.RESEARCH_MATERIAL, industry.RESEARCH_TIME):
                return localization.GetByLabel('UI/Industry/LevelsRemaining')
            if self.activityID in (industry.COPYING, industry.REACTION):
                return localization.GetByLabel('UI/Industry/MaximumRuns')

    def GetRunsRemainingLabel(self):
        remaining = industry.MAX_RUNS_HARD_CAP if self.blueprint.original else self.blueprint.runsRemaining
        minRemaining = min(remaining, self.maxRuns)
        if minRemaining is None:
            return industry.MAX_RUNS_HARD_CAP
        return minRemaining

    def GetStatusColor(self):
        if self.status == industry.STATUS_READY:
            return (1, 1, 1, 1)
        elif self.status == industry.STATUS_INSTALLED:
            return (1, 1, 1, 0.7)
        elif self.status == industry.STATUS_PAUSED:
            return (1, 0, 0, 0.7)
        else:
            return (1, 1, 1, 0.3)

    def GetInstallerName(self):
        return cfg.eveowners.Get(self.installerID).name

    @telemetry.ZONE_METHOD
    def GetLocationsInvControllersAndLocations(self):
        ret = []
        for location in self.locations:
            invController = location.GetInvController()
            ret.append((invController, location))

        ret = sorted(ret, key=self._GetSortKey)
        return ret

    @telemetry.ZONE_METHOD
    def _GetSortKey(self, data):
        invController, location = data
        isContainer = evetypes.GetGroupID(location.typeID) in CONTAINERGROUPS
        return (location.flagID, isContainer, invController.GetName())

    def IsInstalled(self):
        return self.status >= industry.STATUS_INSTALLED

    def HasMultipleProducts(self):
        return len(self.products) > 1

    def IsProductSelectable(self):
        return self.activityID == industry.INVENTION and self.HasMultipleProducts()

    def GetGaugeValue(self):
        maxRuns = self.maxRuns
        if not maxRuns or maxRuns == industry.MAX_RUNS_HARD_CAP:
            return 0.0
        else:
            return float(self.runs) / maxRuns

    def GetModifierCaption(self, modifierCls):
        if modifierCls == industry.TimeModifier:
            return localization.GetByLabel('UI/Industry/ModifierTimeCaption')
        if modifierCls == industry.CostModifier:
            return localization.GetByLabel('UI/Industry/ModifierCostCaption')
        if modifierCls == industry.MaterialModifier:
            return localization.GetByLabel('UI/Industry/ModifierMaterialCaption')
        if modifierCls == industry.ProbabilityModifier:
            return localization.GetByLabel('UI/Industry/ModifierProbabilityCaption')

    def GetModifiers(self, modifierCls):
        modifiers = {}
        for modifier in self.input_modifiers:
            if self._FilterModifiers(modifier, modifierCls):
                if modifier.reference.value in modifiers:
                    modifiers[modifier.reference.value].amount *= modifier.amount
                else:
                    modifiers[modifier.reference.value] = copy.copy(modifier)

        return [ modifier for ref, modifier in sorted(modifiers.items()) ]

    def _FilterModifiers(self, modifier, modifierCls):
        if isinstance(modifier, industry.CostModifier) and modifier.reference == industry.Reference.SYSTEM:
            return False
        if isinstance(modifier, industry.CostModifier) and modifier.reference == industry.Reference.CLONE_STATE:
            return False
        return isinstance(modifier, modifierCls)

    def GetTimeSkillTypes(self):
        skills = []
        if self.activityID == industry.MANUFACTURING:
            skills += [const.typeIndustry, const.typeAdvancedIndustry]
        elif self.activityID == industry.COPYING:
            skills += [const.typeScience, const.typeAdvancedIndustry]
        elif self.activityID == industry.RESEARCH_TIME:
            skills += [const.typeResearch, const.typeAdvancedIndustry]
        elif self.activityID == industry.RESEARCH_MATERIAL:
            skills += [const.typeMetallurgy, const.typeAdvancedIndustry]
        elif self.activityID == industry.INVENTION:
            skills += [const.typeAdvancedIndustry]
        godma = sm.GetService('godma')
        for modifier, attribute, activityID in industryCommon.REQUIRED_SKILL_MODIFIERS:
            if self.activityID == activityID and modifier == industry.TimeModifier:
                for skill in self.required_skills:
                    if godma.GetTypeAttribute(skill.typeID, attribute):
                        skills.append(skill.typeID)

        return skills

    def GetMaterialsByGroups(self):
        if self.IsInstalled():
            return []
        return GetMaterialsByGroups(self.materials)

    def GetFacilityName(self):
        try:
            if self.facility:
                return self.facility.GetName()
            primeFacility = self.status < industry.STATUS_COMPLETED
            return sm.GetService('facilitySvc').GetFacility(self.facilityID, prime=primeFacility).GetName()
        except KeyError:
            return GetFacilityName(self.stationID, None, self.solarSystemID)

    def GetFacilityType(self):
        try:
            if self.facility:
                return self.facility.typeID
            primeFacility = self.status < industry.STATUS_COMPLETED
            return sm.GetService('facilitySvc').GetFacility(self.facilityID, prime=primeFacility).typeID
        except KeyError:
            pass

    def IsPreview(self):
        return self.blueprintID is None

    def HasError(self, errorID):
        for errorID2, args in self.errors:
            if errorID == errorID2:
                return True

        return False

    def GetCurrentActivity(self):
        return self.blueprint.activities.get(self.activityID)

    def GetCostWithoutAlphaTax(self):
        modifiers = [ x for x in self.input_modifiers if x.reference != industry.Reference.CLONE_STATE ]
        return self._get_cost_for_modifiers(modifiers)

    def GetFacilityTax(self):
        tax = 0
        if self.facility and self.facility.tax is not None:
            tax = self.facility.tax
        elif self.activity and self.facility:
            tax = self.activity.activity_tax(self.facility)
        return int(round(self._get_base_cost() * tax))

    def GetOutputLocationName(self):
        try:
            if self.IsOutputLocationSameAsFacility():
                return localization.GetByLabel('UI/Industry/Hangar')
            if self.outputLocationID:
                outputName = ''
                outputLocation = cfg.evelocations.GetIfExists(self.outputLocationID)
                if outputLocation:
                    name = outputLocation.locationName
                    if name:
                        outputName = name
                    else:
                        outputName = localization.GetByLabel('UI/Inventory/UnnamedContainer')
                if self.outputFlagID in flagCorpSAGs:
                    divisionName = sm.GetService('corp').GetHangarDivisionNameFromFlagID(self.outputFlagID)
                    if outputName:
                        outputName = '%s (%s)' % (outputName, divisionName)
                    else:
                        outputName = divisionName
                return outputName
        except StandardError as e:
            return ''

    def IsOutputLocationSameAsFacility(self):
        try:
            if self.facility.facilityID and self.facility.facilityID == self.outputLocationID:
                return True
            return False
        except StandardError:
            return False


class LocationMixin(object):

    def GetName(self):
        try:
            return self.GetInvController().GetName()
        except TypeError:
            return self.GetLocationName()

    def GetIcon(self):
        try:
            return self.GetInvController().GetIconName()
        except TypeError:
            try:
                return inventorycommon.typeHelpers.GetIcon(self.typeID).iconName
            except AttributeError:
                return None

    def GetInvController(self):
        groupID = evetypes.GetGroupID(self.typeID)
        categoryID = evetypes.GetCategoryID(self.typeID)
        if groupID in CONTAINERGROUPS:
            return StationContainer(self.itemID, self.typeID)
        if self.typeID == const.typeOffice:
            return StationCorpHangar(self.itemID, const.corpDivisionsByFlag.get(self.flagID))
        if groupID in (const.groupAssemblyArray, const.groupMobileLaboratory):
            return POSCorpHangar(self.itemID, const.corpDivisionsByFlag.get(self.flagID))
        if categoryID == const.categoryStructure:
            if self.flagID == const.flagHangar:
                return StructureItemHangar(self.itemID)
            if self.flagID in const.corpDivisionsByFlag:
                return StructureCorpHangar(self.itemID, const.corpDivisionsByFlag.get(self.flagID))
        if categoryID == const.categoryStation:
            return StationItems(self.itemID)
        raise TypeError

    def GetLocationName(self):
        if self.solarSystemID == const.locationAssetSafety or self.typeID == const.typeAssetSafetyWrap:
            typeName = evetypes.GetName(const.typeAssetSafetyWrap)
            wraps = []
            if self.ownerID == session.charid:
                wraps = sm.GetService('assetSafety').GetItemsInSafetyForCharacter()
            elif self.ownerID == session.corpid and self.canView:
                wraps = sm.GetService('assetSafety').GetItemsInSafetyForCorp()
            for asw in wraps:
                if asw['assetWrapID'] == self.itemID:
                    return '%s - %s' % (typeName, asw['wrapName'])

            return typeName
        if evetypes.GetCategoryID(self.typeID) in (const.categoryStructure, const.categoryStation):
            return cfg.evelocations.Get(self.itemID).locationName
        try:
            locationName = cfg.evelocations.Get(self.itemID).locationName
        except KeyError:
            locationName = evetypes.GetName(self.typeID)

        return '%s - %s' % (sm.GetService('map').GetItem(self.solarSystemID).itemName, locationName)


class ModifierMixin(object):

    def GetName(self):
        if self.reference == industry.Reference.BLUEPRINT:
            if isinstance(self, industry.TimeModifier):
                return localization.GetByLabel('UI/Industry/BlueprintTimeEfficiency')
            if isinstance(self, industry.MaterialModifier):
                return localization.GetByLabel('UI/Industry/BlueprintMaterialEfficiency')
            if isinstance(self, industry.ProbabilityModifier):
                return localization.GetByLabel('UI/Industry/BlueprintBaseProbability')
            if isinstance(self, industry.CostModifier):
                return localization.GetByLabel('UI/Industry/BlueprintCostModifier')
        else:
            if self.reference == industry.Reference.DECRYPTOR:
                return localization.GetByLabel('UI/Industry/OptionalDecryptor')
            if self.reference == industry.Reference.SYSTEM:
                return localization.GetByLabel('UI/Industry/SystemCostIndex')
            if self.reference == industry.Reference.FACILITY:
                return localization.GetByLabel('UI/Industry/Facility')
            if self.reference == industry.Reference.SKILLS:
                return localization.GetByLabel('UI/Industry/SkillsAndImplants')
            if self.reference == industry.Reference.DISTRICT:
                return localization.GetByLabel('UI/Industry/DistrictModifier')
            if self.reference == industry.Reference.FACTION:
                return localization.GetByLabel('UI/Industry/FactionModifier')
            if self.reference == industry.Reference.CLONE_STATE:
                return localization.GetByLabel('UI/Industry/ClonestateModifier')
            if self.reference == industry.Reference.RIG:
                return localization.GetByLabel('UI/Industry/RigModifier')
            if self.reference == industry.Reference.HULL:
                return localization.GetByLabel('UI/Industry/HullModifier')

    def GetAsPercentage(self):
        return self.GetAsBonus() * 100.0

    def GetAsBonus(self):
        return self.amount - 1.0

    def GetAsSystemCostIndex(self, activityID):
        return self.amount

    def GetPercentageLabel(self, decimals = 1):
        percent = self.GetAsPercentage()
        if isinstance(self, industry.ProbabilityModifier) and self.reference == Reference.BLUEPRINT:
            perentageText = self._GetPercentageText(100.0 + percent, decimals)
            return perentageText
        else:
            color = self.GetModifierColor()
            if percent > 0:
                perentageText = self._GetPercentageText(percent, decimals)
                return '<color=%s>+%s</color>' % (Color.RGBtoHex(*color), perentageText)
            perentageText = self._GetPercentageText(percent, decimals)
            return '<color=%s>%s</color>' % (Color.RGBtoHex(*color), perentageText)

    def _GetPercentageText(self, percent, decimals = 1):
        perentageText = '%.*f%%' % (decimals, percent)
        return perentageText

    def GetModifierColor(self):
        amount = self.GetAsBonus()
        if isinstance(self, industry.ProbabilityModifier):
            amount = -amount
        if amount < 0.0:
            return eveColor.SUCCESS_GREEN
        elif amount > 0.0:
            return eveColor.DANGER_RED
        else:
            return Color.GRAY


industry.Blueprint.extend(BlueprintMixin)
industry.Activity.extend(ActivityMixin)
industry.Facility.extend(FacilityMixin)
industry.Skill.extend(SkillMixin)
industry.Material.extend(MaterialMixin)
industry.Job.extend(JobMixin)
industry.JobData.extend(JobMixin)
industry.Location.extend(LocationMixin)
industry.modifiers.Modifier.extend(ModifierMixin)
