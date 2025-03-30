#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\inventory\treeData.py
from carbon.common.lib import telemetry
from carbon.common.script.util.format import FmtDist
from eve.client.script.environment import invControllers as invCtrl
from eve.client.script.ui.control.treeData import TreeData
from eve.client.script.ui.plex.textures import PLEX_32_GRADIENT_YELLOW
from eve.client.script.ui.shared.inventory.invCommon import CONTAINERGROUPS, SortData
import evetypes
from eve.common.script.sys import eveCfg
from eveexceptions import UserError
from inventorycommon.const import INVENTORY_ID_PLEX_VAULT
from inventorycommon.util import IsModularShip
import localization
from eve.client.script.ui.util import uix
from eve.common.lib import appConst as const
from carbonui.uicore import uicore
from eveservices.menu import GetMenuService
from eve.common.script.sys.idCheckers import IsDockableStructure, IsAutoMoonMiner
from locks import SingletonCall
from caching.memoize import Memoize
import eve.client.script.ui.shared.inventory.invConst as invDef
from eve.client.script.ui.shared.inventory.invConst import ContainerType
NO_DISTANCE_SHOWN = ['POSCorpHangar',
 'POSStrontiumBay',
 'POSFuelBay',
 'POSStructureChargesStorage',
 'POSStructureChargeCrystal',
 'StructureCorpHangar',
 INVENTORY_ID_PLEX_VAULT]

class TreeDataInv(TreeData):

    def __init__(self, invType, parent = None, children = None, label = None, isRemovable = False, cmdName = None, iconName = None, **kw):
        TreeData.__init__(self, parent=parent, children=children, label=label, isRemovable=isRemovable, **kw)
        self.invType = invType
        self.cmdName = cmdName
        self.iconName = iconName
        self.uiName = invType
        self.invController = invDef.GetInventoryControllerClass(invType)(**kw)

    @property
    def clsName(self):
        return self.invType

    @telemetry.ZONE_METHOD
    def GetLabel(self):
        if self._label:
            return self._label
        else:
            return self.invController.GetName()

    @telemetry.ZONE_METHOD
    def GetLabelWithDistance(self):
        label = self.GetLabel()
        if self.clsName in NO_DISTANCE_SHOWN or self.invController.itemID == eveCfg.GetActiveShip():
            return label
        if session.solarsystemid:
            ball = sm.GetService('michelle').GetBall(self.invController.itemID)
            if ball:
                dist = FmtDist(ball.surfaceDist, 1)
                return '%s <color=#66FFFFFF>%s</color>' % (label, dist)
        return label

    def GetIcon(self):
        if self.iconName:
            return self.iconName
        return self.invController.GetIconName()

    def GetMenu(self):
        m = self.invController.GetMenu()
        if self.invController.IsInRange():
            m += [(localization.GetByLabel('UI/Inventory/OpenInNewWindow'), self.OpenNewWindow, ())]
        return m

    def GetHint(self):
        if self.cmdName:
            shortcut = uicore.cmd.GetShortcutStringByFuncName(self.cmdName)
            if shortcut:
                return localization.GetByLabel('UI/Inventory/ShortcutBrackets', shortcut=shortcut)

    def GetID(self):
        return self.invController.GetInvID()

    def GetItemID(self):
        return self.invController.itemID

    def GetInvCont(self, **kw):
        kw.update(self._kw)
        return invDef.GetInventoryContainerClass(self.invType)(**kw)

    def HasInvCont(self):
        return True

    def OpenNewWindow(self, openDragging = False):
        from eve.client.script.ui.shared.inventory.invWindow import Inventory
        invID = self.GetID()
        windowID = invID[0]
        if len(invID) == 3:
            windowID = '%s_%s' % (invID[0], invID[2])
            windowInstanceID = '%s_%s' % (invID[1], invID[2])
        else:
            windowInstanceID = invID[1]
        return Inventory.OpenOrShow(invID=invID, usePrimary=False, toggle=True, openDragging=openDragging, windowID=windowID, windowInstanceID=windowInstanceID, **self._kw)

    def IsForceCollapsed(self):
        return not self.invController.IsPrimed()

    def IsDraggable(self):
        return self.invController.IsInRange()

    def CheckCanQuery(self):
        if self.clsName == 'StationContainer':
            return self.GetParent().CheckCanTake()
        return self.invController.CheckCanQuery()

    def CheckCanTake(self):
        return self.invController.CheckCanTake()

    def IsValidDefaultSelection(self):
        return True


