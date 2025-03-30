#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\conditions\mission.py
from .base import Condition

class ExpandedMission(Condition):
    atom_id = 578

    def __init__(self, feature_id = None, mission_id = None, **kwargs):
        super(ExpandedMission, self).__init__(**kwargs)
        self.feature_id = feature_id
        self.mission_id = self.get_atom_parameter_value('mission_id', mission_id)

    def validate(self, **kwargs):
        expanded_mission = sm.GetService('infoPanel').GetExpandedMission()
        if expanded_mission.get('featureID') != self.feature_id:
            return False
        if expanded_mission.get('missionID') != self.mission_id:
            return False
        return True

    @classmethod
    def get_subtitle(cls, feature_id = None, mission_id = None, **kwargs):
        return u'{} {}'.format(feature_id, cls.get_atom_parameter_value('mission_id', mission_id))
