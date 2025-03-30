#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\util\industryCommon.py
import utillib
from carbon.common.script.sys.serviceConst import ROLE_SERVICE
from carbon.common.script.util.format import BlueToDate
from eve.common.lib import appConst as const
from eve.common.script.sys import idCheckers
from eveexceptions import UserError
import evetypes
import log
import copy
import blue
import localization
import industry
import industry.storage
import datetime
import telemetry
from UserDict import DictMixin
import inventorycommon.typeHelpers
import clonegrade
import dogma.data as dogma_data
from eveprefs import boot
from itertoolsext import Bundle
from eveservices.dogmaim import GetDogmaIMService
from caching.memoize import Memoize
CHARACTER_MODIFIERS = ((industry.SlotModifier, const.attributeManufactureSlotLimit, industry.MANUFACTURING),
 (industry.SlotModifier, const.attributeMaxLaborotorySlots, industry.RESEARCH_TIME),
 (industry.SlotModifier, const.attributeMaxLaborotorySlots, industry.RESEARCH_MATERIAL),
 (industry.SlotModifier, const.attributeMaxLaborotorySlots, industry.COPYING),
 (industry.SlotModifier, const.attributeMaxLaborotorySlots, industry.INVENTION),
 (industry.SlotModifier, const.attributeReactionSlotLimit, industry.REACTION),
 (industry.TimeModifier, const.attributeManufactureTimeMultiplier, industry.MANUFACTURING),
 (industry.TimeModifier, const.attributeManufacturingTimeResearchSpeed, industry.RESEARCH_TIME),
 (industry.TimeModifier, const.attributeMineralNeedResearchSpeed, industry.RESEARCH_MATERIAL),
 (industry.TimeModifier, const.attributeCopySpeedPercent, industry.COPYING),
 (industry.TimeModifier, const.attributeInventionReverseEngineeringResearchSpeed, industry.INVENTION),
 (industry.TimeModifier, const.attributeReactionTimeMultiplier, industry.REACTION))
REQUIRED_SKILL_MODIFIERS = ((industry.TimeModifier, const.attributeManufactureTimePerLevel, industry.MANUFACTURING),)
BLUEPRINT_MODIFIERS = ((industry.CostModifier, const.attributeJobCostMultiplier, None),)
ACCOUNT_ENTRY_TYPES = {industry.MANUFACTURING: const.refManufacturing,
 industry.REACTION: const.refReaction,
 industry.RESEARCH_TIME: const.refResearchingTimeProductivity,
 industry.RESEARCH_MATERIAL: const.refResearchingMaterialProductivity,
 industry.COPYING: const.refCopying,
 industry.INVENTION: const.refResearchingTechnology}

