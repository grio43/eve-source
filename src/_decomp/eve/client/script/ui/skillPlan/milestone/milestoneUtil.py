#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\milestone\milestoneUtil.py
from carbonui.util.color import Color
from eve.client.script.ui import eveColor
COLOR_DISABLED = Color.GRAY3

def GetMissingSkillsColor(highlightNotInTraining):
    if highlightNotInTraining:
        return eveColor.WARNING_ORANGE
    return COLOR_DISABLED
