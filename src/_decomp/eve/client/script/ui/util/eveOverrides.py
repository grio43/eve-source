#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\util\eveOverrides.py
import carbonui.const as uiconst
import evetypes
import inventorycommon.const as invConst
from carbonui.control.dragdrop.dragdata.basedragdata import BaseDragData
from eve.client.script.ui.control.allUserEntries import AllUserEntries
from eve.client.script.ui.control.eveIcon import DraggableIcon
from eve.client.script.ui.inflight.bracketsAndTargets.targetInBar import TargetInBar
from eve.client.script.ui.inflight.bracketsAndTargets.targetInBarFighter import TargetInBarFighter
from eve.client.script.ui.util.uix import GetOwnerLogo
from eve.common.lib.appConst import singletonBlueprintCopy
iconDict = {'listentry.PlaceEntry': 'res:/ui/Texture/WindowIcons/personallocations.png',
 'listentry.NoteItem': 'res:/ui/Texture/WindowIcons/note.png',
 'listentry.VirtualAgentMissionEntry': 'res:/ui/Texture/WindowIcons/journal.png',
 'listentry.FleetFinderEntry': 'res:/UI/Texture/WindowIcons/fleet.png',
 'listentry.FittingEntry': 'res:/ui/Texture/WindowIcons/fitting.png',
 'listentry.MailEntry': 'res:/UI/Texture/WindowIcons/evemail.png',
 'listentry.CorpAllianceEntry': 'res:/ui/Texture/WindowIcons/corporation.png',
 'listentry.QuickbarGroup': 'res:/ui/Texture/WindowIcons/smallfolder.png',
 'listentry.KillMail': 'res:/ui/Texture/WindowIcons/killreport.png',
 'listentry.KillMailCondensed': 'res:/ui/Texture/WindowIcons/killreport.png',
 'listentry.WarKillEntry': 'res:/UI/Texture/WindowIcons/wars.png',
 'listentry.WarEntry': 'res:/UI/Texture/WindowIcons/wars.png',
 'listentry.CertEntry': 'res:/UI/Texture/WindowIcons/certificates.png',
 'listentry.DroneMainGroup': 'res:/UI/Texture/WindowIcons/dronebay.png',
 'listentry.DroneSubGroup': 'res:/UI/Texture/WindowIcons/dronebay.png',
 'listentry.XmppChannelField': 'res:/ui/Texture/WindowIcons/chatchannel.png',
 'listentry.PointerWndEntry': 'res:/ui/texture/classes/HelpPointer/highlightElement64.png'}
iconsByNodeType = {'AccessGroupEntry': 'res:/UI/Texture/WindowIcons/accessGroups.png',
 'BookmarkFolderEntry': 'res:/UI/Texture/classes/Bookmarks/sharedFolderAddress_64.png'}
typeEntries = ('xtriui.InvItem', 'listentry.InvItem', 'listentry.InvAssetItem', 'listentry.InvAssetItemBySelection', 'listentry.InvItemWithVolume', 'xtriui.TypeIcon', 'uicls.GenericDraggableForTypeID', 'listentry.SkillTreeEntry', 'listentry.Item', 'listentry.ContractItemSelect', 'listentry.RedeemToken', 'listentry.FittingModuleEntry', 'listentry.KillItems', 'listentry.CustomsItem', 'uicls.FightersHealthGauge', 'listentry.QuickbarItem', 'listentry.GenericMarketItem', 'listentry.DirectionalScanResults', 'listentry.DroneEntry', 'xtriui.FittingSlot', 'xtriui.ModuleButton', 'xtriui.ShipUIModule')
iconSize = 64

def PrepareDrag_Override(dragContainer, dragSource, *args):
    column = 0
    row = 0
    for dragData in dragContainer.dragData:
        typeID = getattr(dragData, 'typeID', None) or getattr(dragData, 'invtype', None)
        if typeID is not None:
            groupID = evetypes.GetGroupID(typeID)
        else:
            groupID = None
        icon = _ConstructIcon(dragContainer, groupID, column, row)
        if isinstance(dragData, BaseDragData):
            icon.LoadIcon(dragData.GetIconTexturePath())
        else:
            _LoadIcon(icon, dragContainer, dragData, typeID)
        column += 1
        if column >= 3:
            column = 0
            row += 1
        if row > 2:
            break

    return (0, 0)


def _ConstructIcon(dragContainer, groupID, column, row):
    location_icon = groupID in (invConst.groupSolarSystem, invConst.groupConstellation, invConst.groupRegion)
    left = column * (iconSize + 10)
    top = row * (iconSize + 10)
    icon = DraggableIcon(parent=dragContainer, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, pos=(left,
     top,
     64,
     64), location_icon=location_icon)
    return icon


