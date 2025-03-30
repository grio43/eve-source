#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\storylines\client\objectives\trackers\airnpetracker.py
from carbon.common.script.sys.serviceManager import ServiceManager
from storylines.client.objectives.base.tracker import ObjectiveTracker
from storylines.client.airnpe import skip_air_npe
from storylines.client.nes_intro import skip_nes_intro
AIR_NPE_GOAL_ID = 1
NES_INTRO_GOAL_ID = 3

class AirNpeObjectiveTracker(ObjectiveTracker):
    UPDATE_EVENT = 'OnAirNpeObjectiveUpdated'

    def _notify_of_update(self):
        sm = ServiceManager.Instance()
        sm.ScatterEvent('OnAirNpeObjectiveUpdated', current_goal=self.current_goal)

    def skip_mission(self):
        goal_id = self.current_goal.goal_id
        if goal_id == AIR_NPE_GOAL_ID:
            skip_air_npe('SkipTutorialOffer')
        elif goal_id == NES_INTRO_GOAL_ID:
            skip_nes_intro()