class TreeDataPlasticWrap(TreeDataInv):

    def GetChildren(self):
        data = GetContainerDataFromItems(self.invController.GetItems(), parent=self)
        if not data:
            data = [TreeData(parent=self, label=localization.GetByLabel('UI/Inventory/NoNestedContainers'), id='none_%s' % self.invController.itemID)]
        return data

    def HasChildren(self):
        return True


def GetSharedBayHint(invController):
    if invController.itemID != eveCfg.GetActiveShip():
        hint = cfg.evelocations.Get(invController.itemID).name
        ownerID = invController.GetOwnerID()
        if ownerID:
            hint += '<br>%s' % cfg.eveowners.Get(ownerID).name
        return hint


class TreeDataFleetHangar(TreeDataInv):

    def GetChildren(self):
        return GetContainerDataFromItems(self.invController.GetItems(), parent=self)

    def HasChildren(self):
        try:
            for item in self.invController.GetItems():
                if item.groupID in CONTAINERGROUPS:
                    return True

        except UserError as e:
            if e.msg in ('CantViewShipContainer', 'CantViewShipContainerSpace'):
                eve.Message(e.msg, e.dict)
            else:
                raise

        return False

    def GetHint(self):
        return GetSharedBayHint(self.invController)


class TreeDataShipMaintenanceBay(TreeDataInv):

    def GetHint(self):
        return GetSharedBayHint(self.invController)


class TreeDataCelestialParent(TreeDataInv):

    def HasInvCont(self, **kw):
        return False

    def IsForceCollapsed(self):
        return False


class TreeDataInvFolder(TreeData):

    def OpenNewWindow(self, openDragging = False):
        from eve.client.script.ui.shared.inventory.invWindow import Inventory
        return Inventory.OpenOrShow(invID=self.GetID(), usePrimary=False, toggle=True, openDragging=openDragging, iconNum=self.GetIcon(), **self._kw)

    def GetMenu(self):
        return [(localization.GetByLabel('UI/Inventory/OpenInNewWindow'), self.OpenNewWindow, ())]

    def HasChildren(self):
        return True

    @telemetry.ZONE_METHOD
    def GetLabelWithDistance(self):
        return self.GetLabel()

    def IsDraggable(self):
        return True


class TreeDataPOSCorp(TreeDataInvFolder):

    def __init__(self, slimItem, **kw):
        TreeData.__init__(self, **kw)
        self.slimItem = slimItem
        self.invController = invCtrl.POSCorpHangar(self.slimItem.itemID)

    @telemetry.ZONE_METHOD
    def GetLabel(self):
        return uix.GetSlimItemName(self.slimItem)

    @telemetry.ZONE_METHOD
    def GetLabelWithDistance(self):
        label = self.GetLabel()
        bp = sm.GetService('michelle').GetBallpark()
        ball = bp.GetBall(self.invController.itemID)
        if not ball:
            return label
        dist = FmtDist(ball.surfaceDist, 1)
        return '%s <color=#66FFFFFF>%s</color>' % (label, dist)

    def GetIcon(self):
        return 'res:/ui/Texture/WindowIcons/corporation.png'

    def GetItemID(self):
        return self.slimItem.itemID

    def GetID(self):
        return ('POSCorpHangars', self.slimItem.itemID)

    def GetMenu(self):
        m = TreeDataInvFolder.GetMenu(self)
        m += GetMenuService().GetMenuFromItemIDTypeID(self.slimItem.itemID, self.slimItem.typeID)
        return m

    def GetChildren(self):
        data = []
        itemID = self.slimItem.itemID
        for flagID in const.flagCorpSAGs:
            divisionID = const.corpDivisionsByFlag[flagID]
            data.append(TreeDataInv(parent=self, invType=ContainerType.POS_CORP_HANGAR, itemID=itemID, divisionID=divisionID))

        return data

    def IsDraggable(self):
        return self.invController.IsInRange()


