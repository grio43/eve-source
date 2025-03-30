#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\getters\skill.py
import evetypes
from .base import GetterAtom

class GetRequiredSkills(GetterAtom):
    atom_id = 371

    def __init__(self, type_id = None, **kwargs):
        self.type_id = type_id

    def get_values(self):
        if not self.type_id:
            return None
        required_skills = sm.GetService('skills').GetRequiredSkills(self.type_id)
        return {'skills': [ (skill_id, skill_level) for skill_id, skill_level in required_skills.iteritems() ],
         'skill_ids': required_skills.keys(),
         'skill_levels': required_skills.values()}

    @classmethod
    def get_subtitle(cls, type_id = None, **kwargs):
        if not type_id:
            return ''
        return u'{} ({})'.format(evetypes.GetName(type_id), type_id)


class GetSkillPlanCareerPathSelected(GetterAtom):
    atom_id = 397

    def get_values(self):
        from eve.client.script.ui.skillPlan.skillPlanUtil import GetVisibleCareerPathTabGroup
        return {'career_path_id': GetVisibleCareerPathTabGroup()}


class GetSkillPlanFactionSelected(GetterAtom):
    atom_id = 401

    def get_values(self):
        from eve.client.script.ui.skillPlan.skillPlanUtil import GetVisibleFactionTabGroup
        return {'faction_id': GetVisibleFactionTabGroup()}


def get_career_path_name(career_path_id):
    from characterdata.careerpath import get_career_path_internal_name
    name = get_career_path_internal_name(career_path_id)
    return name or ''


class GetCareerPathData(GetterAtom):
    atom_id = 398

    def __init__(self, career_path_id = None, **kwargs):
        super(GetCareerPathData, self).__init__(**kwargs)
        self.career_path_id = self.get_atom_parameter_value('career_path_id', career_path_id)

    def get_values(self, **kwargs):
        if self.career_path_id:
            return {'name': get_career_path_name(self.career_path_id)}
        return {}

    @classmethod
    def get_subtitle(cls, career_path_id = None, **kwargs):
        if not career_path_id:
            return ''
        name = get_career_path_name(career_path_id)
        if name:
            return u'{} ({})'.format(name, career_path_id)
        return u'{}'.format(career_path_id)


class GetSkillPlan(GetterAtom):
    atom_id = 495

    def __init__(self, faction_id = None, career_path_id = None, division_id = None, **kwargs):
        super(GetSkillPlan, self).__init__(**kwargs)
        self.faction_id = self.get_atom_parameter_value('faction_id', faction_id)
        self.career_path_id = self.get_atom_parameter_value('career_path_id', career_path_id)
        self.division_id = self.get_atom_parameter_value('division_id', division_id)

    def get_values(self, **kwargs):
        from skills.skillplan.skillPlanFSDLoader import get_skill_plan_by_parameters
        return {'skill_plan_id': get_skill_plan_by_parameters(self.faction_id, self.career_path_id, self.division_id)}
