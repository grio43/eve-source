#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\inventorysvc.py
import logging
import sys
import weakref
import blue
import inventorycommon.const as invConst
import localization
import telemetry
from carbon.common.script.sys.service import Service
from eve.client.script.environment.invControllers import ShipCargo, Structure
from eve.client.script.ui.control.treeData import TreeData
from eve.client.script.ui.shared.inventory.invCommon import SortData
from eve.client.script.ui.shared.inventory.invConst import ContainerType
from eve.client.script.ui.shared.inventory.invWindow import Inventory
from eve.client.script.ui.shared.inventory.treeData import TreeDataShip, TreeDataInv, TreeDataStationCorp, TreeDataStructureCorp, TreeDataCelestialParent, TreeDataPOSCorp, TreeDataInvFolder, GetTreeDataClassByInvName, TreeDataShipHangar, TreeDataItemHangar, TreeDataAssetSafety, TreeDataStructure, TreeDataPlexVault
from eve.common.script.sys import eveCfg
from hackingcommon import hackingConstants
from spacecomponents.common.componentConst import CARGO_BAY
from spacecomponents.common.data import get_space_component_for_type
from spacecomponents.common.helper import HasCargoBayComponent, HasAutoMoonMinerComponent
from eve.common.script.sys.idCheckers import IsDockableStructure
from eve.common.lib import appConst as const
log = logging.getLogger(__name__)

