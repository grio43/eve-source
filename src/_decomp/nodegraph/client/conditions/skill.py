#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\conditions\skill.py
import evetypes
from .base import Condition

class AvailableSkillPoints(Condition):
    atom_id = 141

    def __init__(self, minimum_amount = None, **kwargs):
        super(AvailableSkillPoints, self).__init__(**kwargs)
        self.minimum_amount = self.get_atom_parameter_value('minimum_amount', minimum_amount)

    def validate(self, **kwargs):
        skill_points = sm.GetService('skills').GetFreeSkillPoints()
        return skill_points >= self.minimum_amount

    @classmethod
    def get_subtitle(cls, minimum_amount = None, **kwargs):
        return u'Minimum amount {}'.format(cls.get_atom_parameter_value('minimum_amount', minimum_amount))


class HasRequiredSkills(Condition):
    atom_id = 370

    def __init__(self, type_id = None, **kwargs):
        super(HasRequiredSkills, self).__init__(**kwargs)
        self.type_id = type_id

    def validate(self, **kwargs):
        if not self.type_id:
            return False
        return sm.GetService('skills').IsSkillRequirementMet(self.type_id)

    @classmethod
    def get_subtitle(cls, type_id = None, **kwargs):
        if not type_id:
            return ''
        return u'{} ({})'.format(evetypes.GetName(type_id), type_id)


class IsOmega(Condition):
    atom_id = 140

    def validate(self, **kwargs):
        return sm.GetService('cloneGradeSvc').IsOmega()


class IsOmegaRequired(Condition):
    atom_id = 386

    def __init__(self, type_id = None, **kwargs):
        super(IsOmegaRequired, self).__init__(**kwargs)
        self.type_id = type_id

    def validate(self, **kwargs):
        if not self.type_id:
            return False
        return sm.GetService('cloneGradeSvc').IsRestrictedForAlpha(self.type_id)

    @classmethod
    def get_subtitle(cls, type_id = None, **kwargs):
        if not type_id:
            return ''
        return u'{} ({})'.format(evetypes.GetName(type_id), type_id)


class SkillInTraining(Condition):
    atom_id = 138

    def __init__(self, type_id = None, **kwargs):
        super(SkillInTraining, self).__init__(**kwargs)
        self.type_id = type_id

    def validate(self, **kwargs):
        return bool(sm.GetService('skillqueue').SkillInTraining(self.type_id))

    @classmethod
    def get_subtitle(cls, type_id = None, **kwargs):
        if not type_id:
            return ''
        return u'{} ({})'.format(evetypes.GetName(type_id), type_id)


class SkillInTrainingQueue(Condition):
    atom_id = 139

    def __init__(self, type_id = None, **kwargs):
        super(SkillInTrainingQueue, self).__init__(**kwargs)
        self.type_id = type_id

    def validate(self, **kwargs):
        return bool(sm.GetService('skillqueue').IsSkillInQueue(self.type_id))

    @classmethod
    def get_subtitle(cls, type_id = None, **kwargs):
        if not type_id:
            return ''
        return u'{} ({})'.format(evetypes.GetName(type_id), type_id)


class SkillTrained(Condition):
    atom_id = 137

    def __init__(self, type_id = None, min_skill_level = None, max_skill_level = None, include_queued = None, **kwargs):
        super(SkillTrained, self).__init__(**kwargs)
        self.type_id = type_id
        self.min_skill_level = self.get_atom_parameter_value('min_skill_level', min_skill_level)
        self.max_skill_level = self.get_atom_parameter_value('max_skill_level', max_skill_level)
        self.include_queued = self.get_atom_parameter_value('include_queued', include_queued)

    def __is_missing_param(self):
        return not self.type_id and not self.min_skill_level and not self.max_skill_level and not self.include_queued

    def validate(self, **kwargs):
        if self.__is_missing_param():
            return
        if not sm.GetService('skills').HasSkill(self.type_id):
            return False
        if self.include_queued:
            skill_level = sm.GetService('skills').MySkillLevelIncludingQueued(self.type_id)
        else:
            skill_level = sm.GetService('skills').MySkillLevel(self.type_id)
        return skill_level >= self.min_skill_level and skill_level <= self.max_skill_level

    @classmethod
    def get_subtitle(cls, type_id = None, min_skill_level = None, max_skill_level = None, **kwargs):
        if not type_id:
            return ''
        return u'Level {} to {} - {} ({})'.format(cls.get_atom_parameter_value('min_skill_level', min_skill_level), cls.get_atom_parameter_value('max_skill_level', max_skill_level), evetypes.GetName(type_id), type_id)


class SkillPlanTraining(Condition):
    atom_id = 413

    def __init__(self, skill_plan_id = None, faction_id = None, career_path_id = None, division_id = None, **kwargs):
        super(SkillPlanTraining, self).__init__(**kwargs)
        self.skill_plan_id = skill_plan_id
        self.faction_id = faction_id
        self.career_path_id = career_path_id
        self.division_id = division_id

    def validate(self, **kwargs):
        from skills.skillplan.skillPlanService import GetSkillPlanSvc
        skill_plan_service = GetSkillPlanSvc()
        return skill_plan_service.IsAnyCertifiedSkillPlanQueuedOrTrained(self.skill_plan_id, self.career_path_id, self.faction_id, self.division_id)


