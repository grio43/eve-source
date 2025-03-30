#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\skills\skillplan\milestone\const.py
from itertoolsext.Enum import Enum

@Enum

class MilestoneType(object):
    TYPE_ID_MILESTONE = 'TYPE_ID_MILESTONE'
    SKILL_REQUIREMENT_MILESTONE = 'SKILL_REQUIREMENT_MILESTONE'


@Enum

class MilestoneSubType(object):
    SHIP_MILESTONE = 'SHIP_MILESTONE'
    SKILL_MILESTONE = 'SKILL_MILESTONE'
    MODULE_MILESTONE = 'MODULE_MILESTONE'
    OTHER_MILESTONE = 'OTHER_MILESTONE'
