#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\skills\skillplan\grpc\corpMilestoneRequest.py
import uuid
from skills.skillplan.grpc.message_bus.corpMilestoneRequestsMessenger import CorpSkillPlanMilestoneRequestsMessenger
from skills.skillplan.grpc.milestoneProtoUtil import GetMilestoneData
from skills.skillplan.milestone.const import MilestoneType

def GetAll(skillPlanID):
    response = GetMilestoneRequestsMessenger().get_all(skillPlanID)
    milestones = []
    for milestoneProto in response.milestones:
        milestoneData = GetMilestoneData(milestoneProto.identifier, milestoneProto.data)
        if milestoneData:
            milestones.append(milestoneData)

    return milestones


def CreateMilestone(skillPlanID, milestone):
    milestoneType = milestone.GetMilestoneType()
    if milestoneType == MilestoneType.SKILL_REQUIREMENT_MILESTONE:
        return CreateWithSkillRequirement(skillPlanID, milestone.GetTypeID(), milestone.GetLevel())
    if milestoneType == MilestoneType.TYPE_ID_MILESTONE:
        return CreateWithTypeID(skillPlanID, milestone.GetTypeID())


def CreateWithTypeID(skillPlanID, typeID):
    response = GetMilestoneRequestsMessenger().create_with_type_id(skillPlanID, typeID)
    return uuid.UUID(bytes=response.milestone.uuid)


def CreateWithSkillRequirement(skillPlanID, skillID, skillLevel):
    response = GetMilestoneRequestsMessenger().create_with_skill_requirement(skillPlanID, skillID, skillLevel)
    return uuid.UUID(bytes=response.milestone.uuid)


def Delete(milestoneID):
    GetMilestoneRequestsMessenger().delete(milestoneID)


def GetMilestoneRequestsMessenger():
    return CorpSkillPlanMilestoneRequestsMessenger(sm.GetService('publicGatewaySvc'))