class SkillPlanPageVisible(Condition):
    atom_id = 276

    def __init__(self, skill_plan_id = None, faction_id = None, career_path_id = None, division_id = None, **kwargs):
        super(SkillPlanPageVisible, self).__init__(**kwargs)
        self.skill_plan_id = skill_plan_id
        self.faction_id = faction_id
        self.career_path_id = career_path_id
        self.division_id = division_id

    def _get_visible_skill_plan_id(self):
        from eve.client.script.ui.skillPlan.skillPlanDockablePanel import SkillPlanDockablePanel
        skill_plans_window = SkillPlanDockablePanel.GetIfOpen()
        if skill_plans_window:
            skill_plan_panel = getattr(skill_plans_window, 'skillPlanPanel', None)
            if skill_plan_panel:
                selected_skill_plan = getattr(skill_plan_panel, 'selectedSkillPlan', None)
                if selected_skill_plan:
                    try:
                        return selected_skill_plan.skillPlanID.int
                    except:
                        pass

    def validate(self, **kwargs):
        visible_skill_plan_id = self._get_visible_skill_plan_id()
        if not visible_skill_plan_id:
            return False
        if self.skill_plan_id and visible_skill_plan_id != self.skill_plan_id:
            return False
        if self.faction_id:
            from skills.skillplan.skillPlanFSDLoader import get_skill_plan_faction
            faction_id = get_skill_plan_faction(visible_skill_plan_id)
            if faction_id != self.faction_id:
                return False
        if self.career_path_id:
            from skills.skillplan.skillPlanFSDLoader import get_skill_plan_career_path
            career_path_id = get_skill_plan_career_path(visible_skill_plan_id)
            if career_path_id != self.career_path_id:
                return False
        if self.division_id:
            from skills.skillplan.skillPlanFSDLoader import get_skill_plan_division
            division_id = get_skill_plan_division(visible_skill_plan_id)
            if division_id != self.division_id:
                return False
        return True

    @classmethod
    def get_subtitle(cls, skill_plan_id = None, **kwargs):
        from skills.skillplan.skillPlanFSDLoader import get_skill_plan_name
        name = get_skill_plan_name(skill_plan_id)
        if name:
            return u'{} ({})'.format(name, skill_plan_id)
        return u'{}'.format(skill_plan_id)


class SkillPlanCareerPathSelected(Condition):
    atom_id = 395

    def __init__(self, career_path_id = None, **kwargs):
        super(SkillPlanCareerPathSelected, self).__init__(**kwargs)
        self.career_path_id = career_path_id

    def validate(self, **kwargs):
        from eve.client.script.ui.skillPlan.skillPlanUtil import GetVisibleCareerPathTabGroup
        selected_career_path_id = GetVisibleCareerPathTabGroup()
        return selected_career_path_id and (not self.career_path_id or selected_career_path_id == self.career_path_id)

    @classmethod
    def get_subtitle(cls, career_path_id = '', **kwargs):
        from characterdata.careerpath import get_career_path_internal_name
        name = get_career_path_internal_name(career_path_id)
        if name:
            return u'{} ({})'.format(name, career_path_id)
        return u'{}'.format(career_path_id)


class SkillPlanFactionSelected(Condition):
    atom_id = 399

    def __init__(self, faction_id = None, **kwargs):
        super(SkillPlanFactionSelected, self).__init__(**kwargs)
        self.faction_id = faction_id

    def validate(self, **kwargs):
        from eve.client.script.ui.skillPlan.skillPlanUtil import GetVisibleFactionTabGroup, HasFactionTabGroup
        has_factions = HasFactionTabGroup()
        if not has_factions:
            return True
        selected_faction_id = GetVisibleFactionTabGroup()
        return selected_faction_id and (not self.faction_id or selected_faction_id == self.faction_id)

    @classmethod
    def get_subtitle(cls, faction_id = '', **kwargs):
        from characterdata.factions import get_faction_name
        name = get_faction_name(faction_id) if faction_id else ''
        if name:
            return u'{} ({})'.format(name, faction_id)
        return u'{}'.format(faction_id)


class SkillPlanContentsShown(Condition):
    atom_id = 443

    def validate(self, **kwargs):
        from eve.client.script.ui.skillPlan.skillPlanDockablePanel import SkillPlanDockablePanel
        skill_plans_window = SkillPlanDockablePanel.GetIfOpen()
        if not skill_plans_window:
            return False
        skill_plan_panel = getattr(skill_plans_window, 'skillPlanPanel', None)
        if skill_plan_panel:
            selected_skill_plan_container = getattr(skill_plan_panel, 'selectedSkillPlanContainer', None)
            if selected_skill_plan_container:
                return selected_skill_plan_container.skillsVisible
        return False