class TreeDataShip(TreeDataInv):

    def __init__(self, invType, typeID, **kw):
        TreeDataInv.__init__(self, invType, **kw)
        self.uiName = 'ShipHangar'
        self.typeID = typeID

    @telemetry.ZONE_METHOD
    def GetLabel(self):
        shipName = TreeDataInv.GetLabel(self)
        return localization.GetByLabel('UI/Inventory/ShipNameAndType', shipName=shipName, typeName=evetypes.GetName(self.typeID))

    def GetHint(self):
        hint = TreeDataInv.GetHint(self)
        typeName = evetypes.GetName(self.typeID)
        if hint:
            return typeName + hint
        else:
            return typeName

    def HasChildren(self):
        return True

    def IsForceCollapsed(self):
        if self.invController.itemID == eveCfg.GetActiveShip():
            return False
        return TreeDataInv.IsForceCollapsed(self)

    def GetIcon(self):
        return self.invController.GetIconName(highliteIfActive=True)

    def GetChildren(self):
        shipData = []
        itemID = self.invController.itemID
        typeID = self.typeID
        if itemID == eveCfg.GetActiveShip():
            cmdName = 'OpenDroneBayOfActiveShip'
        else:
            cmdName = None
        godmaType = sm.GetService('godma').GetType(typeID)
        if godmaType.droneCapacity or IsModularShip(typeID):
            shipData.append(TreeDataInv(parent=self, invType=ContainerType.SHIP_DRONE_BAY, itemID=itemID, cmdName=cmdName))
        if godmaType.fighterCapacity:
            shipData.append(TreeDataInv(parent=self, invType=ContainerType.SHIP_FIGHTER_BAY, itemID=itemID, cmdName=cmdName))
        godmaSM = sm.GetService('godma').GetStateManager()
        if bool(godmaSM.GetType(typeID).hasShipMaintenanceBay):
            shipData.append(TreeDataShipMaintenanceBay(parent=self, invType=ContainerType.SHIP_MAINTENANCE_BAY, itemID=itemID))
        if bool(godmaSM.GetType(typeID).frigateEscapeBayCapacity):
            shipData.append(TreeDataInv(parent=self, invType=ContainerType.SHIP_FRIGATE_ESCAPE_BAY, itemID=itemID))
        if bool(godmaSM.GetType(typeID).hasFleetHangars):
            shipData.append(TreeDataFleetHangar(parent=self, invType=ContainerType.SHIP_FLEET_HANGAR, itemID=itemID))
        if bool(godmaSM.GetType(typeID).specialFuelBayCapacity):
            shipData.append(TreeDataInv(parent=self, invType=ContainerType.SHIP_FUEL_BAY, itemID=itemID))
        if bool(godmaSM.GetType(typeID).generalMiningHoldCapacity):
            shipData.append(TreeDataInv(parent=self, invType=ContainerType.SHIP_GENERAL_MINING_HOLD, itemID=itemID))
        if bool(godmaSM.GetType(typeID).specialAsteroidHoldCapacity):
            shipData.append(TreeDataInv(parent=self, invType=ContainerType.SHIP_ASTEROID_HOLD, itemID=itemID))
        if bool(godmaSM.GetType(typeID).specialIceHoldCapacity):
            shipData.append(TreeDataInv(parent=self, invType=ContainerType.SHIP_ICE_HOLD, itemID=itemID))
        if bool(godmaSM.GetType(typeID).specialGasHoldCapacity):
            shipData.append(TreeDataInv(parent=self, invType=ContainerType.SHIP_GAS_HOLD, itemID=itemID))
        if bool(godmaSM.GetType(typeID).specialMineralHoldCapacity):
            shipData.append(TreeDataInv(parent=self, invType=ContainerType.SHIP_MINERAL_HOLD, itemID=itemID))
        if bool(godmaSM.GetType(typeID).specialSalvageHoldCapacity):
            shipData.append(TreeDataInv(parent=self, invType=ContainerType.SHIP_SALVAGE_HOLD, itemID=itemID))
        if bool(godmaSM.GetType(typeID).specialShipHoldCapacity):
            shipData.append(TreeDataInv(parent=self, invType=ContainerType.SHIP_SHIP_HOLD, itemID=itemID))
        if bool(godmaSM.GetType(typeID).specialSmallShipHoldCapacity):
            shipData.append(TreeDataInv(parent=self, invType=ContainerType.SHIP_SMALL_SHIP_HOLD, itemID=itemID))
        if bool(godmaSM.GetType(typeID).specialMediumShipHoldCapacity):
            shipData.append(TreeDataInv(parent=self, invType=ContainerType.SHIP_MEDIUM_SHIP_HOLD, itemID=itemID))
        if bool(godmaSM.GetType(typeID).specialLargeShipHoldCapacity):
            shipData.append(TreeDataInv(parent=self, invType=ContainerType.SHIP_LARGE_SHIP_HOLD, itemID=itemID))
        if bool(godmaSM.GetType(typeID).specialIndustrialShipHoldCapacity):
            shipData.append(TreeDataInv(parent=self, invType=ContainerType.SHIP_INDUSTRIAL_SHIP_HOLD, itemID=itemID))
        if bool(godmaSM.GetType(typeID).specialAmmoHoldCapacity):
            shipData.append(TreeDataInv(parent=self, invType=ContainerType.SHIP_AMMO_HOLD, itemID=itemID))
        if bool(godmaSM.GetType(typeID).specialCommandCenterHoldCapacity):
            shipData.append(TreeDataInv(parent=self, invType=ContainerType.SHIP_COMMAND_CENTER_HOLD, itemID=itemID))
        if bool(godmaSM.GetType(typeID).specialPlanetaryCommoditiesHoldCapacity):
            shipData.append(TreeDataInv(parent=self, invType=ContainerType.SHIP_PLANETARY_COMMODITIES_HOLD, itemID=itemID))
        if bool(godmaSM.GetType(typeID).specialQuafeHoldCapacity):
            shipData.append(TreeDataInv(parent=self, invType=ContainerType.SHIP_QUAFE_HOLD, itemID=itemID))
        if bool(godmaSM.GetType(typeID).specialCorpseHoldCapacity):
            shipData.append(TreeDataInv(parent=self, invType=ContainerType.SHIP_CORPSE_HOLD, itemID=itemID))
        if bool(godmaSM.GetType(typeID).specialBoosterHoldCapacity):
            shipData.append(TreeDataInv(parent=self, invType=ContainerType.SHIP_BOOSTER_HOLD, itemID=itemID))
        if bool(godmaSM.GetType(typeID).specialSubsystemHoldCapacity):
            shipData.append(TreeDataInv(parent=self, invType=ContainerType.SHIP_SUBSYSTEM_HOLD, itemID=itemID))
        if bool(godmaSM.GetType(typeID).specialMobileDepotHoldCapacity):
            shipData.append(TreeDataInv(parent=self, invType=ContainerType.SHIP_MOBILE_DEPOT_HOLD, itemID=itemID))
        if bool(godmaSM.GetType(typeID).specialColonyResourcesHoldCapacity):
            shipData.append(TreeDataInv(parent=self, invType=ContainerType.SHIP_COLONY_RESOURCES_HOLD, itemID=itemID))
        invController = invCtrl.ShipCargo(itemID=itemID)
        shipData += GetContainerDataFromItems(invController.GetItems(), parent=self)
        if not shipData:
            shipData.append(TreeData(parent=self, label=localization.GetByLabel('UI/Inventory/NoAdditionalBays'), id='none_%s' % itemID))
        return shipData


