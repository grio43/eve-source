#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipprogression\boarding_moment\__init__.py
from ballparkCommon.docking import CanDock
import evetypes
from eve.common.lib import appConst
from fsdBuiltData.common.graphicIDs import GetSofHullName
import logging
import shipgroup
from .const import MomentSteps, ShipSize, ShipShape, SIZE_BY_EVE_TYPE_ID, SIZE_BY_HULL_NAME, SIZE_BY_SHIP_CLASS_ID, SHAPE_BY_EVE_TYPE_ID, SHAPE_BY_HULL_NAME, SHAPE_BY_SHIP_CLASS_ID, UNIQUE_MOMENT_ID_BY_EVE_HULL_NAME, FACTION_BACKGROUND_LOGOS_IDS, UNDEFINED_FACTION_LOGO_ID
from .momentsByHull import MOMENTS_BY_HULL
from .momentsByShape import MOMENTS_BY_SHAPE
from .boardingMomentSvc import GetBoardingMomentService
log = logging.getLogger(__name__)

def should_autoplay_boarding_moment(type_id):
    if not can_play_boarding_moment(type_id):
        return False
    if evetypes.GetGroupID(type_id) in [appConst.groupShuttle, appConst.groupCorvette]:
        return False
    return GetBoardingMomentService().ShouldPlay(type_id)


def can_play_boarding_moment(type_id):
    if is_excluded_from_boarding_moment(type_id):
        return False
    return True


def is_excluded_from_boarding_moment(type_id):
    return evetypes.GetGroupID(type_id) in [appConst.groupCapsule]


def get_boarding_moment_details(type_id, ship_model):
    shape_group = get_ship_shape_group(type_id, ship_model)
    size_group = get_ship_size_group(type_id, ship_model.GetBoundingSphereRadius())
    graphicID = evetypes.GetGraphicID(type_id)
    hullName = GetSofHullName(graphicID)
    if hullName in MOMENTS_BY_HULL:
        log.info('Boarding Moment - [%s] - unique boarding for hull %s', type_id, hullName)
        moments = MOMENTS_BY_HULL.get(hullName)
    else:
        log.info('Boarding Moment - [%s] %s - %s %s', type_id, evetypes.GetName(type_id), shape_group, size_group)
        moments = MOMENTS_BY_SHAPE.get((shape_group, size_group), None)
    faction_group = get_ship_faction_group(type_id)
    return (moments,
     shape_group,
     size_group,
     faction_group,
     get_unique_moment_id(type_id))


def get_ship_size_group(type_id, size):
    if type_id in SIZE_BY_EVE_TYPE_ID:
        return SIZE_BY_EVE_TYPE_ID[type_id]
    graphic_id = evetypes.GetGraphicID(type_id)
    hull_name = GetSofHullName(graphic_id)
    if hull_name in SIZE_BY_HULL_NAME:
        return SIZE_BY_HULL_NAME[hull_name]
    ship_class_id = shipgroup.get_ship_class_id(type_id)
    if ship_class_id in SIZE_BY_SHIP_CLASS_ID:
        return SIZE_BY_SHIP_CLASS_ID[ship_class_id]
    elif not size or size <= 234:
        return ShipSize.SMALL
    elif size <= 1877:
        return ShipSize.MEDIUM
    else:
        return ShipSize.LARGE


def get_unique_moment_id(type_id):
    graphic_id = evetypes.GetGraphicID(type_id)
    hull_name = GetSofHullName(graphic_id)
    return UNIQUE_MOMENT_ID_BY_EVE_HULL_NAME.get(hull_name, 0.0)


def get_ship_shape_group(type_id, model):
    if type_id in SHAPE_BY_EVE_TYPE_ID:
        return SHAPE_BY_EVE_TYPE_ID[type_id]
    graphic_id = evetypes.GetGraphicID(type_id)
    hull_name = GetSofHullName(graphic_id)
    if hull_name in UNIQUE_MOMENT_ID_BY_EVE_HULL_NAME:
        return ShipShape.UNDEFINED
    if hull_name in SHAPE_BY_HULL_NAME:
        return SHAPE_BY_HULL_NAME[hull_name]
    ship_class_id = shipgroup.get_ship_class_id(type_id)
    if ship_class_id in SHAPE_BY_SHIP_CLASS_ID:
        return SHAPE_BY_SHIP_CLASS_ID[ship_class_id]
    ship_shape = get_ship_shape_group_based_on_model(model)
    return ship_shape


def get_ship_shape_group_based_on_model(ship_model):
    ratio = 1.5
    max_ratio = 0.8
    x, y, z = ship_model.generatedShapeEllipsoidRadius
    if max(ship_model.generatedShapeEllipsoidRadius) == -1:
        x, y, z = ship_model.shapeEllipsoidRadius
    max_value = max(x, y, z) * max_ratio
    if y >= max_value:
        if y > x * ratio or y > z * ratio:
            return ShipShape.TALL
    elif x >= max_value:
        if x > y * ratio or x > z * ratio:
            return ShipShape.WIDE
    elif z >= max_value:
        if z > x * ratio or z > y * ratio:
            return ShipShape.LONG
    return ShipShape.BOX


def get_ship_faction_group(type_id):
    faction_id = evetypes.GetFactionID(type_id)
    return FACTION_BACKGROUND_LOGOS_IDS.get(faction_id, UNDEFINED_FACTION_LOGO_ID)
