#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\drones\dronesUtil.py
import evetypes
import itertoolsext
from carbonui import uiconst
from carbonui.uicore import uicore
from carbonui.util.bunch import Bunch
from carbonui.window.settings import GetRegisteredState
from eve.client.script.ui.inflight.drones.dronesConst import DRONESTATE_INSPACE, DRONESTATE_INBAY
from eve.client.script.ui.services.menuSvcExtras.droneFunctions import ReturnToDroneBay
from eve.common.lib import appConst
from eveservices.menu import GetMenuService
from localization import GetByLabel

def GetDronesInBay():
    if session.shipid:
        return sm.GetService('invCache').GetInventoryFromId(session.shipid).ListDroneBay()
    return []


def GetDronesInLocalSpace():
    ballpark = sm.GetService('michelle').GetBallpark()
    if ballpark is None:
        return []
    drones = sm.GetService('michelle').GetDrones()
    return [ drones[droneID] for droneID in drones if drones[droneID].ownerID == session.charid or drones[droneID].controllerID == session.shipid ]


def GetDroneIDsInSpace():
    inBayIDs = GetDroneIDsInBay()
    droneIDs = [ drone.droneID for drone in GetDronesInLocalSpace() if drone.droneID not in inBayIDs ]
    return sorted(droneIDs)


def GetDroneIDsInBay():
    droneIDs = [ drone.itemID for drone in GetDronesInBay() ]
    return sorted(droneIDs)


def GetNumberOfDronesInBay():
    return sum([ invItem.stacksize for invItem in GetDronesInBay() ])


def stop_and_recall_drones():
    uicore.cmd.GetCommandAndExecute('CmdStopShip')
    ReturnToDroneBay([ drone.droneID for drone in GetDronesInLocalSpace() ])


def GetTypeIDForManyDrones(droneState, droneData):
    if not droneData:
        return None
    if droneState == DRONESTATE_INBAY:
        firstDroneData = droneData[0]
        invItem, viewOnly, voucher = firstDroneData
        return invItem.typeID
    if droneState == DRONESTATE_INSPACE:
        lowPriorityDrones = [const.groupMiningDrone, const.groupSalvageDrone, const.groupUnanchoringDrone]

        def IsHigherPrioritySpaceDrone(droneData):
            droneID, typeID, ownerID, locationID = droneData
            if evetypes.GetGroupID(typeID) in lowPriorityDrones:
                return False
            return True

        priorityDrone = itertoolsext.first_or_default(droneData, predicate=IsHigherPrioritySpaceDrone, default=droneData[0])
        droneSlimItem = sm.GetService('michelle').GetItem(priorityDrone[0])
        if droneSlimItem:
            return droneSlimItem.typeID


def ExpandRadialMenuForInSpaceGroup(clickedObject, displayName, droneData):
    manyItemsData = Bunch(menuFunction=GetMenuService().DroneMenu, itemData=droneData, displayName='<b>%s</b>' % displayName)
    typeID = GetTypeIDForManyDrones(DRONESTATE_INSPACE, droneData)
    GetMenuService().TryExpandActionMenu(itemID=None, typeID=typeID, clickedObject=clickedObject, manyItemsData=manyItemsData)


def ExpandRadialMenuForInBayGroup(clickedObject, displayName, droneData):
    manyItemsData = Bunch(menuFunction=GetMenuService().InvItemMenu, itemData=droneData, displayName='<b>%s</b>' % displayName)
    typeID = GetTypeIDForManyDrones(DRONESTATE_INBAY, droneData)
    GetMenuService().TryExpandActionMenu(itemID=None, typeID=typeID, clickedObject=clickedObject, manyItemsData=manyItemsData)


def IsDronesWindowCompact():
    return GetRegisteredState('droneview', 'compact', False)


def LoadShortcutTooltip(tooltipPanel, commandName):
    tooltipPanel.LoadGeneric2ColumnTemplate()
    command = uicore.cmd.commandMap.GetCommandByName(commandName)
    tooltipPanel.AddLabelShortcut(command.GetName(), command.GetShortcutAsString())
    detailedDescription = command.GetDetailedDescription()
    if detailedDescription:
        tooltipPanel.AddLabelMedium(text=detailedDescription, align=uiconst.TOPLEFT, wrapWidth=200, colSpan=tooltipPanel.columns)


def GetMaxDronesInSpace():
    return int(sm.GetService('godma').GetItem(session.charid).maxActiveDrones) or 0


def GetPrimaryActionName(typeID):
    groupID = evetypes.GetGroupID(typeID)
    if groupID == appConst.groupMiningDrone:
        return GetByLabel('UI/Drones/MineWithDrone')
    elif groupID == appConst.groupSalvageDrone:
        return GetByLabel('UI/Drones/Salvage')
    else:
        return GetByLabel('UI/Drones/EngageTarget')