def GetErrorLabel(error, *args):
    if error == industry.Error.INVALID_OWNER:
        return localization.GetByLabel('UI/Industry/Errors/InvalidOwner')
    elif error == industry.Error.INVALID_CHARACTER:
        return localization.GetByLabel('UI/Industry/Errors/InvalidCharacter')
    elif error == industry.Error.INVALID_CORPORATION:
        return localization.GetByLabel('UI/Industry/Errors/InvalidCorporation')
    elif error == industry.Error.INVALID_RUNS:
        return localization.GetByLabel('UI/Industry/Errors/InvalidRuns')
    elif error == industry.Error.INVALID_LICENSED_RUNS:
        return localization.GetByLabel('UI/Industry/Errors/InvalidLicensedRuns')
    elif error == industry.Error.INVALID_INPUT_LOCATION:
        return localization.GetByLabel('UI/Industry/Errors/InvalidInputLocation')
    elif error == industry.Error.INVALID_OUTPUT_LOCATION:
        return localization.GetByLabel('UI/Industry/Errors/InvalidOutputLocation')
    elif error == industry.Error.INVALID_PRODUCT:
        return localization.GetByLabel('UI/Industry/Errors/InvalidProduct')
    elif error == industry.Error.INVALID_COST:
        return localization.GetByLabel('UI/Industry/Errors/InvalidCost')
    elif error == industry.Error.INVALID_ACTIVITY:
        return localization.GetByLabel('UI/Industry/Errors/InvalidActivity')
    elif error == industry.Error.INVALID_FACILITY:
        return localization.GetByLabel('UI/Industry/Errors/InvalidFacility')
    elif error == industry.Error.MISSING_ACTIVITY:
        return localization.GetByLabel('UI/Industry/Errors/MissingActivity')
    elif error == industry.Error.MISSING_ROLE:
        return localization.GetByLabel('UI/Industry/Errors/MissingRole')
    elif error == industry.Error.MISSING_BLUEPRINT:
        return localization.GetByLabel('UI/Industry/Errors/MissingBlueprint')
    elif error == industry.Error.MISSING_FACILITY:
        return localization.GetByLabel('UI/Industry/Errors/MissingFacility')
    elif error == industry.Error.MISSING_MATERIAL:
        return localization.GetByLabel('UI/Industry/Errors/MissingMaterial')
    elif error == industry.Error.MISSING_INPUT_LOCATION:
        return localization.GetByLabel('UI/Industry/Errors/MissingInputLocation')
    elif error == industry.Error.MISSING_OUTPUT_LOCATION:
        return localization.GetByLabel('UI/Industry/Errors/MissingOutputLocation')
    elif error == industry.Error.ACCOUNT_FUNDS:
        return localization.GetByLabel('UI/Industry/Errors/AccountFunds')
    elif error == industry.Error.ACCOUNT_ACCESS:
        return localization.GetByLabel('UI/Industry/Errors/AccountAccess')
    elif error == industry.Error.ACCOUNT_INVALID:
        return localization.GetByLabel('UI/Industry/Errors/AccountInvalid')
    elif error == industry.Error.INCOMPATIBLE_ACTIVITY:
        return localization.GetByLabel('UI/Industry/Errors/IncompatibleActivity')
    elif error == industry.Error.BLUEPRINT_ACCESS:
        return localization.GetByLabel('UI/Industry/Errors/BlueprintAccess')
    elif error == industry.Error.BLUEPRINT_INSTALLED:
        return localization.GetByLabel('UI/Industry/Errors/BlueprintInstalled')
    elif error == industry.Error.BLUEPRINT_WRONG_FACILITY:
        return localization.GetByLabel('UI/Industry/Errors/BlueprintWrongFacility')
    elif error == industry.Error.MISMATCH_COST:
        return localization.GetByLabel('UI/Industry/Errors/MismatchCost')
    elif error == industry.Error.MISMATCH_TAX:
        return localization.GetByLabel('UI/Industry/Errors/MismatchTax')
    elif error == industry.Error.MISMATCH_TIME:
        return localization.GetByLabel('UI/Industry/Errors/MismatchTime')
    elif error == industry.Error.MISMATCH_MATERIAL:
        return localization.GetByLabel('UI/Industry/Errors/MismatchMaterial')
    elif error == industry.Error.INVALID_BLUEPRINT_LOCATION:
        return localization.GetByLabel('UI/Industry/Errors/InvalidBlueprintLocation')
    elif error == industry.Error.MISSING_SKILL:
        return localization.GetByLabel('UI/Industry/Errors/MissingSkill')
    elif error == industry.Error.SLOTS_FULL:
        return localization.GetByLabel('UI/Industry/Errors/SlotsFull')
    elif error == industry.Error.RESEARCH_LIMIT:
        return localization.GetByLabel('UI/Industry/Errors/ResearchLimit')
    elif error == industry.Error.FACILITY_DISTANCE:
        return localization.GetByLabel('UI/Industry/Errors/FacilityDistance')
    elif error == industry.Error.FACILITY_ACTIVITY:
        return localization.GetByLabel('UI/Industry/Errors/FacilityActivity')
    elif error == industry.Error.FACILITY_TYPE:
        return localization.GetByLabel('UI/Industry/Errors/FacilityTypeError')
    elif error == industry.Error.RUN_LENGTH:
        numDays = industry.MAX_RUN_LENGTH * const.SEC / const.DAY
        return localization.GetByLabel('UI/Industry/Errors/RunLength', numDays=numDays)
    elif error == industry.Error.FACILITY_OFFLINE:
        return localization.GetByLabel('UI/Industry/Errors/FacilityOffline')
    elif error == industry.Error.FACILITY_DENIED:
        return localization.GetByLabel('UI/Industry/Errors/FacilityDenied')
    elif error == industry.Error.INPUT_ACCESS:
        return localization.GetByLabel('UI/Industry/Errors/InputAccess')
    elif error == industry.Error.INVALID_MATERIAL_EFFICIENCY:
        return localization.GetByLabel('UI/Industry/Errors/InvalidMaterialEfficiency')
    elif error == industry.Error.INVALID_TIME_EFFICIENCY:
        return localization.GetByLabel('UI/Industry/Errors/InvalidTimeEfficiency')
    elif error == industry.Error.OUTPUT_OVERFLOW:
        return localization.GetByLabel('UI/Industry/Errors/InsufficientSpaceInOutputLocation')
    elif error == industry.Error.STANDINGS_RESTRICTION:
        standings_restriction = args[0]
        if idCheckers.IsCorporation(standings_restriction['to_id']):
            label_path = 'UI/Standings/RestrictedCorporation'
        else:
            label_path = 'UI/Standings/Restricted'
        return localization.GetByLabel(label_path, **standings_restriction)
    else:
        return error.name


