#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveformat\client\location.py
from evePathfinder.core import IsUnreachableJumpCount
from eveformat import localization, tags
from eveformat.client import context
from eveuniverse.security import securityClassLowSec
from security.client.securityColor import get_security_status_color

def solar_system_security_status(solar_system_id, lawless = False):
    security_status = get_security_status(solar_system_id)
    security_status_text = colorize_security_status(security_status)
    if lawless:
        security_status_text = tags.color(localization.get_by_label('UI/Map/StarMap/LawlessSecStatus', secStatusText=get_security_status(solar_system_id)), GetLawlessSystemSecStatusColor(security_status))
    return u'{security_status}{icon}'.format(security_status=security_status_text, icon=get_security_modifier_icon_text(solar_system_id))


def GetLawlessSystemSecStatusColor(securityStatus):
    from eve.client.script.ui import eveColor
    if securityStatus < securityClassLowSec:
        return eveColor.DANGER_RED
    else:
        return eveColor.WARNING_ORANGE


def solar_system_with_security_and_jumps(solar_system_id, from_solar_system_id = None):
    if from_solar_system_id is None:
        from_solar_system_id = get_current_solar_system()
    num_jumps = get_jump_distance_between(from_solar_system_id, solar_system_id)
    if num_jumps is None:
        return solar_system_with_security(solar_system_id)
    return localization.get_by_label('UI/Agency/LocationAndNumJumps', location=solar_system_id, secStatus=solar_system_security_status(solar_system_id), jumps=localization.get_by_label('UI/Common/NumJumps', numJumps=num_jumps))


def solar_system_with_security(solar_system_id):
    security_status = solar_system_security_status(solar_system_id)
    return localization.get_by_label('UI/Agency/Location', location=solar_system_id, secStatus=security_status)


def security_status(security_status):
    return colorize_security_status(round_security_status(security_status))


def get_current_solar_system():
    return context.get_session().solarsystemid2


def get_security_status(solar_system_id):
    security_status = context.get_service('map').GetSystemSecurityValue(solar_system_id)
    return round_security_status(security_status)


def colorize_security_status(security_status):
    return tags.color(security_status, get_security_status_color(security_status))


def round_security_status(security_status):
    security_status = round(security_status, 1)
    if security_status == -0.0:
        security_status = 0.0
    return security_status


def get_jump_distance_between(from_solar_system_id, to_solar_system_id):
    distance = context.get_service('clientPathfinderService').GetJumpCount(from_solar_system_id, to_solar_system_id)
    if IsUnreachableJumpCount(distance):
        return None
    return distance


def get_security_modifier_icon_text(solar_system_id):
    return context.get_service('securitySvc').get_security_modifier_icon_text(solar_system_id)
