#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\skills\skillplan\grpc\message_bus\corpMilestoneRequestsMessenger.py
from eveProto.generated.eve_public.corporation.skill.plan.milestone_pb2 import GetAllRequest, CreateRequest, DeleteRequest
from eveProto.generated.eve_public.corporation.skill.plan.milestone_pb2 import GetAllResponse, CreateResponse, DeleteResponse
from skills.skillplan.grpc.message_bus.requestsMessenger import send_request

class CorpSkillPlanMilestoneRequestsMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def get_all(self, skill_plan_id):
        request = GetAllRequest()
        request.skill_plan.uuid = skill_plan_id.bytes
        return send_request(self.public_gateway, request, GetAllResponse)

    def create_with_type_id(self, skill_plan_id, type_id):
        request = CreateRequest()
        request.milestone.skill_plan.uuid = skill_plan_id.bytes
        request.milestone.train_to_type.sequential = type_id
        return send_request(self.public_gateway, request, CreateResponse)

    def create_with_skill_requirement(self, skill_plan_id, type_id, level):
        request = CreateRequest()
        request.milestone.skill_plan.uuid = skill_plan_id.bytes
        request.milestone.skill.skill_type.sequential = type_id
        request.milestone.skill.level = level
        return send_request(self.public_gateway, request, CreateResponse)

    def delete(self, milestone_id):
        request = DeleteRequest()
        request.milestone.uuid = milestone_id.bytes
        return send_request(self.public_gateway, request, DeleteResponse)