def ItemLocationFlag(location):
    if location.typeID == const.typeOffice:
        return location.flagID
    if evetypes.GetCategoryID(location.typeID) in (const.categoryStarbase, const.categoryStructure):
        return location.flagID
    if evetypes.GetGroupID(location.typeID) == const.groupStation:
        return location.flagID


def ItemOutputFlag(location, itemFlagID = None):
    typeID = location.typeID
    groupID = evetypes.GetGroupID(typeID)
    categoryID = evetypes.GetCategoryID(typeID)
    if groupID == const.groupAuditLogSecureContainer:
        if itemFlagID == const.flagLocked:
            return const.flagLocked
        return const.flagUnlocked
    if typeID == const.typeOffice or groupID == const.groupStation or categoryID in (const.categoryStarbase, const.categoryStructure):
        return location.flagID
    return const.flagNone


def RolesAtLocation(session, locationID):
    if session.role & ROLE_SERVICE:
        return 18446744073709551615L
    elif locationID == session.hqID:
        return session.rolesAtAll | session.rolesAtHQ
    elif locationID == session.baseID:
        return session.rolesAtAll | session.rolesAtBase
    else:
        return session.rolesAtAll | session.rolesAtOther


def CanViewItem(session, ownerID, locationID, flagID):
    if session.role & ROLE_SERVICE:
        return True
    if ownerID == session.charid:
        return True
    if idCheckers.IsCorporation(ownerID):
        return RolesAtLocation(session, locationID) & (const.corpHangarQueryRolesByFlag.get(flagID, 0) | const.corpRoleFactoryManager)
    return False


def CanTakeItem(session, ownerID, locationID, flagID, container = False):
    if session.role & ROLE_SERVICE:
        return True
    if ownerID == session.charid:
        return True
    if idCheckers.IsCorporation(ownerID):
        if container:
            required = const.corpContainerTakeRolesByFlag.get(flagID, 0) | const.corpRoleFactoryManager
        else:
            required = const.corpHangarTakeRolesByFlag.get(flagID, 0) | const.corpRoleFactoryManager
        return RolesAtLocation(session, locationID) & required == required
    return False


def OwnerAccess(session, ownerID, locationID = None, flagID = None):
    if not session or session.role & ROLE_SERVICE:
        return True
    if idCheckers.IsCharacter(ownerID):
        if session.charid != ownerID and session.role & ROLE_SERVICE == 0:
            return False
    elif idCheckers.IsCorporation(ownerID) and not idCheckers.IsNPCCorporation(ownerID):
        if not session.corprole & const.corpRoleFactoryManager:
            return False
        if session.corpid != ownerID and session.role & ROLE_SERVICE == 0:
            return False
    else:
        return False
    if locationID and flagID and not CanViewItem(session, ownerID, locationID, flagID):
        return False
    return True


