#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\skills\skillplan\grpc\corpSkillPlanRequest.py
import uuid
import eveProto.generated.eve_public.skill.plan.plan_pb2 as skill_plan_pb2
from skills.skillplan.grpc.message_bus.corpSkillPlanRequestsMessenger import CorpSkillPlanRequestsMessenger

def GetAll():
    response = _GetMessenger().get_all()
    return {uuid.UUID(bytes=plan.identifier.uuid):plan.skill_plan for plan in response.skill_plans}


def Get(skillPlanID):
    response = _GetMessenger().get(skillPlanID)
    return response.skill_plan


def GetShared(skillPlanID):
    response = _GetMessenger().get_shared(skillPlanID)
    if response.HasField('skill_plan'):
        return response.skill_plan
    else:
        return None


def Create(name, description, requiredSkills, categoryID):
    response = _GetMessenger().create(name, description, requiredSkills, categoryID)
    return uuid.UUID(bytes=response.skill_plan.uuid)


def Delete(skillPlanID):
    _GetMessenger().delete(skillPlanID)


def SetName(skillPlanID, name):
    _GetMessenger().set_name(skillPlanID, name)


def SetDescription(skillPlanID, description):
    _GetMessenger().set_description(skillPlanID, description)


def SetRequiredSkills(skillPlanID, requiredSkills):
    _GetMessenger().set_required_skills(skillPlanID, requiredSkills)


def SetCategory(skillPlanID, categoryID):
    _GetMessenger().set_category(skillPlanID, categoryID)


def _GetMessenger():
    return CorpSkillPlanRequestsMessenger(sm.GetService('publicGatewaySvc'))
