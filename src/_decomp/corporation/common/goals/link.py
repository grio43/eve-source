#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\corporation\common\goals\link.py
import evelink

def get_goal_link(goal_id, goal_name):
    return evelink.local_service_link(method='OpenGoal', text=goal_name, goal_id_int=goal_id)
