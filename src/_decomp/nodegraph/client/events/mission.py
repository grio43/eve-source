#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\events\mission.py
from .base import Event

class OnExpandedMissionChanged(Event):
    atom_id = 577
    __notifyevents__ = ['OnExpandedMissionChanged']

    def OnExpandedMissionChanged(self, featureID = None, missionID = None):
        self.invoke(feature_id=featureID, mission_id=missionID)
