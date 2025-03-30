#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\industry\blueprintSvc.py
from collections import defaultdict
import blue
import evetypes
import telemetry
import industry
import threadutils
from carbon.common.script.sys.service import Service
from eve.common.lib import appConst as const
from eve.common.script.sys import idCheckers
from eve.common.script.util import industryCommon
from caching.memoize import Memoize
from eveexceptions import UserError
import eve.client.script.industry.mixins

class BlueprintService(Service):
    __guid__ = 'svc.blueprintSvc'
    __servicename__ = 'Blueprint'
    __displayname__ = 'Blueprint Service'
    __notifyevents__ = ['OnBlueprintsUpdated', 'OnSessionChanged', 'OnIndustryJob']

    def Run(self, *args, **kwargs):
        Service.Run(self, *args, **kwargs)
        self.blueprintManager = sm.RemoteSvc('blueprintManager')
        self.blueprintLimit = self.blueprintManager.GetLimits()['maxBlueprintResults']
        self.bpSummaries = {}
        self.blueprintChanges = defaultdict(dict)

    def OnBlueprintsUpdated(self, ownerID):
        self.GetAllBlueprintsForOwner.clear_memoized(self, ownerID)
        self.GetOwnerBlueprintsAtFacility.clear_memoized()
        self.bpSummaries.pop(ownerID, None)
        sm.ScatterEvent('OnBlueprintReload', ownerID)

    @telemetry.ZONE_METHOD
    def OnIndustryJob(self, jobID, ownerID, blueprintID, installerID, status, successfulRuns):
        self.blueprintChanges[ownerID][blueprintID] = (jobID, status)
        self._UpdateOnIndustryJobChange(ownerID)

    @threadutils.throttled(3.0)
    def _UpdateOnIndustryJobChange(self, ownerID):
        blueprintChangesForOwner = self.blueprintChanges.pop(ownerID, None)
        if not blueprintChangesForOwner:
            return
        self.GetOwnerBlueprintsAtFacility.clear_memoized()
        for blueprint in self.GetAllBlueprintsForOwner(ownerID)[0]:
            if not blueprintChangesForOwner:
                break
            changeInfoForBlueprint = blueprintChangesForOwner.pop(blueprint.itemID, None)
            if changeInfoForBlueprint is None:
                continue
            jobID, status = changeInfoForBlueprint
            if status < industry.STATUS_COMPLETED:
                blueprint.jobID = jobID
            else:
                blueprint.jobID = None

    def OnSessionChanged(self, isRemote, session, change):
        if 'corprole' in change:
            self.OnBlueprintsUpdated(session.corpid)

    @telemetry.ZONE_METHOD
    def GetBlueprintType(self, blueprintTypeID, isCopy = False):
        try:
            ret = cfg.blueprints[blueprintTypeID]
            if isCopy or evetypes.GetCategoryID(blueprintTypeID) == const.categoryAncientRelic:
                ret = ret.copy()
                ret.original = False
            return ret
        except KeyError:
            raise UserError('IndustryBlueprintNotFound')

    def GetBlueprintTypeCopy(self, typeID, original = True, runsRemaining = None, materialEfficiency = None, timeEfficiency = None):
        bpData = self.GetBlueprintType(typeID).copy()
        bpData.original = original and evetypes.GetCategoryID(typeID) != const.categoryAncientRelic
        if runsRemaining is not None:
            bpData.runsRemaining = runsRemaining
        if materialEfficiency is not None:
            bpData.materialEfficiency = materialEfficiency
        if timeEfficiency is not None:
            bpData.timeEfficiency = timeEfficiency
        return bpData

    @telemetry.ZONE_METHOD
    def GetBlueprintItem(self, blueprintID):
        return industryCommon.BlueprintInstance(self.blueprintManager.GetBlueprintData(blueprintID))

    @Memoize(10)
    def GetBlueprintItemMemoized(self, blueprintID):
        return self.GetBlueprintItem(blueprintID)

    def GetBlueprint(self, blueprintID, blueprintTypeID, isCopy = False):
        try:
            return self.GetBlueprintItem(blueprintID)
        except UserError:
            return self.GetBlueprintType(blueprintTypeID, isCopy=isCopy)

    @staticmethod
    def GetBlueprintByProduct(productTypeID):
        try:
            blueprint = cfg.blueprints.index('productTypeID', productTypeID)
            if blueprint and evetypes.IsPublished(blueprint.blueprintTypeID):
                return blueprint
            return None
        except KeyError:
            return None

    @telemetry.ZONE_METHOD
    def GetOwnerBlueprints(self, ownerID, facilityID = None):
        if facilityID is None:
            return self.GetAllBlueprintsForOwner(ownerID)
        return self.GetOwnerBlueprintsAtFacility(ownerID, facilityID)

    @Memoize(15)
    def GetOwnerBlueprintsAtFacility(self, ownerID, facilityID):
        bps = []
        if ownerID not in self.bpSummaries:
            bps, bpCounts = self.GetAllBlueprintsForOwner(ownerID)
        else:
            bpCounts = self.bpSummaries[ownerID]
        if not bps:
            bps, _ = self.blueprintManager.GetBlueprintDataByOwner(ownerID, facilityID)
            bps = self._AttachFacilities(bps)
        return ([ bp for bp in bps if bp.facilityID == facilityID ], bpCounts)

    @Memoize(15)
    def GetAllBlueprintsForOwner(self, ownerID):
        bps, bpCounts = self.blueprintManager.GetBlueprintDataByOwner(ownerID, None)
        bps = self._AttachFacilities(bps)
        self.bpSummaries[ownerID] = bpCounts
        return (bps, bpCounts)

    def GetCharacterBlueprints(self, facilityID = None):
        return self.GetOwnerBlueprints(session.charid, facilityID)

    def GetCorporationBlueprints(self, facilityID = None):
        return self.GetOwnerBlueprints(session.corpid, facilityID)

    def CanSeeCorpBlueprints(self):
        if idCheckers.IsNPC(session.corpid):
            return False
        return session.corprole & (const.corpRoleCanRentResearchSlot | const.corpRoleFactoryManager | const.corpRoleCanRentFactorySlot) > 0

    def _AttachFacilities(self, blueprints):
        locations = set()
        facilities = set()
        blueprintObjects = []
        for data in blueprints:
            try:
                blueprint = industryCommon.BlueprintInstance(data)
                blueprintObjects.append(blueprint)
                if blueprint.locationTypeID not in (const.typeAssetSafetyWrap, const.typeOffice):
                    locations.add(blueprint.locationID)
                if blueprint.facilityID:
                    locations.add(blueprint.facilityID)
                    facilities.add(blueprint.facilityID)
                blue.pyos.BeNice()
            except KeyError:
                self.LogError('Unable to load blueprint instance: ', data)

        cfg.evelocations.Prime(locations)
        facilitiesByID = {}
        if len(facilities):
            facilitiesByID = {f.facilityID:f for f in sm.GetService('facilitySvc').GetFacilities(facilities)}
        for blueprint in blueprintObjects:
            if blueprint.facilityID:
                try:
                    blueprint.facility = facilitiesByID[blueprint.facilityID]
                except KeyError:
                    self.LogWarn('Could not load facility', blueprint.facilityID)

        return blueprintObjects