class TreeDataStructure(TreeDataInvFolder):

    def __init__(self, *args, **kwargs):
        invType = kwargs.pop('invType')
        self.invController = invDef.GetInventoryControllerClass(invType)(**kwargs)
        self.itemID = kwargs.pop('itemID')
        self.typeID = kwargs.pop('typeID')
        TreeDataInvFolder.__init__(self, *args, **kwargs)

    def HasInvCont(self):
        return False

    def HasChildren(self):
        return True

    def GetLabel(self):
        return self.invController.GetName()

    @Memoize(1 / 60.0)
    @SingletonCall
    def GetChildren(self):
        children = []
        isDockableStructure = IsDockableStructure(self.typeID)
        if isDockableStructure:
            children.append(TreeDataInv(parent=self, invType=ContainerType.STRUCTURE_AMMO_BAY, itemID=self.invController.itemID))
            godmaType = sm.GetService('godma').GetType(self.typeID)
            if godmaType.fighterCapacity:
                children.append(TreeDataInv(parent=self, invType=ContainerType.STRUCTURE_FIGHTER_BAY, itemID=self.invController.itemID))
        children.append(TreeDataInv(parent=self, invType=ContainerType.STRUCTURE_FUEL_BAY, itemID=self.invController.itemID))
        if isDockableStructure:
            children.append(TreeDataInv(parent=self, invType=ContainerType.STRUCTURE_DEED_BAY, itemID=self.invController.itemID))
        if IsAutoMoonMiner(self.typeID):
            children.append(TreeDataInv(parent=self, invType=ContainerType.STRUCTURE_MOON_MATERIAL_BAY, itemID=self.invController.itemID))
        if isDockableStructure:
            children += GetContainerDataFromItems(self.invController.GetItems(), parent=self)
        return children

    def GetIcon(self):
        return self.invController.GetIconName()

    def GetID(self):
        return ('Structure', self.itemID)