class InventorySvc(Service):
    __guid__ = 'svc.inv'
    __exportedcalls__ = {'Register': [],
     'Unregister': []}
    __notifyevents__ = ['OnSlimItemChange']

    def Run(self, *etc):
        Service.Run(self, *etc)
        self.regs = {}
        self.itemClipboard = []
        self.itemClipboardCopy = False
        self.tempInvLocations = set()
        self.treeUpdatingEnabled = True

    def _ShouldCloseContainer(self, item, change):
        if not item.singleton:
            return False
        if item.groupID not in (const.groupWreck,
         const.groupCargoContainer,
         const.groupSecureCargoContainer,
         const.groupAuditLogSecureContainer,
         const.groupFreightContainer):
            return False
        if const.ixLocationID in change or const.ixOwnerID in change or const.ixFlag in change:
            return True
        return False

    @telemetry.ZONE_METHOD
    def OnItemChange(self, item, change, location):
        self.LogInfo('OnItemChange', change, item)
        self.ClearItemClipboard()
        fancyChange = {}
        for k, v in change.iteritems():
            fancyChange[item.__columns__[k]] = (v, '->', item[k])

        self.LogInfo('OnItemChange (fancy)', fancyChange, item)
        old = blue.DBRow(item)
        for k, v in change.iteritems():
            if k == const.ixSingleton and v == 0:
                v = 1
            if k in (const.ixStackSize, const.ixSingleton):
                k = const.ixQuantity
            old[k] = v

        containerName = ''
        containerCookie = None
        closeContainer = self._ShouldCloseContainer(item, change)
        if closeContainer:
            containerName = 'loot_%s' % item.itemID
        for cookie, wr in self.regs.items():
            ob = wr()
            if not ob or ob.destroyed:
                self.Unregister(cookie)
                continue
            if closeContainer == 1:
                if getattr(ob, 'id', 0) == item.itemID:
                    containerCookie = cookie
                    continue
                if getattr(ob, 'name', '') == containerName:
                    containerCookie = cookie
                    continue
            if hasattr(ob, 'invController'):
                if ob.invController is None:
                    continue
                wasHere = old.stacksize != 0 and ob.invController.IsItemHere(old)
                isHere = item.stacksize != 0 and ob.invController.IsItemHere(item)
            else:
                wasHere = old.stacksize != 0 and ob.IsItemHere(old)
                isHere = item.stacksize != 0 and ob.IsItemHere(item)
            try:
                if getattr(ob, 'OnInvChangeAny', None):
                    ob.OnInvChangeAny(item, change)
                if not wasHere and not isHere:
                    continue
                if wasHere and isHere and getattr(ob, 'UpdateItem', None):
                    ob.UpdateItem(item, change)
                elif wasHere and not isHere and getattr(ob, 'RemoveItem', None):
                    ob.RemoveItem(item)
                elif not wasHere and isHere and getattr(ob, 'AddItem', None):
                    ob.AddItem(item)
                if getattr(ob, 'OnInvChange', None):
                    ob.OnInvChange(item, change)
            except:
                self.Unregister(cookie)
                log.exception('svc.inv')
                sys.exc_clear()

        if closeContainer == 1:
            if containerCookie is not None:
                self.Unregister(containerCookie)
        if const.ixFlag in change:
            if change[const.ixFlag] in invConst.fittingFlags and item.flagID not in invConst.fittingFlags:
                sm.ScatterEvent('OnModuleUnfitted', item.typeID)
            if {item.flagID, change[const.ixFlag]}.intersection(set(invConst.hiSlotFlags)):
                sm.ScatterEvent('OnHighSlotFittingChanged')

    def OnSlimItemChange(self, oldSlim, newSlim):
        if oldSlim.hackingSecurityState is not None:
            if oldSlim.hackingSecurityState != newSlim.hackingSecurityState:
                sm.GetService('invCache').InvalidateLocationCache(oldSlim.itemID)
                if newSlim.hackingSecurityState != hackingConstants.hackingStateHacked:
                    invID = ('ItemFloatingCargo', oldSlim.itemID)
                    sm.GetService('inv').RemoveTemporaryInvLocation(invID)

    def Register(self, callbackObj):
        objectID = id(callbackObj)
        if objectID in self.regs:
            return
        self.LogInfo('Registering', objectID, callbackObj)
        self.regs[objectID] = weakref.ref(callbackObj)
        return objectID

    def Unregister(self, cookie):
        if cookie in self.regs:
            del self.regs[cookie]
            self.LogInfo('Unregistered', cookie)
        else:
            log.warning('inv.Unregister: Unknown cookie %s', cookie)

    def SetItemClipboard(self, nodes, copy = False):
        newNodes = []
        for node in nodes:
            if not self.IsOnClipboard(node.item.itemID):
                newNodes.append(node)

        self.itemClipboard = newNodes
        self.itemClipboardCopy = copy
        sm.ScatterEvent('OnInvClipboardChanged')

    @telemetry.ZONE_METHOD
    def PopItemClipboard(self):
        ret = self.itemClipboard
        if not self.itemClipboardCopy:
            self.itemClipboard = []
        sm.ScatterEvent('OnInvClipboardChanged')
        return (ret, self.itemClipboardCopy)

    @telemetry.ZONE_METHOD
    def ClearItemClipboard(self):
        if self.itemClipboard:
            self.itemClipboard = []
            sm.ScatterEvent('OnInvClipboardChanged')

    def IsOnClipboard(self, itemID):
        if self.itemClipboardCopy:
            return
        itemIDs = [ node.item.itemID for node in self.itemClipboard ]
        return itemID in itemIDs

    def GetTemporaryInvLocations(self):
        bp = sm.GetService('michelle').GetBallpark()
        if bp is None or not session.solarsystemid or session.structureid:
            self.tempInvLocations = set()
        else:
            toRemove = []
            for invName, itemID in self.tempInvLocations:
                if itemID not in bp.slimItems:
                    toRemove.append((invName, itemID))

            for invID in toRemove:
                self.tempInvLocations.remove(invID)

        return self.tempInvLocations

    def AddTemporaryInvLocation(self, invID):
        if invID not in self.tempInvLocations:
            self.tempInvLocations.add(invID)
            sm.ChainEvent('ProcessTempInvLocationAdded', invID)

    def RemoveTemporaryInvLocation(self, invID, byUser = False):
        if invID in self.tempInvLocations:
            self.tempInvLocations.remove(invID)
            sm.ChainEvent('ProcessTempInvLocationRemoved', invID, byUser)

    def OnBreadcrumbTextClicked(self, linkNum, windowID, windowInstanceID = None):
        wnd = Inventory.GetIfOpen(windowID=windowID, windowInstanceID=windowInstanceID)
        if wnd:
            wnd.OnBreadcrumbLinkClicked(linkNum)

    @telemetry.ZONE_METHOD
    def GetInvLocationTreeData(self, rootInvID = None):
        data = []
        if session.shipid:
            if session.shipid == session.structureid:
                data.append(TreeDataStructure(invType=ContainerType.STRUCTURE, itemID=session.structureid, typeID=Structure(session.shipid).GetTypeID()))
            else:
                data.append(TreeDataShip(invType=ContainerType.SHIP_CARGO, itemID=session.shipid, typeID=ShipCargo(session.shipid).GetTypeID(), cmdName='OpenCargoHoldOfActiveShip'))
        if session.stationid:
            data.append(TreeDataShipHangar(invType=ContainerType.STATION_SHIPS, itemID=session.stationid, cmdName='OpenShipHangar'))
            data.append(TreeDataItemHangar(invType=ContainerType.STATION_ITEMS, itemID=session.stationid, cmdName='OpenHangarFloor'))
            if self._HangarHasAssetSafetyWrap():
                data.append(TreeDataAssetSafety(invType=ContainerType.ASSET_SAFETY_DELIVERIES, itemID=session.stationid))
            if sm.GetService('officeManager').GetCorpOfficeAtLocation() is not None:
                forceCollapsedMembers = not (rootInvID and rootInvID[0] in ('StationCorpMember', 'StationCorpMembers'))
                forceCollapsed = not (rootInvID and rootInvID[0] in ('StationCorpHangar', 'StationCorpHangars'))
                data.append(TreeDataStationCorp(forceCollapsed=forceCollapsed, forceCollapsedMembers=forceCollapsedMembers))
            if HasCorpDeliveryRoles():
                data.append(TreeDataInv(invType=ContainerType.STATION_CORP_DELIVERIES, itemID=session.stationid, cmdName='OpenCorpDeliveries'))
        elif session.structureid and IsDockableStructure(Structure(session.structureid).GetTypeID()):
            data.append(TreeDataShipHangar(invType=ContainerType.STRUCTURE_SHIP_HANGAR, itemID=session.structureid, cmdName='OpenShipHangar'))
            data.append(TreeDataItemHangar(invType=ContainerType.STRUCTURE_ITEM_HANGAR, itemID=session.structureid, cmdName='OpenHangarFloor'))
            data.append(TreeDataItemHangar(invType=ContainerType.STRUCTURE_DELIVERIES_HANGAR, itemID=session.structureid))
            if self._HangarHasAssetSafetyWrap():
                data.append(TreeDataAssetSafety(invType=ContainerType.ASSET_SAFETY_DELIVERIES, itemID=session.structureid))
            corpOffice = sm.GetService('officeManager').GetCorpOfficeAtLocation()
            if corpOffice:
                data.append(TreeDataStructureCorp(itemID=corpOffice.officeID))
            if HasCorpDeliveryRoles():
                data.append(TreeDataInv(invType=ContainerType.STATION_CORP_DELIVERIES, itemID=session.structureid, cmdName='OpenCorpDeliveries'))
        elif session.solarsystemid:
            starbaseData = []
            defensesData = []
            industryData = []
            hangarData = []
            infrastrcutureData = []
            bp = sm.GetService('michelle').GetBallpark()
            if bp:
                for slimItem in bp.slimItems.values():
                    itemID = slimItem.itemID
                    groupID = slimItem.groupID
                    categoryID = slimItem.categoryID
                    if HasCargoBayComponent(slimItem.typeID):
                        if slimItem.ownerID == session.charid or get_space_component_for_type(slimItem.typeID, CARGO_BAY).allowFreeForAll:
                            data.append(TreeDataInv(invType=ContainerType.SPACE_COMPONENT_INVENTORY, itemID=itemID))
                    if HasAutoMoonMinerComponent(slimItem.typeID) and not session.structureid:
                        data.append(TreeDataInv(invType=ContainerType.STRUCTURE_MOON_MATERIAL_BAY, itemID=itemID, isRemovable=True))
                    haveAccess = bool(slimItem) and (slimItem.ownerID == session.charid or slimItem.ownerID == session.corpid or session.allianceid and slimItem.allianceID == session.allianceid)
                    isAnchored = not bp.balls[itemID].isFree
                    if not haveAccess or not isAnchored:
                        continue
                    if groupID == const.groupControlTower:
                        towerData = [TreeDataInv(invType=ContainerType.POS_STRONTIUM_BAY, itemID=itemID), TreeDataInv(invType=ContainerType.POS_FUEL_BAY, itemID=itemID)]
                        starbaseData.append(TreeDataCelestialParent(invType=ContainerType.BASE_CELESTIAL_CONTAINER, itemID=itemID, children=towerData, iconName='res:/UI/Texture/windowIcons/corporation.png'))
                    elif groupID == const.groupCorporateHangarArray:
                        hangarData.append(TreeDataPOSCorp(slimItem=slimItem))
                    elif groupID == const.groupAssemblyArray:
                        industryData.append(TreeDataPOSCorp(slimItem=slimItem))
                    elif groupID == const.groupMobileLaboratory:
                        industryData.append(TreeDataPOSCorp(slimItem=slimItem))
                    elif groupID in (const.groupMobileMissileSentry, const.groupMobileProjectileSentry, const.groupMobileHybridSentry):
                        defensesData.append(TreeDataInv(invType=ContainerType.POS_STRUCTURE_CHARGES, itemID=itemID))
                    elif groupID == const.groupMobileLaserSentry:
                        sentryData = [TreeDataInv(invType=ContainerType.POS_STRUCTURE_CHARGE_CRYSTAL, itemID=itemID), TreeDataInv(invType=ContainerType.POS_STRUCTURE_CHARGES_STORAGE, itemID=itemID)]
                        defensesData.append(TreeDataCelestialParent(invType=ContainerType.BASE_CELESTIAL_CONTAINER, itemID=itemID, children=sentryData, iconName='ui_13_64_9'))
                    elif groupID == const.groupShipMaintenanceArray:
                        hangarData.append(TreeDataInv(invType=ContainerType.POS_SHIP_MAINTENANCE_ARRAY, itemID=itemID))
                    elif groupID == const.groupSilo:
                        industryData.append(TreeDataInv(invType=ContainerType.POS_SILO, itemID=itemID))
                    elif groupID == const.groupMobileReactor:
                        industryData.append(TreeDataInv(invType=ContainerType.POS_MOBILE_REACTOR, itemID=itemID))
                    elif groupID == const.groupReprocessingArray:
                        industryData.append(TreeDataInv(invType=ContainerType.POS_REFINERY, itemID=itemID))
                    elif groupID == const.groupCompressionArray:
                        industryData.append(TreeDataInv(invType=ContainerType.POS_COMPRESSION, itemID=itemID))
                    elif groupID == const.groupPersonalHangar:
                        hangarData.append(TreeDataInv(invType=ContainerType.POS_PERSONAL_HANGAR, itemID=itemID))

            if industryData:
                SortData(industryData)
                starbaseData.append(TreeDataInvFolder(label=localization.GetByLabel('UI/Inventory/POSGroupIndustry'), children=industryData, icon='res:/UI/Texture/WindowIcons/industry.png'))
            if hangarData:
                SortData(hangarData)
                starbaseData.append(TreeDataInvFolder(label=localization.GetByLabel('UI/Inventory/POSGroupStorage'), children=hangarData, icon='res:/ui/Texture/WindowIcons/cargo.png'))
            if infrastrcutureData:
                SortData(infrastrcutureData)
                starbaseData.append(TreeDataInvFolder(label=localization.GetByLabel('UI/Inventory/POSGroupInfrastructure'), children=infrastrcutureData, icon='res:/ui/Texture/WindowIcons/sovereignty.png'))
            if defensesData:
                SortData(defensesData)
                starbaseData.append(TreeDataInvFolder(label=localization.GetByLabel('UI/Inventory/POSGroupDefenses'), children=defensesData, icon='ui_5_64_13'))
            if starbaseData:
                data.append(TreeDataInvFolder(label=localization.GetByLabel('UI/Inventory/StarbaseStructures'), children=starbaseData, icon='res:/ui/Texture/WindowIcons/station.png'))
        data.append(TreeDataPlexVault())
        return TreeData(children=data)

    def _HangarHasAssetSafetyWrap(self):
        inv = sm.GetService('invCache').GetInventory(const.containerHangar)
        if len(inv.List(flag=const.flagAssetSafety)) > 0:
            return True
        return False

    def GetInvLocationTreeDataTemp(self, rootInvID = None):
        data = []
        tmpLocations = sm.GetService('inv').GetTemporaryInvLocations().copy()
        for invName, itemID in tmpLocations:
            if rootInvID in tmpLocations and rootInvID != (invName, itemID):
                continue
            if itemID == eveCfg.GetActiveShip():
                sm.GetService('inv').RemoveTemporaryInvLocation((invName, itemID))
                continue
            else:
                cls = GetTreeDataClassByInvName(invName)
                data.append(cls(invName, itemID=itemID, isRemovable=True))

        return TreeData(children=data)

    def ChangeTreeUpdatingState(self, isUpdateEnabled):
        changed = self.treeUpdatingEnabled != isUpdateEnabled
        self.treeUpdatingEnabled = isUpdateEnabled
        if changed:
            sm.ScatterEvent('OnInvTreeUpdatingChanged', isUpdateEnabled)

    def IsTreeUpdatingEnabled(self):
        return self.treeUpdatingEnabled


def HasCorpDeliveryRoles():
    deliveryRoles = const.corpRoleAccountant | const.corpRoleJuniorAccountant | const.corpRoleTrader
    hasCorpDeliveryRoles = session.corprole & deliveryRoles > 0
    return hasCorpDeliveryRoles
