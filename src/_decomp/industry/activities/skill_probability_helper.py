#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\industry\activities\skill_probability_helper.py
import evetypes
import industry
import logging
import traceback
logger = logging.getLogger(__name__)

class SkillProbabilityHelper(object):
    _types_to_give_lower_skill_probability = None

    @classmethod
    def get_probability_from_type_id(cls, type_id):
        if not cls._types_to_give_lower_skill_probability:
            try:
                cls._types_to_give_lower_skill_probability = evetypes.GetTypeIDsByListID(evetypes.TYPE_LIST_LOWER_INVENTION_SKILL_PROBABILITY)
            except Exception as e:
                logger.exception('Failed to GetTypeIDsByListID for TYPE_LIST_LOWER_INVENTION_SKILL_PROBABILITY (%s) - %s', evetypes.TYPE_LIST_LOWER_INVENTION_SKILL_PROBABILITY, traceback.format_exc())

        if cls._types_to_give_lower_skill_probability:
            if type_id in cls._types_to_give_lower_skill_probability:
                return industry.INVENTION_SKILL_PROBABILITY_LOWER
        return industry.INVENTION_SKILL_PROBABILITY
