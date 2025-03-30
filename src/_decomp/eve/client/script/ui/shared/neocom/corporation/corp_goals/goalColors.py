#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corp_goals\goalColors.py
from goals.common.goalConst import GoalState
from eve.client.script.ui import eveColor, eveThemeColor

def get_color(state):
    if state == GoalState.ACTIVE:
        return eveThemeColor.THEME_FOCUS
    if state == GoalState.COMPLETED:
        return eveColor.SUCCESS_GREEN
    if state == GoalState.CLOSED:
        return eveColor.GUNMETAL_GREY
    if state == GoalState.EXPIRED:
        return eveColor.DANGER_RED
