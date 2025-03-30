#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\infoPanelObjectiveTracker.py
from eve.client.script.ui.shared.infoPanels.infoPanelMissions import InfoPanelMissions
from storylines.client.objectives.base.tracker import ObjectiveTracker
from uihider import UiHiderMixin

class InfoPanelObjectiveTracker(UiHiderMixin, InfoPanelMissions):
    OBJECTIVE_TRACKER_CLASS = ObjectiveTracker

    def ApplyAttributes(self, attributes):
        self.objective_tracker = self.OBJECTIVE_TRACKER_CLASS()
        super(InfoPanelObjectiveTracker, self).ApplyAttributes(attributes)

    @staticmethod
    def IsAvailable():
        return bool(ObjectiveTracker().get_objectives())

    def GetMissions(self):
        return self.objective_tracker.get_goals()

    def HasOptionsMenu(self):
        return False

    def GetOptionsMenu(self, menuParent, mission):
        pass
