#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\skills\skillplan\skillPlanService.py
import log
import logging
import uuid
from collections import defaultdict
import uthread
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst
from carbonui.uicore import uicore
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.common.script.sys.idCheckers import IsPlayerCorporation
from eveexceptions import UserError
from localization import GetByLabel
from skills.skillplan import skillPlanFSDLoader, skillPlanConst, skillPlanSignals, skillPlanValidation
from skills.skillplan.controllers.certifiedSkillPlanController import CertifiedSkillPlanController
from skills.skillplan.controllers.corpSkillPlanController import CorpSkillPlanController
from skills.skillplan.controllers.personalSkillPlanController import PersonalSkillPlanController
from skills.skillplan.errors import SkillPlanConnectionError
from skills.skillplan.grpc import corpSkillPlanRequest, personalSkillPlanRequest
from skills.skillplan.grpc.message_bus.corpSkillPlanNoticeMessenger import CorpSkillPlanNoticeMessenger
from skills.skillplan.milestone.milestoneService import PersonalSkillPlanMilestoneService, CorpSkillPlanMilestoneService
from stackless_response_router.exceptions import TimeoutException
logger = logging.getLogger(__name__)
skillPlanSvc = None

def GetSkillPlanSvc():
    global skillPlanSvc
    if skillPlanSvc is None:
        skillPlanSvc = SkillPlanService()
    return skillPlanSvc


