#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\skills\skillplan\grpc\milestoneProtoUtil.py
import uuid
from skills.skillplan.milestone.const import MilestoneType

def GetMilestoneData(milestone_id, attributes):
    if attributes.train_to_type.sequential:
        return (uuid.UUID(bytes=milestone_id.uuid), MilestoneType.TYPE_ID_MILESTONE, int(attributes.train_to_type.sequential))
    if attributes.skill.skill_type:
        return (uuid.UUID(bytes=milestone_id.uuid), MilestoneType.SKILL_REQUIREMENT_MILESTONE, (int(attributes.skill.skill_type.sequential), attributes.skill.level))
