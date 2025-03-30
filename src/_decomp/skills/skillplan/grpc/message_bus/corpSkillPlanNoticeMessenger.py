#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\skills\skillplan\grpc\message_bus\corpSkillPlanNoticeMessenger.py
import uuid
from eveProto.generated.eve_public.corporation.skill.plan.plan_pb2 import CreatedNotice, DeletedNotice, CategoryUpdatedNotice, NameUpdatedNotice, DescriptionUpdatedNotice, SkillRequirementsUpdatedNotice
from signals import Signal

class CorpSkillPlanNoticeMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway
        self.public_gateway.subscribe_to_notice(CreatedNotice, self._on_created)
        self.public_gateway.subscribe_to_notice(DeletedNotice, self._on_deleted)
        self.public_gateway.subscribe_to_notice(SkillRequirementsUpdatedNotice, self._on_skill_requirements_updated)
        self.public_gateway.subscribe_to_notice(NameUpdatedNotice, self._on_name_updated)
        self.public_gateway.subscribe_to_notice(DescriptionUpdatedNotice, self._on_description_updated)
        self.public_gateway.subscribe_to_notice(CategoryUpdatedNotice, self._on_category_updated)
        self.on_created = Signal()
        self.on_deleted = Signal()
        self.on_skill_requirements_updated = Signal()
        self.on_name_updated = Signal()
        self.on_description_updated = Signal()
        self.on_category_updated = Signal()

    def _on_deleted(self, payload, primative):
        skill_plan_id = uuid.UUID(bytes=payload.skill_plan.uuid)
        self.on_deleted(skill_plan_id)

    def _on_created(self, payload, primative):
        skill_plan_id = uuid.UUID(bytes=payload.identifier.uuid)
        skill_plan = payload.skill_plan
        self.on_created(skill_plan_id, skill_plan)

    def _on_skill_requirements_updated(self, payload, primative):
        skill_plan_id = uuid.UUID(bytes=payload.identifier.uuid)
        skill_requirements = [ (int(req.skill_type.sequential), req.level) for req in payload.requirements ]
        self.on_skill_requirements_updated(skill_plan_id, skill_requirements)

    def _on_name_updated(self, payload, primative):
        skill_plan_id = uuid.UUID(bytes=payload.identifier.uuid)
        self.on_name_updated(skill_plan_id, payload.name)

    def _on_description_updated(self, payload, primative):
        skill_plan_id = uuid.UUID(bytes=payload.identifier.uuid)
        self.on_description_updated(skill_plan_id, payload.description)

    def _on_category_updated(self, payload, primative):
        skill_plan_id = uuid.UUID(bytes=payload.identifier.uuid)
        category_id = uuid.UUID(bytes=payload.category.uuid).int
        self.on_category_updated(skill_plan_id, category_id)