class SkillPlanService(object):
    __notifyevents__ = ['OnSessionReset', 'OnSessionChanged', 'OnSkillLevelsTrained']

    def __init__(self):
        self.personalCache = None
        self.corpCache = None
        self.certifiedCache = {}
        self.certifiedByCareerPathID = defaultdict(list)
        self.trackedPlanID = None
        self._PrimeCertifiedCache()
        self.personalMilestoneSvc = PersonalSkillPlanMilestoneService()
        self.corpMilestoneSvc = CorpSkillPlanMilestoneService()
        self.ConnectCorpNotices()
        sm.RegisterNotify(self)

    def ConnectCorpNotices(self):
        self.corpSkillPlanMessenger = CorpSkillPlanNoticeMessenger(sm.GetService('publicGatewaySvc'))
        self.corpSkillPlanMessenger.on_created.connect(self.OnRemoteCorpSkillPlanCreated)
        self.corpSkillPlanMessenger.on_deleted.connect(self.OnRemoteCorpSkillPlanDeleted)
        self.corpSkillPlanMessenger.on_skill_requirements_updated.connect(self.OnRemoteCorpSkillPlanRequirementsChanged)
        self.corpSkillPlanMessenger.on_name_updated.connect(self.OnRemoteCorpSkillPlanNameChanged)
        self.corpSkillPlanMessenger.on_description_updated.connect(self.OnRemoteCorpSkillPlanDescriptionChanged)
        self.corpSkillPlanMessenger.on_category_updated.connect(self.OnRemoteCorpSkillPlanCategoryChanged)

    def OnRemoteCorpSkillPlanCreated(self, skillPlanID, skillPlanData):
        if self.corpCache is None:
            return
        self._CreateAndCacheCorpSkillPlanController(self.corpCache, skillPlanID, skillPlanData)
        skillPlanSignals.on_created(skillPlanID)

    def OnRemoteCorpSkillPlanRequirementsChanged(self, skillPlanID, skillRequirements):
        skillPlan = self._GetCorp(skillPlanID)
        if skillPlan:
            skillPlan.ResetSkillRequirements(skillRequirements)

    def OnRemoteCorpSkillPlanNameChanged(self, skillPlanID, name):
        skillPlan = self._GetCorp(skillPlanID)
        if skillPlan:
            skillPlan.SetName(name)
            skillPlanSignals.on_saved(skillPlan)

    def OnRemoteCorpSkillPlanDescriptionChanged(self, skillPlanID, description):
        skillPlan = self._GetCorp(skillPlanID)
        if skillPlan:
            skillPlan.SetDescription(description)
            skillPlanSignals.on_saved(skillPlan)

    def OnRemoteCorpSkillPlanCategoryChanged(self, skillPlanID, categoryID):
        skillPlan = self._GetCorp(skillPlanID)
        if skillPlan:
            skillPlan.SetCategoryID(categoryID)
            skillPlanSignals.on_saved(skillPlan)

    def OnRemoteCorpSkillPlanDeleted(self, skillPlanID):
        if self.corpCache is None or skillPlanID not in self.corpCache:
            return
        self.corpCache.pop(skillPlanID)
        skillPlanSignals.on_deleted(skillPlanID)

    def _GetCorp(self, skillPlanID):
        if self.corpCache:
            return self.corpCache.get(skillPlanID, None)

    def OnSkillLevelsTrained(self, skillLevels):
        trackedPlan = self.GetTrackedSkillPlan()
        if trackedPlan and trackedPlan.IsCompleted():
            if set(trackedPlan.GetSkillRequirements()).intersection(skillLevels):
                skillPlanSignals.on_tracked_plan_completed(trackedPlan.GetID())

    def Get(self, skillPlanID):
        if skillPlanID is None:
            return
        if skillPlanID in self.GetAllCertified():
            return self.GetCertifiedSkillPlan(skillPlanID)
        if skillPlanID in self.GetAllPersonal():
            return self.GetAllPersonal()[skillPlanID]
        if skillPlanID in self.GetAllCorp():
            return self.GetAllCorp()[skillPlanID]

    def GetCertifiedSkillPlan(self, skillPlanID):
        return self.GetAllCertified().get(skillPlanID, None)

    def GetOwnedByOther(self, skillPlanID, ownerID = None):
        try:
            if IsPlayerCorporation(ownerID):
                skillPlanData = corpSkillPlanRequest.GetShared(skillPlanID)
                if skillPlanData:
                    return self._GetCorpSkillPlanController(skillPlanID, skillPlanData, ownerID)
            else:
                skillPlanData = personalSkillPlanRequest.GetShared(skillPlanID)
                if skillPlanData:
                    return self._GetPersonalSkillPlanController(skillPlanID, skillPlanData)
        except Exception as e:
            logger.exception(e)
            return None

    def GetNewUnsavedPersonal(self):
        return PersonalSkillPlanController(skillPlanID=skillPlanConst.PLAN_ID_NEW_UNSAVED, milestoneSvc=self.personalMilestoneSvc, ownerID=session.charid)

    def GetNewUnsavedCorp(self):
        return CorpSkillPlanController(skillPlanID=skillPlanConst.PLAN_ID_NEW_UNSAVED, milestoneSvc=self.corpMilestoneSvc, ownerID=session.corpid)

    def GetAllPersonal(self):
        self._PrimePersonalCache()
        return self.personalCache

    def GetAllCorp(self):
        self._PrimeCorpCache()
        return self.corpCache

    def _PrimeCorpCache(self):
        if self.corpCache is not None:
            return
        try:
            corpCache = {}
            if sm.GetService('publicGatewaySvc').is_available():
                skillPlans = corpSkillPlanRequest.GetAll()
                calls = [ (self._CreateAndCacheCorpSkillPlanController, (corpCache, skillPlanID, skillPlanData)) for skillPlanID, skillPlanData in skillPlans.items() ]
                uthread.parallel(calls)
            self.corpCache = corpCache
        except Exception as e:
            logger.exception(e)
            raise SkillPlanConnectionError()

    def GetTrackedSkillPlan(self):
        trackedPlanID = self._GetTrackedSkillPlanID()
        if trackedPlanID is None:
            return
        return self.Get(trackedPlanID)

    def IsSkillPlanTracked(self, skillPlanID):
        return self._GetTrackedSkillPlanID() == skillPlanID

    def OnSessionChanged(self, isRemote, session, change):
        if 'corpid' in change:
            self.corpCache = None
            self.corpMilestoneSvc = CorpSkillPlanMilestoneService()

    def OnSessionReset(self):
        self.FlushCache()

    def FlushCache(self):
        self.personalCache = None
        self.corpCache = None
        self.personalMilestoneSvc = PersonalSkillPlanMilestoneService()
        self.corpMilestoneSvc = CorpSkillPlanMilestoneService()
        self.trackedPlanID = None

    def _GetTrackedSkillPlanID(self):
        if not sm.GetService('publicGatewaySvc').is_available():
            return
        try:
            if self.trackedPlanID is None:
                self.trackedPlanID = personalSkillPlanRequest.GetActive()
            if self.trackedPlanID == uuid.UUID(int=0):
                return
            return self.trackedPlanID
        except Exception as e:
            ShowQuickMessage(GetByLabel('UI/SkillPlan/ConnectionError'))
            logger.exception(e)
            return

    def SetTrackedSkillPlanID(self, skillPlanID):
        if not sm.GetService('publicGatewaySvc').is_available():
            return
        if self._GetTrackedSkillPlanID() != skillPlanID:
            untracked = self._GetTrackedSkillPlanID()
            self.trackedPlanID = self._SetTrackedPlanID(skillPlanID)
            trackedPlan = self.Get(skillPlanID)
            untrackedPlan = self.Get(untracked)
            skillPlanSignals.on_tracked_plan_changed(untrackedPlan, trackedPlan)
            if skillPlanID:
                PlaySound('skill_planner_tracked_play')
            else:
                PlaySound('skill_planner_untracked_play')

    def _SetTrackedPlanID(self, skillPlanID):
        try:
            return personalSkillPlanRequest.SetActive(skillPlanID)
        except Exception as e:
            ShowQuickMessage(GetByLabel('UI/SkillPlan/ConnectionError'))
            logger.exception(e)
            return None

    def _PrimePersonalCache(self):
        if self.personalCache is not None:
            return
        try:
            personalCache = {}
            if sm.GetService('publicGatewaySvc').is_available():
                skillPlanIDs = personalSkillPlanRequest.GetAll()
                calls = [ (self._CreateAndCachePersonalSkillPlanController, (personalCache, skillPlanID)) for skillPlanID in skillPlanIDs ]
                uthread.parallel(calls)
            self.personalCache = personalCache
        except Exception as e:
            logger.exception(e)
            raise SkillPlanConnectionError()

    def _CreateAndCachePersonalSkillPlanController(self, cache, skillPlanID):
        try:
            skillPlanData = personalSkillPlanRequest.Get(skillPlanID)
            planController = self._GetPersonalSkillPlanController(skillPlanID, skillPlanData, ownerID=session.charid)
            if planController is not None:
                cache[skillPlanID] = planController
        except Exception as e:
            logger.exception(e)
            return

    def _GetPersonalSkillPlanController(self, skillPlanID, skillPlanData, ownerID = None):
        try:
            skillRequirements = [ (int(req.skill_type.sequential), req.level) for req in skillPlanData.skill_requirements ]
            skillPlan = PersonalSkillPlanController(skillPlanID=skillPlanID, name=skillPlanData.name, description=skillPlanData.description, skillRequirements=skillRequirements, milestoneSvc=self.personalMilestoneSvc, ownerID=ownerID)
            changed = skillPlanValidation.ValidateSkillPlan(skillPlan.GetSkillRequirements())
            if changed:
                personalSkillPlanRequest.SetRequiredSkills(skillPlanID, skillPlan.GetSkillRequirements())
            return skillPlan
        except Exception as e:
            logger.exception(e)
            return None

    def _CreateAndCacheCorpSkillPlanController(self, cache, skillPlanID, skillPlanData):
        skillPlan = self._GetCorpSkillPlanController(skillPlanID, skillPlanData)
        if skillPlan is not None:
            cache[skillPlan.GetID()] = skillPlan

    def _GetCorpSkillPlanController(self, skillPlanID, skillPlanData, ownerID = None):
        try:
            categoryID = uuid.UUID(bytes=skillPlanData.category.uuid).int
            return CorpSkillPlanController(skillPlanID=skillPlanID, name=skillPlanData.name, description=skillPlanData.description, categoryID=categoryID, ownerID=ownerID or session.corpid, milestoneSvc=self.corpMilestoneSvc)
        except Exception as e:
            logger.exception(e)
            return None

    def GetAllCertified(self):
        return self.certifiedCache

    def GetAllCertifiedForCareerPath(self, careerPathID):
        return self.certifiedByCareerPathID[careerPathID]

    def FilterCertifiedSkillPlans(self, skillPlanID = None, careerPathID = None, factionID = None, npcCorporationDivision = None):
        skillPlansToCheck = []
        if skillPlanID:
            skillPlanUUID = uuid.UUID(int=skillPlanID)
            if skillPlanUUID in self.certifiedCache:
                skillPlan = self.certifiedCache[skillPlanUUID]
                skillPlansToCheck.append(skillPlan)
        elif careerPathID:
            if careerPathID in self.certifiedByCareerPathID:
                skillPlansToCheck = self.GetAllCertifiedForCareerPath(careerPathID)
        else:
            skillPlansToCheck = self.GetAllCertified().values()
        filteredSkillPlans = []
        for skillPlan in skillPlansToCheck:
            if careerPathID and skillPlan.careerPathID != careerPathID:
                continue
            if factionID and skillPlan.factionID != factionID:
                continue
            if npcCorporationDivision and skillPlan.npcCorporationDivision != npcCorporationDivision:
                continue
            filteredSkillPlans.append(skillPlan)

        return filteredSkillPlans

    def IsAnyCertifiedSkillPlanQueuedOrTrained(self, skillPlanID, careerPathID, factionID, npcCorporationDivision):
        skillPlans = self.FilterCertifiedSkillPlans(skillPlanID, careerPathID, factionID, npcCorporationDivision)
        if not skillPlans:
            return False
        for skillPlan in skillPlans:
            if skillPlan.IsQueuedOrTrained():
                return True

        return False

    def _PrimeCertifiedCache(self):
        for skillPlanID, skillPlanData in skillPlanFSDLoader.get_skill_plans().iteritems():
            skillRequirements = [ (skill.typeID, skill.level) for skill in skillPlanData.skillRequirements ]
            skillPlanID = uuid.UUID(int=skillPlanID)
            skillPlan = CertifiedSkillPlanController(skillPlanID=skillPlanID, name=skillPlanData.nameID, description=skillPlanData.descriptionID, skillRequirements=skillRequirements, milestones=skillPlanData.milestones, factionID=skillPlanData.factionID, careerPathID=skillPlanData.careerPathID, npcCorporationDivision=skillPlanData.npcCorporationDivision)
            self.certifiedCache[skillPlanID] = skillPlan
            self.certifiedByCareerPathID[skillPlanData.careerPathID].append(skillPlan)

    def Delete(self, skillPlanID):
        if skillPlanID in self.GetAllPersonal():
            self._DeletePersonal(skillPlanID)
        elif skillPlanID in self.GetAllCorp():
            self._DeleteCorp(skillPlanID)
        else:
            logger.exception("Unable to delete skill plan with id: %s as it's not found", skillPlanID)

    def _DeletePersonal(self, skillPlanID):
        if uicore.Message('DeleteSkillPlan', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return
        try:
            personalSkillPlanRequest.Delete(skillPlanID)
            self.personalCache.pop(skillPlanID)
            skillPlanSignals.on_deleted(skillPlanID)
        except Exception:
            ShowQuickMessage(GetByLabel('UI/SkillPlan/ConnectionError'))
            raise

    def _DeleteCorp(self, skillPlanID):
        if uicore.Message('DeleteSkillPlan', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return
        try:
            corpSkillPlanRequest.Delete(skillPlanID)
            self.corpCache.pop(skillPlanID)
            skillPlanSignals.on_deleted(skillPlanID)
        except Exception:
            ShowQuickMessage(GetByLabel('UI/SkillPlan/ConnectionError'))
            raise

    def Save(self, skillPlan):
        if isinstance(skillPlan, CertifiedSkillPlanController):
            return
        if isinstance(skillPlan, PersonalSkillPlanController):
            if skillPlan.GetID() == skillPlanConst.PLAN_ID_NEW_UNSAVED:
                newSkillPlan = self._SaveNewPersonalSkillPlan(skillPlan)
                skillPlanSignals.on_created(newSkillPlan.GetID())
            else:
                self._SaveExistingPersonalSkillPlan(skillPlan)
        elif isinstance(skillPlan, CorpSkillPlanController):
            if skillPlan.GetID() == skillPlanConst.PLAN_ID_NEW_UNSAVED:
                self._SaveNewCorpSkillPlan(skillPlan)
            else:
                self._SaveExistingCorpSkillPlan(skillPlan)

    def _SaveExistingPersonalSkillPlan(self, skillPlan):
        try:
            skillPlanUpdateCalls = self._GetCallsToUpdate(skillPlan, personalSkillPlanRequest)
            if len(skillPlanUpdateCalls) > 0:
                uthread.parallel(skillPlanUpdateCalls)
        except Exception as e:
            logger.exception(e)
            self._RaiseErrorMessageOnSave(e, skillPlan)

        self.personalCache[skillPlan.GetID()] = skillPlan
        skillPlan.SaveMilestones()
        skillPlanSignals.on_saved(skillPlan)

    def _SaveExistingCorpSkillPlan(self, skillPlan):
        try:
            skillPlanUpdateCalls = self._GetCallsToUpdate(skillPlan, corpSkillPlanRequest)
            if len(skillPlanUpdateCalls) > 0:
                uthread.parallel(skillPlanUpdateCalls)
        except Exception as e:
            logger.exception(e)
            self._RaiseErrorMessageOnSave(e, skillPlan)

        self.corpCache[skillPlan.GetID()] = skillPlan
        skillPlan.SaveMilestones()
        skillPlanSignals.on_saved(skillPlan)

    def _GetCallsToUpdate(self, skillPlan, requestModule):
        skillPlanID = skillPlan.GetID()
        cachedSkillPlan = self.Get(skillPlanID)
        skillPlanUpdateCalls = []
        if skillPlan.GetName() != cachedSkillPlan.GetName():
            skillPlanUpdateCalls.append((requestModule.SetName, (skillPlanID, skillPlan.GetName())))
        if skillPlan.GetDescription() != cachedSkillPlan.GetDescription():
            skillPlanUpdateCalls.append((requestModule.SetDescription, (skillPlanID, skillPlan.GetDescription())))
        if skillPlan.GetSkillRequirements() != cachedSkillPlan.GetSkillRequirements():
            skillPlanUpdateCalls.append((requestModule.SetRequiredSkills, (skillPlanID, skillPlan.GetSkillRequirements())))
        if skillPlan.GetCategoryID() != cachedSkillPlan.GetCategoryID():
            skillPlanUpdateCalls.append((requestModule.SetCategory, (skillPlanID, skillPlan.GetCategoryID())))
        return skillPlanUpdateCalls

    def _SaveNewPersonalSkillPlan(self, skillPlan):
        self.CheckNumPersonalSkillPlans()
        try:
            newSkillPlanID = personalSkillPlanRequest.Create(skillPlan.GetName(), skillPlan.GetDescription(), skillPlan.GetSkillRequirements())
        except Exception as e:
            logger.exception(e)
            self._RaiseErrorMessageOnSave(e, skillPlan)

        newSkillPlan = self._CreateAndCachePersonalController(newSkillPlanID, skillPlan)
        return newSkillPlan

    def _CreateAndCachePersonalController(self, newSkillPlanID, skillPlan):
        self._PrimePersonalCache()
        skillRequirements = skillPlan.GetSkillRequirements()[:]
        skillPlanValidation.ValidateSkillPlan(skillRequirements)
        newSkillPlan = PersonalSkillPlanController(skillPlanID=newSkillPlanID, name=skillPlan.GetName(), description=skillPlan.GetDescription(), skillRequirements=skillRequirements, milestoneSvc=self.personalMilestoneSvc, ownerID=session.charid)
        newSkillPlan.SetMilestonesToAdd(skillPlan.GetMilestonesSet())
        newSkillPlan.SaveMilestones()
        self.personalCache[newSkillPlanID] = newSkillPlan
        return newSkillPlan

    def _SaveNewCorpSkillPlan(self, skillPlan):
        self.CheckNumCorpSkillPlans()
        try:
            newSkillPlanID = corpSkillPlanRequest.Create(skillPlan.GetName(), skillPlan.GetDescription(), skillPlan.GetSkillRequirements(), skillPlan.GetCategoryID())
        except Exception as e:
            logger.exception(e)
            self._RaiseErrorMessageOnSave(e, skillPlan)

        newSkillPlan = self._CreateAndCacheCorpController(newSkillPlanID, skillPlan)
        skillPlanSignals.on_created(newSkillPlanID)
        return newSkillPlan

    def _CreateAndCacheCorpController(self, newSkillPlanID, skillPlan):
        self._PrimeCorpCache()
        skillRequirements = skillPlan.GetSkillRequirements()[:]
        skillPlanValidation.ValidateSkillPlan(skillRequirements)
        newSkillPlan = CorpSkillPlanController(skillPlanID=newSkillPlanID, name=skillPlan.GetName(), description=skillPlan.GetDescription(), skillRequirements=skillRequirements, milestoneSvc=self.corpMilestoneSvc, categoryID=skillPlan.GetCategoryID(), ownerID=session.corpid)
        newSkillPlan.SetMilestonesToAdd(skillPlan.GetMilestonesSet())
        newSkillPlan.SaveMilestones()
        self.corpCache[newSkillPlanID] = newSkillPlan
        return newSkillPlan

    def _RaiseErrorMessageOnSave(self, e, skillPlan):
        if isinstance(e, UserError):
            if e.msg == 'SkillPlansErrorInvalidData' and len(skillPlan.GetName()) > skillPlanConst.MAX_LEN_NAME:
                raise UserError('UnableToSaveSkillPlanNameTooLong')
            elif e.msg == 'SkillPlansErrorInvalidData' and len(skillPlan.GetDescription()) > skillPlanConst.MAX_LEN_DESC:
                raise UserError('UnableToSaveSkillPlanDescTooLong')
            else:
                raise UserError('UnableToSaveSkillPlan')
        if isinstance(e, TimeoutException):
            raise UserError('SkillPlanSaveTimeout')
        else:
            raise UserError('UnableToSaveSkillPlan')

    def CheckNumPersonalSkillPlans(self):
        plans = self.GetAllPersonal()
        if plans is None:
            raise UserError('UnableToFetchSkillPlans')
        numPlans = len(plans)
        if numPlans >= skillPlanConst.MAX_PERSONAL_PLANS:
            raise UserError('MaxPersonalPlansReached', {'numPlans': numPlans})

    def CheckNumCorpSkillPlans(self):
        plans = self.GetAllCorp()
        if plans is None:
            raise UserError('UnableToFetchSkillPlans')
        numPlans = len(plans)
        if numPlans >= skillPlanConst.MAX_CORP_PLANS:
            raise UserError('MaxCorpPlansReached', {'numPlans': numPlans})

    def SaveCopyOfPlanAsPersonalSkillPlan(self, skillPlan):
        newSkillPlan = self._SaveNewPersonalSkillPlan(skillPlan)
        return newSkillPlan

    def IsSkillPlanMineOrCertified(self, skillPlanID):
        return bool(self.Get(skillPlanID))

    def HasFinishedAIRSkillPlan(self):
        skillSvc = sm.StartService('skills')
        skillsInQueue = sm.GetService('skillqueue').GetQueueAsRequirements()
        airSkillPlan = self.Get(skillPlanConst.PLAN_ID_AIR)
        for typeID, level in airSkillPlan.skillRequirements:
            if skillSvc.MySkillLevel(typeID) < level and (typeID, level) not in skillsInQueue:
                return False

        return True
