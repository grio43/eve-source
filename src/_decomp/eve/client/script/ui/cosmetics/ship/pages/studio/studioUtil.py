#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\studio\studioUtil.py
import math
from appConst import factionDeathless
from eve.client.script.ui.shared.shipTree import shipTreeConst
from carbon.common.script.sys.serviceConst import ROLE_GML
RANDOMIZE_BUTTON_ANALYTIC_ID = 'ShipSKINR_RandomizeDesign'
SHARE_BUTTON_ANALYTIC_ID = 'ShipSKINR_ShareDesign'
CIRCULAR_LAYOUT_RATIO = 0.9

def get_radial_position(radius, angle_deg):
    x = radius * math.cos(math.radians(angle_deg))
    y = radius * math.sin(math.radians(angle_deg))
    return (x, y)


def get_circular_layout_radius(width, height):
    diameter = min(width, height)
    return diameter * 0.5 * CIRCULAR_LAYOUT_RATIO


def is_green_screen_enabled():
    if session.role & ROLE_GML:
        from eve.devtools.script.insider import qa_green_screen_setting
        return qa_green_screen_setting.is_enabled()
    return False


def get_ship_factions():
    BLACKLISTED_FACTION_IDS = ()
    return [ x for x in shipTreeConst.FACTIONS if x not in BLACKLISTED_FACTION_IDS ]
