#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\corporation\client\goals\goalDetailsWnd.py
from carbonui.control.window import Window
from corporation.client.goals.goalDetailsCont import GoalDetailsCont

class GoalDetailsWnd(Window):
    default_windowID = 'GoalDetails'
    default_captionLabelPath = 'UI/Corporations/Goals/ProjectDetails'
    default_minSize = (500, 400)
    default_height = 600
    default_width = 600

    def ApplyAttributes(self, attributes):
        super(GoalDetailsWnd, self).ApplyAttributes(attributes)
        job_id = attributes.job_id
        GoalDetailsCont(parent=self.content, job_id=job_id)