def AssertBlueprintAccess(session, ownerID, locationID = None, flagID = None):
    if not OwnerAccess(session, ownerID, locationID, flagID):
        raise UserError('IndustryBlueprintAccessDenied')


def AssertLocationAccess(session, ownerID, locationID = None, flagID = None):
    if not OwnerAccess(session, ownerID, locationID, flagID):
        raise UserError('IndustryLocationAccessDenied')


def AssertFacilityAccess(session, ownerID, facility):
    facilityType = facility['typeID']
    facilityID = facility['facilityID']
    if idCheckers.IsStation(facilityID):
        return
    if evetypes.GetCategoryID(facilityType) == const.categoryStructure:
        return
    if not OwnerAccess(session, ownerID):
        raise UserError('IndustryFacilityAccessDenied')


def AssertJobAccess(session, ownerID):
    if not OwnerAccess(session, ownerID):
        raise UserError('IndustryJobAccessDenied')


@telemetry.ZONE_METHOD
def AttachSessionToJob(job, session):
    if job and session:
        job.characterID = session.charid
        job.corporationID = session.corpid
        job.roles = RolesAtLocation(session, job.facilityID)


def JobStatus(data):
    now = blue.os.GetWallclockTime()
    if isinstance(data.endDate, datetime.datetime):
        now = BlueToDate(now)
    if data.status == industry.STATUS_INSTALLED and data.endDate < now:
        return industry.STATUS_READY
    elif data.status == industry.STATUS_PAUSED and data.pauseDate > data.endDate:
        return industry.STATUS_READY
    else:
        return data.status


@Memoize
def GetBlueprintsByTypeID(invTypeID):
    blueprints = set()
    if not invTypeID:
        return blueprints
    for typeID in cfg.blueprints.filter_keys('productTypeID', invTypeID):
        blueprints.add(typeID)

    blueprints.discard(None)
    return blueprints


@Memoize
def GetBlueprintsByProductGroup(groupID):
    blueprints = set()
    for typeIDInGroup in evetypes.GetTypeIDsByGroup(groupID):
        for typeID in cfg.blueprints.filter_keys('productTypeID', typeIDInGroup):
            blueprints.add(typeID)

    blueprints.discard(None)
    return blueprints


@Memoize
def GetBlueprintsByProductCategory(categoryID):
    blueprints = set()
    for groupID in evetypes.GetGroupIDsByCategory(categoryID):
        for typeIDInGroup in evetypes.GetTypeIDsByGroup(groupID):
            for typeID in cfg.blueprints.filter_keys('productTypeID', typeIDInGroup):
                blueprints.add(typeID)

    blueprints.discard(None)
    return blueprints


def BlueprintInstance(data):
    blueprint = cfg.blueprints[data.typeID].copy()
    blueprint.blueprintID = data.itemID
    blueprint.timeEfficiency = data.timeEfficiency
    blueprint.materialEfficiency = data.materialEfficiency
    blueprint.runsRemaining = data.runs
    blueprint.quantity = max(data.quantity, 1)
    blueprint.singleton = True if data.quantity < 0 else False
    blueprint.original = data.quantity != -2 and evetypes.GetCategoryID(data.typeID) != const.categoryAncientRelic
    blueprint.locationID = data.locationID
    blueprint.locationTypeID = data.locationTypeID
    blueprint.locationFlagID = data.locationFlagID
    blueprint.flagID = data.flagID
    blueprint.facilityID = data.facilityID
    blueprint.ownerID = data.ownerID
    blueprint.jobID = data.jobID
    blueprint.isImpounded = data.isImpounded
    blueprint.solarSystemID = data.solarSystemID
    return blueprint


