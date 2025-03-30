#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\storylines\client\objectives\base\goal.py
from eve.client.script.ui.shared.infoPanels.infoPanelMissions import InfoPanelMissionData
from localization import GetByMessageID

class StorylineGoal(InfoPanelMissionData):

    def __init__(self, goal_id, title, title_icon):
        self.goal_id = goal_id
        super(StorylineGoal, self).__init__(title=GetByMessageID(title), icon=title_icon)

    def Update(self, objectives):
        self._SetObjectives(objectives)

    def _SetObjectives(self, objectives):
        self.objectives = objectives

    def GetID(self):
        return self.goal_id
