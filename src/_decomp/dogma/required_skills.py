#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\required_skills.py
import evetypes
from dogma.const import attributeRequiredSkill1
from dogma.const import attributeRequiredSkill1Level
from dogma.const import attributeRequiredSkill2
from dogma.const import attributeRequiredSkill2Level
from dogma.const import attributeRequiredSkill3
from dogma.const import attributeRequiredSkill3Level
from dogma.const import attributeRequiredSkill4
from dogma.const import attributeRequiredSkill4Level
from dogma.const import attributeRequiredSkill5
from dogma.const import attributeRequiredSkill5Level
from dogma.const import attributeRequiredSkill6
from dogma.const import attributeRequiredSkill6Level
from dogma import data as dogma_data
REQUIRED_SKILL_AND_LEVEL_ATTRIBUTES = [(attributeRequiredSkill1, attributeRequiredSkill1Level),
 (attributeRequiredSkill2, attributeRequiredSkill2Level),
 (attributeRequiredSkill3, attributeRequiredSkill3Level),
 (attributeRequiredSkill4, attributeRequiredSkill4Level),
 (attributeRequiredSkill5, attributeRequiredSkill5Level),
 (attributeRequiredSkill6, attributeRequiredSkill6Level)]

class RequiredSkillData(object):

    def __init__(self, type_id, type_name, tree_level, skill_level):
        self.type_id = type_id
        self.type_name = type_name
        self.tree_level = tree_level
        self.skill_level = skill_level

    def __str__(self):
        return '{}\t{}\t{}\t{}'.format(self.type_id, self.type_name, self.tree_level, self.skill_level)


def _construct_required_skill_tree(tree_level, type_id, result):
    new_tree_level = tree_level + 1
    for skillAttributeID, levelAttributeID in REQUIRED_SKILL_AND_LEVEL_ATTRIBUTES:
        skill_type_id = dogma_data.get_type_attribute(type_id, skillAttributeID)
        level = dogma_data.get_type_attribute(type_id, levelAttributeID)
        if skill_type_id and level:
            skill_type_id = int(skill_type_id)
            level = int(level)
            result.append(RequiredSkillData(skill_type_id, evetypes.GetName(skill_type_id), new_tree_level, level))
            _construct_required_skill_tree(new_tree_level, skill_type_id, result)


def get_esp_required_skills_for_type(type_id):
    result = []
    _construct_required_skill_tree(0, type_id, result)
    return result
