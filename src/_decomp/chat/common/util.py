#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\chat\common\util.py
from carbon.common.script.sys import service
from eveuniverse.solar_systems import is_empty_system
from eve.common.script.sys.idCheckers import IsTriglavianSystem, IsWormholeSystem, IsZarzakh
from chat.common.const import MemberClassification, CLASSIFACTION_TO_COLOR

def is_local_chat_suppressed(solar_system_id):
    return is_empty_system(solar_system_id)


def is_local_chat_delayed(solar_system_id):
    return IsWormholeSystem(solar_system_id) or IsZarzakh(solar_system_id) or IsTriglavianSystem(solar_system_id)


def get_classification_from_role(role):
    if role is None:
        return MemberClassification.UNSPECIFIED
    if role & service.ROLE_CHTINVISIBLE == service.ROLE_CHTINVISIBLE:
        return MemberClassification.INVISIBLE
    if role & service.ROLE_PINKCHAT == service.ROLE_PINKCHAT:
        return MemberClassification.NPC
    if role & service.ROLE_QA == service.ROLE_QA:
        return MemberClassification.DEVELOPER
    mask = service.ROLE_GML | service.ROLE_GMH | service.ROLE_GMS | service.ROLE_ADMIN
    if role & mask != 0:
        return MemberClassification.GAME_MASTER
    mask = service.ROLE_CENTURION | service.ROLE_LEGIONEER
    if role & mask != 0:
        return MemberClassification.VOLUNTEER
    return MemberClassification.UNSPECIFIED


def get_color_for_role(role):
    classification = get_classification_from_role(role)
    return CLASSIFACTION_TO_COLOR.get(classification, '0x99ffffff')