def JobData(data, blueprint):
    job = industry.JobData(blueprint, data.activityID)
    job.data = data
    job.jobID = data.jobID
    job.blueprintID = data.blueprintID
    job.blueprintTypeID = data.blueprintTypeID
    job.blueprintLocationID = data.blueprintLocationID
    job.blueprintLocationFlagID = data.blueprintLocationFlagID
    job.facilityID = data.facilityID
    job.ownerID = data.ownerID
    job.status = JobStatus(data)
    job.installerID = data.installerID
    job.completedCharacterID = data.completedCharacterID
    job.solarSystemID = data.solarSystemID
    job.stationID = data.stationID
    job.startDate = BlueToDate(data.startDate)
    job.endDate = BlueToDate(data.endDate)
    job.pauseDate = BlueToDate(data.pauseDate) if data.pauseDate else None
    job.runs = data.runs
    job.licensedRuns = data.licensedRuns
    job.successfulRuns = data.successfulRuns
    job.cost = data.cost
    job.time = datetime.timedelta(seconds=data.timeInSeconds)
    job.probability = data.probability if data.probability is not None else 1
    job.productTypeID = data.productTypeID
    job.optionalTypeID = data.optionalTypeID
    job.optionalTypeID2 = data.optionalTypeID2
    job.outputLocationID = data.outputLocationID
    job.outputFlagID = data.outputFlagID
    return job


def Facility(data):
    facility = industry.Facility(facilityID=data['facilityID'], typeID=data['typeID'], ownerID=data['ownerID'], tax=data['tax'], solarSystemID=data['solarSystemID'], online=data['online'], serviceAccess=data['serviceAccess'], sccTaxModifier=data['sccTaxModifier'])
    facility.rigModifiers = data['rigModifiers']
    globalModifiers = data['globalModifiers']
    for activityID, (timeModifiers, materialModifiers, costModifiers, categories, groups, invTypes) in data['activities'].iteritems():
        blue.pyos.BeNice()
        blueprints = set()
        for categoryID in categories:
            blueprints.update(GetBlueprintsByProductCategory(categoryID))

        for groupID in groups:
            blueprints.update(GetBlueprintsByProductGroup(groupID))

        for typeID in invTypes:
            blueprints.update(GetBlueprintsByTypeID(typeID))

        facility.update_activity(activityID, blueprints, categories, groups, invTypes)
        if globalModifiers['faction'] != 1.0:
            facility.modifiers.append(industry.CostModifier(amount=globalModifiers['faction'], reference=industry.Reference(industry.Reference.FACTION.value), activity=activityID, blueprints=None, categoryID=None, groupID=None))
        if globalModifiers['system'].get(activityID) not in (0.0, 1.0):
            facility.modifiers.append(industry.CostModifier(amount=globalModifiers['system'][activityID], reference=industry.Reference(industry.Reference.SYSTEM.value), activity=activityID, blueprints=None, categoryID=None, groupID=None))
        mapping = [(timeModifiers, industry.TimeModifier), (materialModifiers, industry.MaterialModifier), (costModifiers, industry.CostModifier)]
        for modifiers, cls in mapping:
            for amount, categoryID, groupID, invTypeID, reference in modifiers:
                if categoryID:
                    blueprints = GetBlueprintsByProductCategory(categoryID) | {0}
                elif groupID:
                    blueprints = GetBlueprintsByProductGroup(groupID) | {0}
                elif invTypeID:
                    blueprints = GetBlueprintsByTypeID(invTypeID) | {0}
                else:
                    blueprints = None
                facility.modifiers.append(cls(amount=amount, reference=industry.Reference(reference), activity=activityID, blueprints=blueprints, categoryID=categoryID, groupID=groupID, invTypeID=invTypeID))

    return facility


def CheckLocationCapacity(job, locationTypeID):
    if cfg.IsCargoContainer(utillib.KeyVal(singleton=True, groupID=evetypes.GetGroupID(locationTypeID))):
        containerCapacity = evetypes.GetCapacity(locationTypeID)
        requiredVolume = round(sum([ inventorycommon.util.GetTypeVolume(material.typeID, material.quantity) for material in job.output ]), 2)
        if requiredVolume > containerCapacity:
            return False
    return True


