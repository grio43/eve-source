#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\skills\skillplan\milestone\milestoneService.py
import logging
from collections import defaultdict
import uthread
from milestoneController import BuildMilestonesFromRawData
from skills.skillplan import skillPlanSignals
import skills.skillplan.grpc.personalMilestoneRequest as personalMilestoneRequest
import skills.skillplan.grpc.corpMilestoneRequest as corpMilestoneRequest
from skills.skillplan.grpc.message_bus.corpMilestoneNoticeMessenger import CorpMilestoneNoticeMessenger
from skills.skillplan.milestone.milestoneController import GetMilestoneController
logger = logging.getLogger(__name__)

class BaseSkillPlanMilestoneService(object):
    milestoneRequest = None

    def __init__(self):
        self.cache = defaultdict(dict)
        skillPlanSignals.on_deleted.connect(self.OnSkillPlanDeleted)

    def Get(self, skillPlanID, milestoneID):
        if milestoneID in self.GetMilestonesForSkillPlan(skillPlanID):
            return self.GetMilestonesForSkillPlan(skillPlanID)[milestoneID]

    def GetMilestonesForSkillPlan(self, skillPlanID):
        if skillPlanID not in self.cache:
            self._PrimeCacheForSkillPlan(skillPlanID)
        return self.cache[skillPlanID].copy()

    def ClearMilestonesForSkillPlan(self, skillPlanID):
        if skillPlanID in self.cache:
            del self.cache[skillPlanID]

    def _PrimeCacheForSkillPlan(self, skillPlanID):
        try:
            milestones = self.milestoneRequest.GetAll(skillPlanID)
            self.cache[skillPlanID] = {}
            for m in BuildMilestonesFromRawData(milestones):
                if not m.IsValid():
                    self.milestoneRequest.Delete(m.milestoneID)
                else:
                    self.cache[skillPlanID][m.milestoneID] = m

        except Exception as e:
            logger.exception(e)

    def _AddToCache(self, skillPlanID, milestoneController):
        self.cache[skillPlanID][milestoneController.GetID()] = milestoneController

    def _Create(self, skillPlanID, milestoneController):
        try:
            milestoneID = self.milestoneRequest.CreateMilestone(skillPlanID, milestoneController)
            milestoneController.SetMilestoneID(milestoneID)
            self._AddToCache(skillPlanID, milestoneController)
        except Exception as e:
            logger.exception(e)

    def _Delete(self, skillPlanID, milestoneID):
        try:
            self.milestoneRequest.Delete(milestoneID)
            if skillPlanID in self.cache and milestoneID in self.cache[skillPlanID]:
                self._RemoveFromCache(skillPlanID, milestoneID)
        except Exception as e:
            logger.exception(e)

    def _RemoveFromCache(self, skillPlanID, milestoneID):
        self.cache[skillPlanID].pop(milestoneID, None)

    def _GetSkillPlanID(self, milestoneID):
        for skillPlanID, milestoneIDs in self.cache.iteritems():
            if milestoneID in milestoneIDs:
                return skillPlanID

    def SaveMilestones(self, skillPlanID, milestoneControllers):
        addCalls = []
        for milestoneController in milestoneControllers:
            addCalls.append((self._Create, (skillPlanID, milestoneController)))

        uthread.parallel(addCalls)

    def DeleteMilestones(self, skillPlanID, milestoneIDs):
        deleteCalls = [ (self._Delete, (skillPlanID, milestoneID)) for milestoneID in milestoneIDs ]
        uthread.parallel(deleteCalls)

    def OnSkillPlanDeleted(self, skillPlanID):
        if skillPlanID in self.cache:
            self.ClearMilestonesForSkillPlan(skillPlanID)


class PersonalSkillPlanMilestoneService(BaseSkillPlanMilestoneService):
    milestoneRequest = personalMilestoneRequest


class CorpSkillPlanMilestoneService(BaseSkillPlanMilestoneService):
    milestoneRequest = corpMilestoneRequest

    def __init__(self):
        super(CorpSkillPlanMilestoneService, self).__init__()
        self.corpMilestoneMessenger = CorpMilestoneNoticeMessenger(sm.GetService('publicGatewaySvc'))
        self.corpMilestoneMessenger.on_created.connect(self.OnRemoteCorpMilestoneCreated)
        self.corpMilestoneMessenger.on_deleted.connect(self.OnRemoteCorpMilestoneDeleted)

    def OnRemoteCorpMilestoneCreated(self, skillPlanID, milestoneID, milestoneType, milestoneInfo):
        controller = GetMilestoneController(milestoneID, milestoneType, milestoneInfo)
        self._AddToCache(skillPlanID, controller)

    def OnRemoteCorpMilestoneDeleted(self, milestoneID):
        skillPlanID = self._GetSkillPlanID(milestoneID)
        if skillPlanID:
            self._RemoveFromCache(skillPlanID, milestoneID)
