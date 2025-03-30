#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\skills\skillplan\grpc\message_bus\corpMilestoneNoticeMessenger.py
import uuid
from eveProto.generated.eve_public.corporation.skill.plan.milestone_pb2 import CreatedNotice, DeletedNotice
from signals import Signal
from skills.skillplan.grpc.milestoneProtoUtil import GetMilestoneData

class CorpMilestoneNoticeMessenger(object):
    public_gateway = None

    def __init__(self, public_gateway):
        self.public_gateway = public_gateway
        self.public_gateway.subscribe_to_notice(CreatedNotice, self._on_created)
        self.public_gateway.subscribe_to_notice(DeletedNotice, self._on_deleted)
        self.on_created = Signal()
        self.on_deleted = Signal()

    def _on_created(self, payload, primative):
        skill_plan_id = uuid.UUID(bytes=payload.skill_plan.uuid)
        milestone_id, milestone_type, milestone_info = GetMilestoneData(payload.identifier, payload.milestone)
        self.on_created(skill_plan_id, milestone_id, milestone_type, milestone_info)

    def _on_deleted(self, payload, primative):
        milestone_id = uuid.UUID(bytes=payload.milestone.uuid)
        self.on_deleted(milestone_id)