class TreeDataStationCorp(TreeDataInvFolder):

    def __init__(self, forceCollapsed = True, forceCollapsedMembers = True, *args):
        self.itemID = sm.GetService('officeManager').GetCorpOfficeAtLocation().officeID
        self.forceCollapsedMembers = forceCollapsedMembers
        self.forceCollapsed = forceCollapsed
        TreeDataInvFolder.__init__(self, *args)

    def GetChildren(self):
        if self._children:
            return self._children
        corpData = []
        for flagID in sorted(const.corpDivisionsByFlag.keys()):
            divID = const.corpDivisionsByFlag[flagID]
            invController = invCtrl.StationCorpHangar(self.itemID, divID)
            divData = []
            for item in invController.GetItems():
                if item.groupID in CONTAINERGROUPS and item.singleton:
                    divData.append(TreeDataInv(invType=ContainerType.STATION_CONTAINER, itemID=item.itemID, typeID=item.typeID))

            cfg.evelocations.Prime([ d.invController.itemID for d in divData ])
            SortData(divData)
            corpData.append(TreeDataInv(parent=self, invType=ContainerType.STATION_CORP_HANGAR, itemID=self.itemID, divisionID=divID, children=divData))

        securityOfficerRoles = session.corprole & const.corpRoleSecurityOfficer == const.corpRoleSecurityOfficer
        if securityOfficerRoles:
            memberData = sm.GetService('corpui').GetMemberHangarsData().keys()
            cfg.eveowners.Prime([ member[1] for member in memberData ])
            corpData.append(TreeDataCorpMembers(parent=self, memberData=memberData, groupChildren=True, forceCollapsed=self.forceCollapsedMembers))
        self._children = corpData
        return corpData

    def HasChildren(self):
        return True

    def IsForceCollapsed(self):
        if self._children or not self.forceCollapsed:
            return False
        invController = invCtrl.StationCorpHangar(self.itemID, 0)
        return not invController.IsPrimed()

    def GetIcon(self):
        return 'res:/ui/Texture/WindowIcons/corpHangar.png'

    @telemetry.ZONE_METHOD
    def GetLabel(self):
        return localization.GetByLabel('UI/Inventory/CorporationHangars')

    def GetID(self):
        return ('StationCorpHangars', self.itemID)


