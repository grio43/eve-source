#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\characterskills\client\UI\util.py
import characterskills
import eveformat
from evetypes import GetDescription, GetGroupName, GetName
from localization import GetByLabel
SKILL_MISSING_TEXT = 'UI/SkillQueue/SkillBookMissing'
SKILL_LEVEL_TEXT = 'UI/Common/SkillLevel'
SKILL_PROGRESS_TEXT = 'UI/SkillQueue/CurrentAndTotalSkillPoints'

def get_skill_title(skill_type_id, skill_level):
    return u'{} {}'.format(GetName(skill_type_id), eveformat.number_roman(skill_level, zero_text='0'))


def get_skill_subtitle(skill_type_id):
    return GetGroupName(skill_type_id)


def get_skill_description(skill_type_id):
    return GetDescription(skill_type_id)


def get_skill_progress_info(skill_type_id):
    skill = sm.GetService('skills').GetSkillIncludingLapsed(skill_type_id)
    if skill is None:
        return get_skill_missing_text()
    current_points = skill.skillPoints
    current_rank = skill.skillRank
    return get_skill_points_text(current_points, current_rank)


def get_skill_missing_text():
    return GetByLabel(SKILL_MISSING_TEXT)


def get_skill_level_text(skill_level):
    roman_level = eveformat.number_roman(skill_level, zero_text='0')
    return GetByLabel(SKILL_LEVEL_TEXT, level=roman_level)


def get_skill_points_text(skill_points, skill_rank):
    total_points = characterskills.GetSPForLevelRaw(skill_rank, 5)
    return GetByLabel(SKILL_PROGRESS_TEXT, current=skill_points or 0, total=total_points)
