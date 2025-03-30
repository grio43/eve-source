#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\skills\skillplan\grpc\personalMilestoneRequest.py
import uuid
from skills.skillplan.grpc.message_bus.milestoneRequestsMessenger import SkillPlanMilestoneRequestsMessenger
from skills.skillplan.milestone.const import MilestoneType

def GetAll(skillPlanID):
    response = GetMilestoneRequestsMessenger().get_all(skillPlanID)
    milestones = []
    for milestone in response.milestones:
        if milestone.data.train_to_type.sequential:
            milestones.append((uuid.UUID(bytes=milestone.identifier.uuid), MilestoneType.TYPE_ID_MILESTONE, int(milestone.data.train_to_type.sequential)))
        elif milestone.data.skill.skill_type:
            milestones.append((uuid.UUID(bytes=milestone.identifier.uuid), MilestoneType.SKILL_REQUIREMENT_MILESTONE, (int(milestone.data.skill.skill_type.sequential), milestone.data.skill.level)))

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
    return SkillPlanMilestoneRequestsMessenger(sm.GetService('publicGatewaySvc'))