class TreeDataShipHangar(TreeDataInv):

    def HasChildren(self):
        return True

    def GetChildren(self):
        children = []
        activeShipID = eveCfg.GetActiveShip()
        singletonShips = [ ship for ship in self.invController.GetItems() if ship.singleton == 1 and ship.itemID != activeShipID ]
        cfg.evelocations.Prime([ ship.itemID for ship in singletonShips ])
        for ship in singletonShips:
            children.append(TreeDataShip(parent=self, invType=ContainerType.SHIP_CARGO, itemID=ship.itemID, typeID=ship.typeID))

        SortData(children)
        return children

    def GetLabelWithDistance(self):
        return self.GetLabel()


class TreeDataItemHangar(TreeDataInv):

    def __init__(self, invType, **kw):
        super(TreeDataItemHangar, self).__init__(invType, **kw)
        self.uiName = 'ItemHangar'

    def HasChildren(self):
        for item in self.invController.GetItems():
            if item.groupID in CONTAINERGROUPS:
                return True

        return False

    def GetChildren(self):
        return GetContainerDataFromItems(self.invController.GetItems(), parent=self)

    def GetLabelWithDistance(self):
        return self.GetLabel()


class TreeDataStructureCorp(TreeDataInvFolder):

    def __init__(self, *args, **kwargs):
        self.itemID = kwargs.pop('itemID')
        TreeDataInvFolder.__init__(self, *args, **kwargs)

    def GetChildren(self):
        if not self._children:
            children = []
            for flagID in const.flagCorpSAGs:
                divisionID = const.corpDivisionsByFlag[flagID]
                controller = invCtrl.StructureCorpHangar(self.itemID, divisionID)
                data = GetContainerDataFromItems(controller.GetItems(), parent=self)
                children.append(TreeDataInv(parent=self, invType=ContainerType.STRUCTURE_CORP_HANGAR, itemID=self.itemID, divisionID=divisionID, children=data))

            self._children = children
        return self._children

    def HasChildren(self):
        return True

    def IsForceCollapsed(self):
        return False

    def GetIcon(self):
        return 'res:/ui/Texture/WindowIcons/corpHangar.png'

    def GetLabel(self):
        return localization.GetByLabel('UI/Inventory/CorporationHangars')

    def GetID(self):
        return ('StructureCorpHangars', self.itemID)


class TreeDataCorpAssetSafety(TreeDataStructureCorp):

    def __init__(self, *args, **kwargs):
        self.name = kwargs.pop('name')
        TreeDataStructureCorp.__init__(self, *args, **kwargs)

    def GetChildren(self):
        if not self._children:
            children = []
            controller = invCtrl.AssetSafetyCorpContainer(self.itemID, None)
            items = controller.GetItems()
            divisions = {const.corpAssetSafetyFlags[item.flagID] for item in items}
            for division in sorted(list(divisions)):
                filteredItems = [ item for item in items if const.corpAssetSafetyFlags[item.flagID] == division ]
                data = GetContainerDataFromItems(filteredItems, parent=self)
                children.append(TreeDataInv(parent=self, invType=ContainerType.ASSET_SAFETY_CORP_CONTAINER, itemID=self.itemID, divisionID=division, children=data))

            self._children = children
        return self._children

    def HasInvCont(self):
        return True

    def IsForceCollapsed(self):
        return False

    def GetLabel(self):
        return self.name


class TreeDataAssetSafety(TreeDataInv):

    def __init__(self, *args, **kw):
        kw.setdefault('invType', ContainerType.ASSET_SAFETY_DELIVERIES)
        TreeDataInv.__init__(self, *args, **kw)

    def GetLabel(self):
        return localization.GetByLabel('UI/Inventory/AssetSafety/AssetSafetyDeliveries')

    def HasChildren(self):
        return True

    def HasInvCont(self):
        return True

    def IsForceCollapsed(self):
        return False

    def GetChildren(self):
        items = self.invController.GetItems()
        if not items:
            self._children = []
            return []
        if self._children:
            return self._children
        data = []
        names = sm.GetService('assetSafety').GetWrapNames([ item.itemID for item in items ])
        for item in items:
            itemID = item.itemID
            if item.typeID != const.typeAssetSafetyWrap:
                raise RuntimeError('There is something in the asset safety that is not a assetSafetyWrap', itemID, item.typeID)
            if item.ownerID == session.corpid:
                data.append(TreeDataCorpAssetSafety(parent=self, itemID=itemID, name=names[itemID]))
            else:
                data.append(TreeDataInv(parent=self, invType=ContainerType.ASSET_SAFETY_CONTAINER, itemID=itemID, typeID=item.typeID, name=names[itemID]))

        cfg.evelocations.Prime([ item.itemID for item in items ])
        SortData(data)
        self._children = data
        return data

    def GetLabelWithDistance(self):
        return self.GetLabel()