@telemetry.ZONE_METHOD
def MatchLocation(job, locationID = None, flagID = None, checkCapacity = False):
    for location in job.locations:
        if location.flagID == flagID and location.itemID == locationID and (not checkCapacity or CheckLocationCapacity(job, location.typeID)):
            return copy.copy(location)

    for location in job.locations:
        if location.flagID == flagID and location.ownerID == job.ownerID and (not checkCapacity or CheckLocationCapacity(job, location.typeID)):
            return copy.copy(location)

    if locationID and idCheckers.IsCorporation(job.ownerID):
        if idCheckers.IsStation(job.facility.facilityID):
            typeID = cfg.stations.Get(job.facility.facilityID).stationTypeID
        else:
            typeID = sm.GetService('structureDirectory').GetStructureInfo(job.facility.facilityID).typeID
        return industry.Location(itemID=job.facility.facilityID, ownerID=job.ownerID, flagID=const.flagCorpDeliveries, typeID=typeID)
    try:
        firstLocation = job.locations[0]
        if not checkCapacity or CheckLocationCapacity(job, firstLocation.typeID):
            return copy.copy(firstLocation)
    except IndexError:
        pass


@telemetry.ZONE_METHOD
def GetDecryptors(job):
    if job.activityID == industry.INVENTION:
        options = [industry.Material(mutable=True)]
        for typeID in evetypes.GetTypeIDsByGroup(const.groupDecryptors):
            options.append(industry.Material(mutable=True, typeID=typeID, quantity=1, modifiers=[industry.MaxRunsModifier(dogma_data.get_type_attribute(typeID, const.attributeInventionMaxRunModifier), output=True, activity=industry.INVENTION, reference=industry.Reference.DECRYPTOR),
             industry.MaterialModifier(dogma_data.get_type_attribute(typeID, const.attributeInventionMEModifier) / 100.0, output=True, activity=industry.INVENTION, reference=industry.Reference.DECRYPTOR),
             industry.TimeModifier(dogma_data.get_type_attribute(typeID, const.attributeInventionPEModifier) / 100.0, output=True, activity=industry.INVENTION, reference=industry.Reference.DECRYPTOR),
             industry.ProbabilityModifier(dogma_data.get_type_attribute(typeID, const.attributeInventionPropabilityMultiplier), activity=industry.INVENTION, reference=industry.Reference.DECRYPTOR)]))

        decryptor = industry.Material(mutable=True, options=options)
        if job.request:
            allTypes = decryptor.all_types()
            for typeID in job.request['materials']:
                if typeID in allTypes:
                    decryptor.select(typeID)

        if getattr(job, 'optionalTypeID', None) in decryptor.all_types():
            decryptor.select(job.optionalTypeID)
        if getattr(job, 'optionalTypeID2', None) in decryptor.all_types():
            decryptor.select(job.optionalTypeID2)
        return [decryptor]
    return []


def GetJobModifiers(job, characterID):
    if boot.role == 'client':
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        cloneGrade = sm.GetService('cloneGradeSvc').GetCloneGrade()
    else:
        dogmaLocation = GetDogmaIMService().GetDogmaLocation(characterID, const.groupCharacter)
        cloneGrade = sm.GetService('subscriptionMgr').GetCloneGradeFromCharID(characterID)
    modifiers = []
    for modifier, attribute, activity in BLUEPRINT_MODIFIERS:
        amount = dogma_data.get_type_attribute(job.blueprint.blueprintTypeID, attribute)
        if amount is not None:
            modifiers.append(modifier(amount, reference=industry.Reference.BLUEPRINT, activity=activity))

    for modifier, attribute, activity in REQUIRED_SKILL_MODIFIERS:
        for skill in job.required_skills:
            amount = dogma_data.get_type_attribute(skill.typeID, attribute)
            if amount is not None:
                amount = 1.0 + amount * job.skills[skill.typeID] / 100.0
                modifiers.append(modifier(amount, reference=industry.Reference.SKILLS, activity=activity))

    attributeValues = dogmaLocation.GetIndustryCharacterModifiers(characterID)
    for modifier, attribute, activity in CHARACTER_MODIFIERS:
        modifiers.append(modifier(amount=attributeValues[attribute], activity=activity, reference=industry.Reference.SKILLS))

    if cloneGrade == clonegrade.CLONE_STATE_ALPHA:
        m = industry.CostModifier(clonegrade.CLONE_STATE_INDUSTRY_TAX, additive=True, reference=industry.Reference.CLONE_STATE, activity=None)
        modifiers.append(m)
    return modifiers


