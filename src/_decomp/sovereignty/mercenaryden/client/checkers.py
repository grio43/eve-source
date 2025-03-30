#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\mercenaryden\client\checkers.py
from carbon.common.script.sys.serviceManager import ServiceManager
from eve.common.lib.appConst import maxApproachDistance, maxCargoContainerTransferDistance
from eve.common.script.sys.idCheckers import IsMercenaryDen

def is_mercenary_den_owned(group_id, owner_id):
    if not IsMercenaryDen(group_id):
        return False
    if owner_id != session.charid:
        return False
    return True


def is_mercenary_den_close_enough_to_see_option_to_configure(item_id):
    return _is_mercenary_den_closer_than(item_id, distance=maxApproachDistance)


def is_mercenary_den_close_enough_to_configure(item_id):
    return _is_mercenary_den_closer_than(item_id, distance=maxCargoContainerTransferDistance)


def _is_mercenary_den_closer_than(item_id, distance):
    autopilot_service = ServiceManager.Instance().GetService('autoPilot')
    return autopilot_service.IsSystemNavigationComplete(item_id, interactionRange=distance)
