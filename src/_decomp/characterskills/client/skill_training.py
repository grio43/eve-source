#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\characterskills\client\skill_training.py
import clonegrade

class ClientCharacterSkillInterface(object):

    def __init__(self, skill_service):
        self.skill_service = skill_service

    def get_primary_attribute_id(self, skill_type_id):
        return self.skill_service.GetPrimarySkillAttribute(skill_type_id)

    def get_secondary_attribute_id(self, skill_type_id):
        return self.skill_service.GetSecondarySkillAttribute(skill_type_id)

    def get_skill_rank(self, skill_type_id):
        return self.skill_service.GetSkillRank(skill_type_id)

    def get_skill_level(self, skill_type_id):
        skill = self.skill_service.GetSkillIncludingLapsed(skill_type_id)
        if skill:
            return skill.trainedSkillLevel
        else:
            return 0

    def get_character_attribute_at_time(self, attribute_id, time_offset):
        attribute = self.skill_service.GetCharacterAttribute(attribute_id)
        skill_boosters = self.get_skill_accelerator_boosters()
        if sm.GetService('cloneGradeSvc').IsOmega():
            attribute -= skill_boosters.get_attribute_bonus_expired_at_time_offset(attribute_id, time_offset)
        else:
            attribute -= skill_boosters.get_attribute_bonus_expired_at_time_offset(attribute_id, time_offset) * clonegrade.ALPHA_TRAINING_MULTIPLIER
        return attribute

    def get_skill_points(self, skill_type_id):
        skill = self.skill_service.GetSkillIncludingLapsed(skill_type_id)
        if skill:
            return skill.trainedSkillPoints
        else:
            return 0

    def get_skill_accelerator_boosters(self):
        return self.skill_service.GetSkillAcceleratorBoosters()