def _LoadIcon(icon, dragContainer, dragData, typeID):
    from eve.client.script.ui.shared.inventory.treeData import TreeDataInv, TreeDataInvFolder
    guid = getattr(dragData, '__guid__', None)
    if getattr(dragData, 'LoadIcon', None) is not None:
        dragData.LoadIcon(icon, dragContainer, iconSize)
    elif getattr(dragData, 'GetDragIcon', None):
        icon.SetTexturePath(dragData.GetDragIcon())
    elif guid in typeEntries:
        icon.LoadIconByTypeID(typeID=typeID, size=iconSize, isCopy=IsBlueprintCopy(dragData))
    elif guid in AllUserEntries():
        GetOwnerLogo(icon, dragData.charID, iconSize, noServerCall=False)
    elif guid in iconDict:
        icon.LoadIcon(iconDict.get(guid))
    elif guid and guid.startswith('listentry.ContractEntry'):
        iconName = 'res:/ui/Texture/WindowIcons/contracts.png'
        if 'Auction' in guid:
            iconName = 'res:/ui/Texture/WindowIcons/contractAuction.png'
        elif 'ItemExchange' in guid:
            iconName = 'res:/ui/Texture/WindowIcons/contractItemExchange.png'
        elif 'Courier' in guid:
            iconName = 'res:/ui/Texture/WindowIcons/contractCourier.png'
        icon.LoadIcon(iconName)
    elif getattr(dragData, 'isLandMark', None):
        landmarkIconNum = dragData.iconNum
        icon.sr.icon.LoadIcon(landmarkIconNum)
        icon.sr.icon.rectLeft = 64
        icon.sr.icon.rectWidth = 128
    elif guid in ('xtriui.ListSurroundingsBtn', 'listentry.LocationTextEntry', 'listentry.LocationGroup', 'listentry.LocationSearchItem', 'listentry.LabelLocationTextTop'):
        icon.LoadIconByTypeID(dragData.typeID, itemID=dragData.itemID)
    elif guid == 'listentry.PaletteEntry':
        icon.LoadIconByTypeID(dragData.id, itemID=dragData.id)
    elif guid in ('listentry.SkillEntry', 'listentry.SkillQueueSkillEntry'):
        icon.LoadIconByTypeID(dragData.invtype)
    elif guid == 'neocom.BtnDataNode':
        icon.LoadIcon(dragData.iconPath)
    elif isinstance(dragData, (TreeDataInv, TreeDataInvFolder)):
        icon.LoadIcon(dragData.GetIcon())
    elif guid == 'listentry.RecruitmentEntry':
        corpID = dragData.corporationID
        GetOwnerLogo(icon, corpID, iconSize, noServerCall=False)
    elif guid in ('uicls.TargetInBar', 'uicls.TargetInBarFighter'):
        if guid == 'uicls.TargetInBar':
            targetType = TargetInBar
        else:
            targetType = TargetInBarFighter
        icon.Flush()
        targetIcon = targetType(align=uiconst.TOPLEFT, pos=(0, 0, 64, 64), parent=icon)
        targetIcon.updatedamage = True
        targetIcon.AddUIObjects(slimItem=dragData.slimItem(), itemID=dragData.itemID)
        if getattr(dragData, 'OnBeginMoveTarget', None):
            dragData.OnBeginMoveTarget()
    elif getattr(dragData, 'typeID', None) == invConst.typeSkinMaterial:
        icon.LoadIcon(dragData.texturePath)
    elif getattr(dragData, 'nodeType', None) in iconsByNodeType:
        path = iconsByNodeType.get(dragData.nodeType)
        icon.LoadIcon(path)
    elif guid == 'listentry.AgencyHelpVideoEntry':
        icon.LoadIcon('res:/ui/texture/icons/bigplay_64.png')
    elif hasattr(dragData, 'typeID'):
        icon.LoadIconByTypeID(dragData.typeID)


def IsBlueprintCopy(node):
    if getattr(node, 'isCopy', None):
        return True
    bpData = getattr(node, 'bpData', None)
    if bpData:
        return not bpData.original
    if getattr(node, 'invtype', None):
        if getattr(node, 'rec', None) is None:
            return False
        node.isBlueprint = evetypes.GetCategoryID(node.invtype) == invConst.categoryBlueprint
        if node.isBlueprint:
            return node.rec.singleton == singletonBlueprintCopy
    return False
