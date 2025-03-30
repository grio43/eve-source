#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\drones\droneGroupsController.py
import blue
import localization
from eve.client.script.ui.inflight.drones.dronesConst import DRONESTATE_INBAY, DRONESTATE_INSPACE
from eve.client.script.ui.inflight.drones.dronesUtil import GetDronesInLocalSpace, GetDronesInBay
from eve.client.script.ui.util.utilWindows import NamePopup
from signals import Signal
settingsName = 'droneBlah2'

class _DroneGroupsController:
    __notifyevents__ = ['OnItemLaunch']

    def __init__(self):
        sm.RegisterNotify(self)
        self.groups = self._SettifyGroups(settings.user.ui.Get(settingsName, {}))
        self._UpdateGroupsByID()
        self.on_groups_changed = Signal('on_groups_changed')

    def OnItemLaunch(self, ids):
        reload = False
        for oldID, newIDs in ids.iteritems():
            group = self.GetDroneGroup(oldID)
            if group is not None:
                for newID in newIDs:
                    if newID != oldID:
                        group['droneIDs'].add(newID)
                        reload = True

        if reload:
            self.OnGroupsChanged()

    def _UpdateGroupsByID(self):
        self.groupsByID = {group.get('id'):group for group in self.groups.itervalues()}

    def GetGroupsByName(self):
        return self.groups

    def GetGroupNames(self):
        return self.groups.keys()[:]

    def GetGroupByID(self, groupID):
        return self.groupsByID.get(groupID, None)

    def GetFavoriteGroup(self):
        return self.GetGroupByID(self.GetFavoriteGroupID())

    def GetFavoriteGroupID(self):
        settingName = self._GetFavoriteDroneGroupConfigName()
        return settings.user.ui.Get(settingName, None)

    def SetFavoriteGroupID(self, value):
        settingName = self._GetFavoriteDroneGroupConfigName()
        settings.user.ui.Set(settingName, value)

    def GetFavoriteGroupDroneIDsInBayOrSpace(self):
        favoriteGroup = self.GetFavoriteGroup()
        if favoriteGroup:
            dronesInBay = GetDronesInBay()
            dronesIDsInSpace = [ x.droneID for x in sm.GetService('michelle').GetDrones().itervalues() ]
            allDroneIDs = [ x.itemID for x in dronesInBay ] + dronesIDsInSpace
            droneIDsInFavorite = favoriteGroup.get('droneIDs')
            return set(droneIDsInFavorite).intersection(allDroneIDs)

    def _GetFavoriteDroneGroupConfigName(self):
        shipTypeID = None
        if session.shipid:
            shipItem = sm.GetService('godma').GetItem(session.shipid)
            if shipItem:
                shipTypeID = shipItem.typeID
        return 'drones_favoriteGroupID_%s' % shipTypeID

    def GroupXfier(fn):

        def XfyGroup(group):
            ret = group.copy()
            ret['droneIDs'] = fn(group['droneIDs'])
            return ret

        return lambda self, groups: dict([ (name, XfyGroup(group)) for name, group in groups.iteritems() ])

    _SettifyGroups = GroupXfier(set)
    _ListifyGroups = GroupXfier(list)

    def OnGroupsChanged(self):
        self.UpdateGroupSettings()
        self._UpdateGroupsByID()
        self.on_groups_changed()

    def UpdateGroupSettings(self):
        settings.user.ui.Set(settingsName, self._ListifyGroups(self.groups))
        sm.GetService('settings').SaveSettings()

    def GetSubGroup(self, groupName):
        if groupName in self.groups:
            return self.groups[groupName]

    def _GetDroneDictFromDroneIDs(self, itemIDs, droneState, includeFunction = None):
        if includeFunction is None:
            includeFunction = self._IsDroneIDinItemIDs
        droneDict = {}
        if droneState == DRONESTATE_INBAY:
            droneDict = {drone.itemID:(drone, 0, None) for drone in GetDronesInBay() if includeFunction(drone.itemID, itemIDs)}
            return droneDict
        if droneState == DRONESTATE_INSPACE:
            listOfDrones = GetDronesInLocalSpace()
        else:
            return droneDict
        droneDict = {drone.droneID:(drone.droneID,
         drone.typeID,
         drone.ownerID,
         drone.locationID) for drone in listOfDrones if includeFunction(drone.droneID, itemIDs)}
        return droneDict

    def GetDroneDataForMainGroup(self, droneState):
        droneDict = self._GetDroneDictFromDroneIDs(None, droneState, includeFunction=self._IncludeAllDrones)
        return droneDict.values()

    def _GetDroneDictForSubGroup(self, droneState, groupName):
        allDronesBelongingToGroup = self.GetSubGroup(groupName)['droneIDs']
        droneDict = self._GetDroneDictFromDroneIDs(allDronesBelongingToGroup, droneState)
        return droneDict

    def GetDroneIDsInSubGroup(self, droneState, groupName):
        droneDict = self._GetDroneDictForSubGroup(droneState, groupName)
        return droneDict.keys()

    def GetDroneDataForSubGroup(self, droneState, groupName):
        droneDict = self._GetDroneDictForSubGroup(droneState, groupName)
        return droneDict.values()

    def _IsDroneIDinItemIDs(self, droneID, itemIDs):
        return droneID in itemIDs

    def _IncludeAllDrones(self, droneID, itemIDs):
        return True

    def GetDroneGroup(self, droneID, getall = 0):
        retall = []
        for groupName, group in self.groups.iteritems():
            droneIDs = group['droneIDs']
            if droneID in droneIDs:
                if getall:
                    retall.append(group)
                else:
                    return group

        if getall:
            return retall

    def RemoveFromGroup(self, itemIDs):
        for itemID in itemIDs:
            for group in self.GetDroneGroup(itemID, getall=1):
                group['droneIDs'].remove(itemID)

        self.OnGroupsChanged()

    def _EmptyGroup(self, groupName):
        droneGroup = self.GetSubGroup(groupName)
        for droneID in droneGroup.get('droneIDs', set()).copy():
            for group in self.GetDroneGroup(droneID, getall=1):
                group['droneIDs'].remove(droneID)

    def MoveToGroup(self, droneGroupID, groupName, itemIDs):
        group = self.GetSubGroup(groupName)
        if group['droneIDs'] and group['droneGroupID'] != droneGroupID:
            eve.Message('CannotMixDrones')
            return False
        self.RemoveFromGroup(itemIDs)
        group = self.GetSubGroup(groupName)
        if not group['droneIDs']:
            group['droneGroupID'] = droneGroupID
        if group:
            for itemID in itemIDs:
                group['droneIDs'].add(itemID)

        self.OnGroupsChanged()
        return True

    def CreateSubGroup(self, droneGroupID, itemIDs):
        ret = NamePopup(localization.GetByLabel('UI/Generic/TypeGroupName'), localization.GetByLabel('UI/Generic/TypeNameForGroup'))
        if not ret:
            return False
        droneIDs = set()
        for itemID in itemIDs:
            for group in self.GetDroneGroup(itemID, getall=1):
                group['droneIDs'].remove(itemID)

            droneIDs.add(itemID)

        origname = groupname = ret
        i = 2
        while groupname in self.groups:
            groupname = '%s_%i' % (origname, i)
            i += 1

        group = {}
        group['label'] = groupname
        group['droneIDs'] = droneIDs
        group['id'] = (groupname, str(blue.os.GetWallclockTime()))
        group['droneGroupID'] = droneGroupID
        self.groups[groupname] = group
        self.OnGroupsChanged()
        return True

    def DeleteGroup(self, groupName):
        self._EmptyGroup(groupName)
        if groupName in self.groups:
            del self.groups[groupName]
        self.OnGroupsChanged()


_droneGroupsController = None

def GetDroneGroupsController():
    global _droneGroupsController
    if not _droneGroupsController:
        _droneGroupsController = _DroneGroupsController()
    return _droneGroupsController
