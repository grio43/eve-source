#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\skills\skillplan\controllers\editableSkillPlanController.py
import copy
import uthread
import uuid
from eve.client.script.ui.skillPlan import skillPlanUtil, skillPlanUISignals
from evetypes.skills import get_dogma_required_skills_recursive
from skills import skillConst
from skills.skillplan import skillPlanValidation, skillPlanConst
from skills.skillplan.controllers.baseSkillPlanController import BaseSkillPlanController
from skills.skillplan.grpc import personalSkillPlanRequest
from skills.skillplan.milestone.milestoneController import TypeIDMilestoneController, SkillRequirementMilestoneController
from skills.skillplan.milestone.milestonesUtil import GetMilestonesToAddAndDeletedIDs

class EditableSkillPlanController(BaseSkillPlanController):

    def __init__(self, skillPlanID, name = '', description = '', skillRequirements = None, ownerID = None, milestoneSvc = None, categoryID = None):
        super(EditableSkillPlanController, self).__init__(skillPlanID, name, description, skillRequirements)
        self._milestoneSvc = milestoneSvc
        self._milestonesToAdd = set()
        self._milestoneIDsToDelete = set()
        self.categoryID = categoryID
        self.ownerID = ownerID

    def GetOwnerID(self):
        return self.ownerID

    def AppendSkillRequirement(self, typeID, level = None):
        if level is None:
            level = self.GetNextLevel(typeID)
        if level is None:
            return
        self.skillRequirements.append((typeID, level))
        self._InvalidateSkillRequirementsDict()
        self._ValidateAndTriggerSkillRequirementsChangedEvent()

    def AppendSkillRequirements(self, skillRequirements):
        for typeID, level in skillRequirements:
            if typeID is None or level is None:
                continue
            self.skillRequirements.append((typeID, level))

        self._InvalidateSkillRequirementsDict()
        self._ValidateAndTriggerSkillRequirementsChangedEvent()

    def _InvalidateSkillRequirementsDict(self):
        self._skillRequirementsDict = None

    def InsertSkillRequirement(self, typeID, level = None, aboveTypeID = None, aboveLevel = None):
        if level is None:
            level = self.GetNextLevel(typeID)
        if level is None:
            return
        self._InsertSkillRequirementAbove(typeID, level, aboveTypeID, aboveLevel)

    def _InsertSkillRequirementAbove(self, typeID, level, aboveTypeID, aboveLevel):
        index = self.GetSkillRequirementIndex(aboveTypeID, aboveLevel)
        self.skillRequirements.insert(index, (typeID, level))
        self._InvalidateSkillRequirementsDict()
        self._ValidateAndTriggerSkillRequirementsChangedEvent()

    def GetNextLevel(self, typeID):
        level = self.GetHighestLevel(typeID) or 0
        level += 1
        if level <= skillConst.skill_max_level:
            return level
        else:
            return None

    def CanRemoveSkillRequirement(self, typeID, level):
        if level != self.GetSkillRequirementsDict().get(typeID, None):
            return False
        skillsRequiring = skillPlanUtil.GetSkillsRequiring(typeID, level)
        index = self.skillRequirements.index((typeID, level))
        for _typeID, _level in self.skillRequirements[index:]:
            if _typeID in skillsRequiring:
                return False

        return True

    def RemoveSkillRequirement(self, typeID, level):
        self.skillRequirements.remove((typeID, level))
        self._InvalidateSkillRequirementsDict()
        self._CheckRemoveMilestones()
        self._ValidateAndTriggerSkillRequirementsChangedEvent()

    def _CheckRemoveMilestones(self):
        missingReqs = self._GetMilestonesMissingRequirements(self.GetMilestones())
        for milestone in missingReqs.iterkeys():
            self.RemoveMilestone(milestone.GetID())

    def _AddSkillsMissingForMilestones(self, milestones):
        missingReqs = self._GetMilestonesMissingRequirements(milestones)
        if len(missingReqs) > 0:
            updatedSkillList = self.GetSkillRequirements()
            for _, skillReqs in missingReqs.iteritems():
                updatedSkillList.extend(skillReqs)

            skillPlanValidation.ValidateSkillPlan(updatedSkillList)
            self.skillRequirements = updatedSkillList
            uthread.new(personalSkillPlanRequest.SetRequiredSkills, self.skillPlanID, self.GetSkillRequirements())

    def _GetMilestonesMissingRequirements(self, milestones):
        skillRequirements = self.GetSkillRequirementsDict()
        missingReqs = {}
        for milestone in milestones.values():
            for typeID, level in milestone.GetRequiredSkills().iteritems():
                if level > skillRequirements.get(typeID, 0):
                    if milestone not in missingReqs:
                        missingReqs[milestone] = []
                    missingReqs[milestone].append((typeID, level))
                    continue

        return missingReqs

    def ResetSkillRequirements(self, skillRequirements):
        self.skillRequirements = skillRequirements
        self._InvalidateSkillRequirementsDict()
        self._ValidateAndTriggerSkillRequirementsChangedEvent()

    def ClearSkillRequirements(self):
        self.skillRequirements = []
        self._InvalidateSkillRequirementsDict()
        skillPlanUISignals.on_skill_requirements_changed(self.skillPlanID)

    def ClearMilestones(self):
        milestoneIDs = self.GetMilestones()
        for milestoneID in milestoneIDs:
            self.RemoveMilestone(milestoneID)

    def MoveSkillRequirement(self, typeID, level, aboveTypeID = None, aboveLevel = None):
        originIndex = self.GetSkillRequirementIndex(typeID, level)
        if aboveTypeID is not None and aboveLevel is not None:
            dropIndex = self.GetSkillRequirementIndex(aboveTypeID, aboveLevel)
        else:
            dropIndex = len(self.skillRequirements)
        if self.IsSkillRequirementMoveValid(originIndex, dropIndex):
            if originIndex > dropIndex:
                typeID, level = self.skillRequirements.pop(originIndex)
                self.skillRequirements.insert(dropIndex, (typeID, level))
            elif dropIndex > originIndex:
                typeID, level = self.skillRequirements[originIndex]
                self.skillRequirements.insert(dropIndex, (typeID, level))
                self.skillRequirements.pop(originIndex)
            skillPlanUISignals.on_skill_requirements_changed(self.skillPlanID)

    def IsSkillRequirementMoveValid(self, originalIndex, targetIndex):
        skillList = copy.copy(self.GetSkillRequirements())
        if originalIndex > targetIndex:
            typeID, level = skillList.pop(originalIndex)
            skillList.insert(targetIndex, (typeID, level))
        elif targetIndex > originalIndex:
            typeID, level = skillList[originalIndex]
            skillList.insert(targetIndex, (typeID, level))
            skillList.pop(originalIndex)
        return skillPlanValidation.IsPlanValid(skillList)

    def IsSkillInsertionValid(self, typeID, level, targetIndex):
        skillList = copy.copy(self.GetSkillRequirements())
        skillList.insert(targetIndex, (typeID, level))
        return skillPlanValidation.IsPlanValid(skillList)

    def _ValidateAndTriggerSkillRequirementsChangedEvent(self):
        self._ValidateSkillRequirements()
        skillPlanUISignals.on_skill_requirements_changed(self.skillPlanID)

    def _ValidateSkillRequirements(self):
        return skillPlanValidation.ValidateSkillPlan(self.GetSkillRequirements())

    def GetSkillRequirementIndex(self, typeID, level):
        if (typeID, level) in self.skillRequirements:
            return self.skillRequirements.index((typeID, level))
        return -1

    def SetName(self, name):
        self.name = name

    def SetDescription(self, description):
        self.description = description

    def AddTypeIDMilestone(self, typeID):
        milestones = self.GetMilestones()
        for each in milestones.itervalues():
            if each.GetData() == typeID:
                return

        if len(milestones) == skillPlanConst.MAX_NUM_MILESTONES:
            return
        milestone = TypeIDMilestoneController(typeID=typeID, milestoneID=uuid.uuid4())
        self._milestonesToAdd.add(milestone)
        self.AddAllSkillsRequiredFor(typeID)
        skillPlanUISignals.on_milestone_added(self.skillPlanID, milestone.GetID())

    def AddSkillRequirementMilestone(self, typeID, level):
        milestones = self.GetMilestones()
        for each in milestones.itervalues():
            if each.GetData() == (typeID, level):
                return

        if len(milestones) == skillPlanConst.MAX_NUM_MILESTONES:
            return
        if not self.AddAllSkillsRequiredFor(typeID, level):
            return
        milestone = SkillRequirementMilestoneController(typeID=typeID, level=level, milestoneID=uuid.uuid4())
        self._milestonesToAdd.add(milestone)
        skillPlanUISignals.on_milestone_added(self.skillPlanID, milestone.GetID())

    def AddAllSkillsRequiredFor(self, typeID, level = None):
        requiredSkills = get_dogma_required_skills_recursive(typeID)
        if level:
            requiredSkills[typeID] = max(requiredSkills.get(typeID, 0), level)
        if not requiredSkills:
            return False
        for _typeID, _level in requiredSkills.iteritems():
            self.skillRequirements.append((_typeID, _level))

        self._InvalidateSkillRequirementsDict()
        self._ValidateAndTriggerSkillRequirementsChangedEvent()
        return True

    def BulkAddAllSkillsRequiredFor(self, typeIDs):
        for typeID in typeIDs:
            requiredSkills = get_dogma_required_skills_recursive(typeID)
            for _typeID, _level in requiredSkills.iteritems():
                if (_typeID, _level) not in self.skillRequirements:
                    self.skillRequirements.append((_typeID, _level))

        self._InvalidateSkillRequirementsDict()
        self._ValidateAndTriggerSkillRequirementsChangedEvent()

    def RemoveMilestone(self, milestoneID):
        toAddMilestones = {milestone.GetID():milestone for milestone in self._milestonesToAdd}
        if milestoneID in toAddMilestones:
            self._milestonesToAdd.remove(toAddMilestones[milestoneID])
        else:
            self._milestoneIDsToDelete.add(milestoneID)
        skillPlanUISignals.on_milestone_removed(self.skillPlanID, milestoneID)

    def GetMilestonesToAdd(self):
        return self._milestonesToAdd

    def GetMilestoneIDsToDelete(self):
        return self._milestoneIDsToDelete

    def SetMilestoneIDsToDelete(self, milestoneIDsToDelete):
        self._milestoneIDsToDelete = milestoneIDsToDelete

    def SetMilestonesToAdd(self, milestonesToAdd):
        self._milestonesToAdd = milestonesToAdd

    def GetMilestones(self):
        if self.GetMilestonesToAdd() or self.GetMilestoneIDsToDelete():
            return {m.GetID():m for m in self.GetMilestonesToAdd()}
        elif self.skillPlanID == skillPlanConst.PLAN_ID_NEW_UNSAVED:
            return {}
        else:
            return self._GetPersistedMilestones()

    def _GetPersistedMilestones(self):
        milestones = self._milestoneSvc.GetMilestonesForSkillPlan(self.skillPlanID)
        self._AddSkillsMissingForMilestones(milestones)
        return milestones

    def GetPersistedMilestone(self, milestoneID):
        self._GetPersistedMilestones().get(milestoneID, None)

    def AdjustMilestonesToAddAndDeletedIDs(self):
        oldMilestonesToDelete = [ self._milestoneSvc.Get(self.skillPlanID, x) for x in self.GetMilestoneIDsToDelete() ]
        milestonesToAdd, milestoneIDsToDelete = GetMilestonesToAddAndDeletedIDs(self.GetMilestonesToAdd(), self.GetMilestoneIDsToDelete(), oldMilestonesToDelete)
        self.SetMilestonesToAdd(milestonesToAdd)
        self.SetMilestoneIDsToDelete(milestoneIDsToDelete)

    def SaveMilestones(self):
        deleteIDs = self.GetMilestoneIDsToDelete()
        if deleteIDs:
            self._milestoneSvc.DeleteMilestones(self.GetID(), deleteIDs)
        self._milestoneIDsToDelete.clear()
        milestonesToAdd = self.GetMilestonesToAdd()
        if milestonesToAdd:
            self._milestoneSvc.SaveMilestones(self.GetID(), milestonesToAdd)
        self._milestonesToAdd.clear()

    def HasEditableCategoryID(self):
        return False

    def GetCopy(self):
        newSkillPlan = self.__class__(skillPlanID=self.GetID(), name=self.GetName(), description=self.GetDescription(), skillRequirements=self.GetSkillRequirements()[:], milestoneSvc=self._milestoneSvc, ownerID=self.GetOwnerID(), categoryID=self.GetCategoryID())
        milestones = {x.GetCopy() for x in self.GetMilestones().itervalues()}
        newSkillPlan.SetMilestonesToAdd(milestones)
        milestonesIDsToDelete = set(self.GetMilestones().keys())
        newSkillPlan.SetMilestoneIDsToDelete(milestonesIDsToDelete)
        return newSkillPlan

    def SetCategoryID(self, categoryID):
        self.categoryID = categoryID

    def GetCategoryID(self):
        return self.categoryID
