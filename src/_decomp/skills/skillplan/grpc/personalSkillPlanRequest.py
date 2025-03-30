#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\skills\skillplan\grpc\personalSkillPlanRequest.py
import uuid
import eveProto.generated.eve_public.skill.plan.plan_pb2 as skill_plan_pb2
from message_bus.skillPlanRequestsMessenger import SkillPlanRequestsMessenger

def GetAll():
    response = _GetSkillPlanRequestsMessenger().get_all()
    return [ uuid.UUID(bytes=plan.uuid) for plan in response.skill_plans ]


def Get(skillPlanID):
    response = _GetSkillPlanRequestsMessenger().get(skillPlanID)
    return response.skill_plan


def GetShared(skillPlanID):
    response = _GetSkillPlanRequestsMessenger().get_shared(skillPlanID)
    if response.HasField('skill_plan'):
        return response.skill_plan
    else:
        return None


def GetActive():
    response = _GetSkillPlanRequestsMessenger().get_active()
    skill_plan_id = uuid.UUID(bytes=response.skill_plan.uuid)
    return skill_plan_id


def SetActive(skillPlanID):
    return _GetSkillPlanRequestsMessenger().set_active(skillPlanID)


def Create(name, description, requiredSkills):
    response = _GetSkillPlanRequestsMessenger().create(name, description, requiredSkills)
    return uuid.UUID(bytes=response.skill_plan.uuid)


def Delete(skillPlanID):
    _GetSkillPlanRequestsMessenger().delete(skillPlanID)


def SetName(skillPlanID, name):
    _GetSkillPlanRequestsMessenger().set_name(skillPlanID, name)


def SetDescription(skillPlanID, description):
    _GetSkillPlanRequestsMessenger().set_description(skillPlanID, description)


def SetRequiredSkills(skillPlanID, requiredSkills):
    _GetSkillPlanRequestsMessenger().set_required_skills(skillPlanID, requiredSkills)


def _GetSkillPlanRequestsMessenger():
    return SkillPlanRequestsMessenger(sm.GetService('publicGatewaySvc'))
