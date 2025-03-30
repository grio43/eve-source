#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\skills\skillplan\grpc\message_bus\corpSkillPlanRequestsMessenger.py
import uuid
from eveProto.generated.eve_public.corporation.skill.plan.plan_pb2 import GetRequest, GetAllRequest, GetSharedRequest
from eveProto.generated.eve_public.corporation.skill.plan.plan_pb2 import CreateRequest, DeleteRequest
from eveProto.generated.eve_public.corporation.skill.plan.plan_pb2 import SetNameRequest, SetSkillRequirementsRequest
from eveProto.generated.eve_public.corporation.skill.plan.plan_pb2 import SetDescriptionRequest, SetCategoryRequest
from eveProto.generated.eve_public.corporation.skill.plan.plan_pb2 import GetResponse, GetAllResponse, GetSharedResponse
from eveProto.generated.eve_public.corporation.skill.plan.plan_pb2 import CreateResponse, DeleteResponse
from eveProto.generated.eve_public.corporation.skill.plan.plan_pb2 import SetNameResponse, SetSkillRequirementsResponse
from eveProto.generated.eve_public.corporation.skill.plan.plan_pb2 import SetDescriptionResponse, SetCategoryResponse
from skills.skillplan.grpc.message_bus.requestsMessenger import send_request

class CorpSkillPlanRequestsMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway

    def get(self, skill_plan_id):
        request = GetRequest()
        request.skill_plan.uuid = skill_plan_id.bytes
        return send_request(self.public_gateway, request, GetResponse)

    def get_shared(self, skill_plan_id):
        request = GetSharedRequest()
        request.skill_plan.uuid = skill_plan_id.bytes
        return send_request(self.public_gateway, request, GetSharedResponse)

    def get_all(self):
        request = GetAllRequest()
        return send_request(self.public_gateway, request, GetAllResponse)

    def create(self, name, description, required_skills, category_id):
        request = CreateRequest()
        request.skill_plan.name = name
        request.skill_plan.description = description
        for type_id, level in required_skills:
            required_skill = request.skill_plan.skill_requirements.add()
            required_skill.skill_type.sequential = type_id
            required_skill.level = level

        request.skill_plan.category.uuid = uuid.UUID(int=category_id).bytes
        return send_request(self.public_gateway, request, CreateResponse)

    def delete(self, skill_plan_id):
        request = DeleteRequest()
        request.skill_plan.uuid = skill_plan_id.bytes
        return send_request(self.public_gateway, request, DeleteResponse)

    def set_name(self, skill_plan_id, name):
        request = SetNameRequest()
        request.skill_plan.uuid = skill_plan_id.bytes
        request.name = name
        return send_request(self.public_gateway, request, SetNameResponse)

    def set_description(self, skill_plan_id, description):
        request = SetDescriptionRequest()
        request.skill_plan.uuid = skill_plan_id.bytes
        request.description = description
        return send_request(self.public_gateway, request, SetDescriptionResponse)

    def set_required_skills(self, skill_plan_id, required_skills):
        request = SetSkillRequirementsRequest()
        request.skill_plan.uuid = skill_plan_id.bytes
        for type_id, level in required_skills:
            required_skill = request.requirements.add()
            required_skill.skill_type.sequential = type_id
            required_skill.level = level

        return send_request(self.public_gateway, request, SetSkillRequirementsResponse)

    def set_category(self, skill_plan_id, category_id):
        request = SetCategoryRequest()
        request.skill_plan.uuid = skill_plan_id.bytes
        request.category.uuid = uuid.UUID(int=category_id).bytes
        return send_request(self.public_gateway, request, SetCategoryResponse)