def GetOptionalMaterials(job):
    return GetDecryptors(job)


@Memoize
def GetBlueprintPrice(typeID, activityID):
    try:
        if boot.role == 'client':
            blueprint = sm.GetService('blueprintSvc').GetBlueprintType(typeID)
        else:
            blueprint = sm.GetService('blueprintManager').GetBlueprintType(typeID)
        if activityID in industry.SCIENCE_ACTIVITIES:
            activityID = industry.MANUFACTURING
        materials = blueprint.activities[activityID].materials
        return sum([ GetBlueprintPrice(material.typeID, activityID) * material.quantity for material in materials ])
    except (KeyError, UserError):
        pass

    try:
        if typeID is not None:
            adjustedAveragePrice = inventorycommon.typeHelpers.GetAdjustedAveragePrice(typeID)
            if adjustedAveragePrice:
                return adjustedAveragePrice
    except KeyError:
        pass

    log.LogError('industryCommon.GetBlueprintPrice missing adjustedAveragePrice for type: ', typeID)
    return 0


class JobPrices(DictMixin):

    def __init__(self, activityID):
        self.activityID = activityID

    def __getitem__(self, key):
        return GetBlueprintPrice(key, self.activityID)

    def __setitem__(self, key, item):
        raise RuntimeError('Job pricing is immutable')

    def __delitem__(self, key):
        raise RuntimeError('Job pricing is immutable')

    @staticmethod
    def keys():
        return evetypes.GetAllTypeIDs()


def IsBlueprintCategory(categoryID):
    return categoryID in (const.categoryBlueprint, const.categoryAncientRelic)


@Memoize
def GetIndustryModifiers(typeID):
    activityModifierSourcesStorage = industry.storage.ActivityModifierSourcesStorage()
    try:
        typeActivityModifiers = activityModifierSourcesStorage[typeID]
    except KeyError:
        return []

    typeModifiers = []
    for activityID, activityName in industry.ACTIVITY_NAMES.iteritems():
        activityModifiers = getattr(typeActivityModifiers, activityName, None)
        if not activityModifiers:
            continue
        for modifierID, modifierName in industry.MODIFIERS.iteritems():
            modifiers = getattr(activityModifiers, modifierName, None)
            if not modifiers:
                continue
            for modifier in modifiers:
                productCategories, productGroups = _GetCategoriesGroupsForActivityFilter(modifier.filterID)
                typeModifiers.append(Bundle(typeID=typeID, activityID=activityID, modifierType=modifierID, attributeID=modifier.dogmaAttributeID, productGroups=productGroups, productCategories=productCategories))

    return typeModifiers


@Memoize
def _GetCategoriesGroupsForActivityFilter(filterID):
    if filterID is None:
        return (None, None)
    activityTargetFiltersStorage = industry.storage.ActivityTargetFiltersStorage()
    try:
        targetFilter = activityTargetFiltersStorage[filterID]
    except KeyError:
        log.LogWarn('industryCommon._GetGroupCategoriesForActivityFilter called for unknown filter', filterID)
        return (None, None)

    productCategories = set(targetFilter.categoryIDs or [])
    productGroups = set(targetFilter.groupIDs or [])
    if not productCategories and not productGroups:
        log.LogWarn('industryCommon._GetCategoriesGroupsForActivityFilter found modifier filter with no filtered product types', filterID)
        return (None, None)
    return (productCategories, productGroups)


@Memoize
def GetActivities():
    return industry.storage.ActivitiesStorage()


@Memoize
def GetAssemblyLine(assemblyLineTypeID):
    return Bundle(industry.storage.AssemblylineStorage()[assemblyLineTypeID])


@Memoize
def GetInstallationType(typeID):
    return industry.storage.InstallationTypeStorage()[typeID]
