#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\link.py
import uuid
import evelink.client
SCHEME_SKILL_PLAN = 'skillPlan'
link_color_info = evelink.LinkColorInfo(normal='#94ccff', hover='#aed9ff')

def register_link_handlers(registry):
    registry.register(SCHEME_SKILL_PLAN, handle_link, hint='UI/SkillPlan/SkillPlan')


def handle_link(url):
    skillPlanID, ownerID = parse_skillPlanID_url(url)
    from eve.client.script.ui.skillPlan.skillPlanPanelWnd import OpenSkillPlanWnd
    OpenSkillPlanWnd(skillPlanID, ownerID)


def parse_skillPlanID_url(url):
    _, skillPlanID, ownerID = url.split(':')
    try:
        skillPlanID = int(skillPlanID)
    except ValueError:
        skillPlanID = uuid.UUID(skillPlanID)

    try:
        ownerID = int(ownerID)
    except ValueError:
        ownerID = None

    return (skillPlanID, ownerID)


def format_skill_plan_url(skillPlanID, ownerID):
    return u'{}:{}:{}'.format(SCHEME_SKILL_PLAN, skillPlanID, ownerID)


def skillplan_link(planID, name, ownerID = None):
    return evelink.Link(url=format_skill_plan_url(planID, ownerID), text=name)
