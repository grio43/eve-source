#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\skills\skillplan\loggers\skillPlanLogger.py
from eveProto.generated.eve_public.app.eveonline.skill.plan.certified.analytics_pb2 import Clicked
from eveProto.generated.eve_public.app.eveonline.skill.plan.certified.analytics_pb2 import TrainingStarted
from eveProto.generated.eve_public.app.eveonline.skill.plan.certified.analytics_pb2 import Tracked
from eveProto.generated.eve_public.app.eveonline.skill.plan.certified.analytics_pb2 import AllSkillbooksBought
from eveProto.generated.eve_public.app.eveonline.skill.plan.certified.analytics_pb2 import OmegaButtonClicked
from eveexceptions import EatsExceptions

@EatsExceptions('protoClientLogs')
def log_certified_skill_plan_clicked(skill_plan_id):
    event = Clicked()
    event.id.id = skill_plan_id.int
    _publish_event(event)


@EatsExceptions('protoClientLogs')
def log_certified_skill_plan_train_all_clicked(skill_plan_id):
    event = TrainingStarted()
    event.id.id = skill_plan_id.int
    _publish_event(event)


@EatsExceptions('protoClientLogs')
def log_certified_skill_plan_track_plan_clicked(skill_plan_id):
    event = Tracked()
    event.id.id = skill_plan_id.int
    _publish_event(event)


@EatsExceptions('protoClientLogs')
def log_certified_skill_plan_buy_missing_skillbooks_clicked(skill_plan_id):
    event = AllSkillbooksBought()
    event.id.id = skill_plan_id.int
    _publish_event(event)


@EatsExceptions('protoClientLogs')
def log_certified_skill_plan_omega_button_clicked(skill_plan_id):
    event = OmegaButtonClicked()
    event.id.id = skill_plan_id.int
    _publish_event(event)


def _publish_event(event):
    sm.GetService('publicGatewaySvc').publish_event_payload(event)
