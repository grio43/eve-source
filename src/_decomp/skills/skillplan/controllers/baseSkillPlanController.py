#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\skills\skillplan\controllers\baseSkillPlanController.py
import collections
import evetypes
from characterskills.util import GetProgressRatioForSkillLevels, GetInTrainingRatioForSkillLevels, GetSkillRequirementsDictFromSkillLevels, GetTotalSkillPoints
from eve.common.lib import appConst
from localization import GetByLabel
from localization.formatters import timeIntervalFormatters
from skills.client.util import buy_missing_skills
from skills.skillplan import skillPlanConst, skillPlanValidation

class BaseSkillPlanController(object):

    def __init__(self, skillPlanID, name = '', description = '', skillRequirements = None):
        self.skillPlanID = skillPlanID
        self.name = name
        self.description = description
        self.skillRequirements = skillRequirements or []
        self._skillRequirementsDict = None

    def GetName(self):
        return self.name

    def GetTypeName(self):
        return GetByLabel('UI/SkillPlan/SkillPlan')

    def GetInternalName(self):
        return self.name

    def GetID(self):
        return self.skillPlanID

    def GetDescription(self):
        return self.description

    def GetSkillRequirements(self):
        return self.skillRequirements or []

    def GetCategoryID(self):
        return None

    def GetOwnerID(self):
        return None

    def GetMilestones(self):
        raise NotImplementedError

    def GetMilestone(self, milestoneID):
        return self.GetMilestones().get(milestoneID, None)

    def GetNextMilestoneUnlocked(self):
        milestones = [ milestone for milestone in self.GetMilestones().values() if not milestone.IsCompleted() ]
        if not milestones:
            return None
        ret = [ (self.GetMilestoneLastSkillIndex(milestone.GetID()), milestone) for milestone in milestones ]
        _, milestone = sorted(ret)[0]
        return milestone

    def GetMilestoneLastSkillIndex(self, milestoneID):
        milestoneReq = self.GetMilestone(milestoneID).GetRequiredSkills()
        return max([ self.GetSkillRequirements().index(req) for req in milestoneReq.iteritems() ])

    def HasEmptyMilestoneSlots(self):
        return len(self.GetMilestones()) < skillPlanConst.MAX_NUM_MILESTONES

    def GetSkillRequirementsDict(self):
        if self._skillRequirementsDict is not None:
            return self._skillRequirementsDict
        ret = collections.OrderedDict()
        for typeID, level in self.GetSkillRequirements():
            ret[typeID] = max(ret.get(typeID, 0), level)

        self._skillRequirementsDict = ret
        return ret

    def GetHighestLevel(self, typeID):
        return self.GetSkillRequirementsDict().get(typeID, None)

    def GetTotalTrainingTime(self):
        skills = self.GetSkillRequirementsDict()
        return long(sm.GetService('skills').GetTrainingTimeForSkillsExcludeTrained(skills))

    def GetTotalTrainingTimeText(self):
        duration = self.GetTotalTrainingTime()
        return self.GetTimeLeftFormattedText(duration)

    def GetTotalTrainingTimeLeft(self):
        skills = self.GetSkillRequirementsDict()
        return long(sm.GetService('skills').GetTrainingTimeForSkills(skills))

    def GetTotalTrainingTimeLeftText(self):
        if self.IsCompleted():
            return GetByLabel('UI/SkillPlan/Completed')
        else:
            duration = self.GetTotalTrainingTimeLeft()
            return self.GetTimeLeftFormattedText(duration)

    def GetTimeLeftFormattedText(self, duration):
        if duration > appConst.DAY:
            showTo = 'hour'
        elif duration > appConst.HOUR:
            showTo = 'minute'
        else:
            showTo = 'second'
        return timeIntervalFormatters.FormatTimeIntervalShortWritten(duration, showFrom='day', showTo=showTo)

    def GetProgressRatio(self):
        return GetProgressRatioForSkillLevels(self.GetSkillRequirementsDict())

    def GetInTrainingRatio(self):
        return GetInTrainingRatioForSkillLevels(self.GetSkillRequirementsDict())

    def GetLastSkillCompletedAtRatio(self, skillRequirements):
        skillRequirements = self.GetSkillRequirements()
        index = max([ skillRequirements.index(skillReq) for skillReq in skillRequirements ])
        skillRequirementsDict = GetSkillRequirementsDictFromSkillLevels(skillRequirements[:index + 1])
        spAtCompleted = GetTotalSkillPoints(skillRequirementsDict)
        return float(spAtCompleted) / GetTotalSkillPoints(self.GetSkillRequirementsDict())

    def IsCompleted(self):
        required = self.GetSkillRequirementsDict()
        if not required:
            return False
        for typeID, level in required.iteritems():
            if sm.GetService('skills').MySkillLevel(typeID) < level:
                return False

        return True

    def IsTrainable(self):
        return not self.IsOmegaLocked() and not self.IsMissingSkillbooks()

    def IsQueuedOrTrained(self):
        return not len(self.GetUntrainedSkills())

    def IsOmega(self):
        for typeID in self.GetSkillRequirementsDict().keys():
            if sm.GetService('cloneGradeSvc').IsRestrictedForAlpha(typeID):
                return True

        return False

    def GetNumOmegaSkills(self):
        nbOmegaSkills = 0
        for typeID in self.GetSkillRequirementsDict().keys():
            if sm.GetService('cloneGradeSvc').IsRestrictedForAlpha(typeID):
                nbOmegaSkills += 1

        return nbOmegaSkills

    def IsOmegaLocked(self):
        return self.IsOmega() and not sm.GetService('cloneGradeSvc').IsOmega()

    def IsMissingSkillbooks(self):
        return bool(self.GetMissingSkillbooks())

    def GetMissingSkillbooks(self):
        typeIDs = self.GetSkillRequirementsDict().keys()
        return [ typeID for typeID in typeIDs if sm.GetService('skills').GetMyLevelIncludingLapsed(typeID) is None ]

    def IsCertified(self):
        return False

    def AddToTrainingQueue(self):
        if buy_missing_skills(self.GetSkillRequirementsDict().keys()):
            numSkillsAdded = sm.GetService('skillqueue').AddSkillsToQueue(self.GetUntrainedSkills())
            self.NotifyOfSkillPlanTrainingStarted()
            return numSkillsAdded
        return 0

    def NotifyOfSkillPlanTrainingStarted(self):
        sm.ScatterEvent('OnSkillPlanTrainingStarted', self.GetID(), self.GetName())

    def GetUntrainedSkills(self):
        return [ (typeID, level) for typeID, level in self.GetSkillRequirements() if sm.GetService('skills').MySkillLevelIncludingQueued(typeID) < level ]

    def IsEditable(self):
        raise NotImplementedError

    def IsTrackable(self):
        raise NotImplementedError

    def IsValid(self):
        return skillPlanValidation.IsPlanValid(self.GetSkillRequirements())

    def GetRequirementsClipboardText(self):
        skillsTxt = ''
        for typeID, level in self.GetSkillRequirements():
            skillsTxt += '%s %s\n' % (evetypes.GetName(typeID), level)

        return skillsTxt

    def GetMilestonesSet(self):
        return set(self.GetMilestones().values())

    def GetFactionID(self):
        return None

    def GetCareerPathID(self):
        return None
