#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\skills\skillplan\controllers\certifiedSkillPlanController.py
import uuid
import localization
from localization import GetByLabel
from skills.skillplan.controllers.baseSkillPlanController import BaseSkillPlanController
from skills.skillplan.milestone.milestoneController import SkillRequirementMilestoneController, TypeIDMilestoneController

class CertifiedSkillPlanController(BaseSkillPlanController):

    def __init__(self, skillPlanID, name = '', description = '', skillRequirements = None, milestones = None, factionID = None, careerPathID = None, npcCorporationDivision = None):
        super(CertifiedSkillPlanController, self).__init__(skillPlanID, name, description, skillRequirements)
        self._milestones = {}
        if milestones:
            self._ConstructMilestonesControllers(milestones)
        self.factionID = factionID
        self.careerPathID = careerPathID
        self.npcCorporationDivision = npcCorporationDivision

    def _ConstructMilestonesControllers(self, milestones):
        for m in milestones:
            milestoneID = uuid.uuid4()
            level = getattr(m, 'level', None)
            if level is not None:
                controller = SkillRequirementMilestoneController(typeID=m.typeID, level=level, milestoneID=milestoneID)
            else:
                controller = TypeIDMilestoneController(typeID=m.typeID, milestoneID=milestoneID)
            self._milestones[milestoneID] = controller

    def GetMilestones(self):
        return self._milestones

    def GetFactionID(self):
        return self.factionID

    def GetCareerPathID(self):
        return self.careerPathID

    def GetName(self):
        return localization.GetByMessageID(self.name)

    def GetInternalName(self):
        return localization.GetByMessageID(self.name, languageID='en')

    def GetDescription(self):
        return localization.GetByMessageID(self.description)

    def IsCertified(self):
        return True

    def IsEditable(self):
        return False

    def IsTrackable(self):
        return True

    def GetTypeName(self):
        return GetByLabel('UI/SkillPlan/CertifiedSkillPlan')
