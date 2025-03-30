#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\factionGoal.py
import uuid

class FactionGoal(object):

    def __init__(self, proto):
        self.goalID = uuid.UUID(bytes=proto.goal.uuid)
        self.factionID = proto.attributes.faction.sequential
        self.progress = proto.attributes.progress
        self.target = proto.attributes.target
        self.uiAnnotations = {}
        for annotation in proto.attributes.ui_annotations:
            self.uiAnnotations[annotation.key] = annotation.value

    def __repr__(self):
        return 'Faction Goal - ID: %s, factionID: %d, progress: %d, target: %d, annotations: %s' % (str(self.goalID),
         self.factionID,
         self.progress,
         self.target,
         self.uiAnnotations)
