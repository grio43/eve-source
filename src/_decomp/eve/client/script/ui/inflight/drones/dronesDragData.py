#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\drones\dronesDragData.py
from carbonui.control.dragdrop.dragdata import TypeDragData
from carbonui.control.dragdrop.dragdata.basedragdata import BaseDragData
from eve.client.script.ui.inflight.drones.dronesUtil import GetDronesInBay, GetDronesInLocalSpace

class _HasDronesInterface:

    def GetDroneIDs(self):
        raise NotImplementedError

    def GetTypeID(self):
        raise NotImplementedError


class _HasInBayDronesInterface(_HasDronesInterface):
    pass


class _HasInSpaceDronesInterface(_HasDronesInterface):
    pass


class DroneEntryDragData(TypeDragData):
    droneState = None

    def __init__(self, itemID, typeID):
        super(DroneEntryDragData, self).__init__(typeID)
        self.itemID = itemID

    def GetIconTexturePath(self):
        return 'res:/UI/Texture/WindowIcons/dronebay.png'

    def GetDroneIDs(self):
        return [self.itemID]


class DroneEntryInBayDragData(DroneEntryDragData, _HasInBayDronesInterface):
    pass


class DroneEntryInSpaceDragData(DroneEntryDragData, _HasInSpaceDronesInterface):
    pass


class BaseDroneGroupDragData(BaseDragData):

    def GetIconTexturePath(self):
        return 'res:/UI/Texture/WindowIcons/dronebay.png'

    def get_link(self):
        return None

    def GetDronesDragData(self):
        raise NotImplementedError

    def GetTypeID(self):
        items = self.GetDronesDragData()
        if items:
            return items[0].typeID


class AllDronesInBayDragData(BaseDroneGroupDragData, _HasInBayDronesInterface):

    def GetDronesDragData(self):
        return [ DroneEntryInBayDragData(drone.itemID, drone.typeID) for drone in self.GetDroneInvItems() ]

    def GetDroneInvItems(self):
        return GetDronesInBay()

    def GetDroneIDs(self):
        return [ drone.itemID for drone in self.GetDroneInvItems() ]


class DronesInBayDragData(BaseDroneGroupDragData, _HasInBayDronesInterface):

    def __init__(self, droneIDs):
        self.droneIDs = droneIDs

    def GetDronesDragData(self):
        return [ DroneEntryInBayDragData(item.itemID, item.typeID) for item in GetDronesInBay() if item.itemID in self.droneIDs ]

    def GetDroneInvItems(self):
        return [ item for item in GetDronesInBay() if item.itemID in self.droneIDs ]

    def GetDroneIDs(self):
        return self.droneIDs


class AllDronesInSpaceDragData(BaseDroneGroupDragData, _HasInSpaceDronesInterface):

    def GetDronesDragData(self):
        return [ DroneEntryInSpaceDragData(drone.droneID, drone.typeID) for drone in self.GetSlimItems() ]

    def GetSlimItems(self):
        return GetDronesInLocalSpace()

    def GetDroneIDs(self):
        return [ drone.droneID for drone in self.GetSlimItems() ]


class DronesInSpaceDragData(BaseDroneGroupDragData, _HasInSpaceDronesInterface):

    def __init__(self, droneIDs):
        self.droneIDs = droneIDs

    def GetDronesDragData(self):
        return [ DroneEntryInSpaceDragData(drone.droneID, drone.typeID) for drone in GetDronesInLocalSpace() if drone.droneID in self.droneIDs ]

    def GetDroneIDs(self):
        return self.droneIDs


def _GetDroneIDs(dataClass, dragData):
    droneIDs = set()
    for data in dragData:
        if isinstance(data, dataClass):
            droneIDs.update(data.GetDroneIDs())

    return list(droneIDs)


def GetDroneIDs(dragData):
    return _GetDroneIDs(_HasDronesInterface, dragData)


def GetInBayDroneIDs(dragData):
    return _GetDroneIDs(_HasInBayDronesInterface, dragData)


def GetInSpaceDroneIDs(dragData):
    return _GetDroneIDs(_HasInSpaceDronesInterface, dragData)


def HasInBayDroneIDs(dragData):
    return bool(GetInBayDroneIDs(dragData))


def HasInSpaceDroneIDs(dragData):
    return bool(GetInSpaceDroneIDs(dragData))