class TreeDataCorpMembers(TreeDataInvFolder):

    def __init__(self, memberData, groupChildren = False, label = None, forceCollapsed = True, *args, **kw):
        if label is None:
            label = localization.GetByLabel('UI/Inventory/MemberHangars')
        self.memberData = memberData
        self.groupChildren = groupChildren
        self.memberData.sort(key=lambda x: cfg.eveowners.Get(x[0]).name.lower())
        self.forceCollapsed = forceCollapsed
        TreeData.__init__(self, label=label, *args, **kw)

    def GetID(self):
        return ('StationCorpMembers', self.GetLabel())

    def GetChildren(self):
        if self._children:
            return self._children
        data = []
        maxNumPerLevel = 50
        numMembers = len(self.memberData)
        if not self.groupChildren or numMembers <= maxNumPerLevel:
            for itemID, ownerID in self.memberData:
                if itemID == session.charid:
                    continue
                if itemID == ownerID:
                    data.append(TreeDataInv(parent=self, invType=ContainerType.STATION_CORP_MEMBER, itemID=itemID, ownerID=ownerID))

        else:
            currLetter = None
            levelData = []
            for itemID, ownerID in self.memberData:
                letter = cfg.eveowners.Get(ownerID).name[0].upper()
                if letter != currLetter:
                    if levelData:
                        data.append(TreeDataCorpMembers(label=currLetter, memberData=levelData))
                    currLetter = letter
                    levelData = []
                levelData.append((itemID, ownerID))

            if levelData:
                data.append(TreeDataCorpMembers(label=currLetter, memberData=levelData))
        if not data:
            data.append(TreeData(label=localization.GetByLabel('UI/Inventory/NoCorpHangars')))
        self.forceCollapsed = False
        self._children = data
        return data

    def IsForceCollapsed(self):
        return self.forceCollapsed

    def GetIcon(self):
        return 'res:/ui/Texture/WindowIcons/corporationmembers.png'


class TreeDataPlexVault(TreeDataInv):

    def __init__(self, **kwargs):
        kwargs['invType'] = ContainerType.PLEX_VAULT
        super(TreeDataPlexVault, self).__init__(**kwargs)

    def GetLabel(self):
        return localization.GetByLabel('UI/PlexVault/PlexVault')

    def GetIcon(self):
        return PLEX_32_GRADIENT_YELLOW

    def IsValidDefaultSelection(self):
        return False


def GetContainerDataFromItems(items, parent = None):
    data = []
    for item in items:
        if item.typeID == const.typePlasticWrap and item.singleton:
            data.append(TreeDataPlasticWrap(parent=parent, invType=ContainerType.STATION_CONTAINER, itemID=item.itemID, typeID=item.typeID))
        elif item.groupID in CONTAINERGROUPS and item.singleton:
            data.append(TreeDataInv(parent=parent, invType=ContainerType.STATION_CONTAINER, itemID=item.itemID, typeID=item.typeID))
        elif item.typeID == const.typeAssetSafetyWrap:
            data.append(TreeDataInv(parent=parent, invType=ContainerType.ASSET_SAFETY_CONTAINER, itemID=item.itemID, typeID=item.typeID))

    cfg.evelocations.Prime([ d.invController.itemID for d in data ])
    SortData(data)
    return data


def GetTreeDataClassByInvName(invName):
    if invName == 'ShipFleetHangar':
        return TreeDataFleetHangar
    elif invName == 'ShipMaintenanceBay':
        return TreeDataShipMaintenanceBay
    else:
        return TreeDataInv
