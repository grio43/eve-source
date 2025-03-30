#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\stateFlag.py
import homestation.client
from brennivin.itertoolsext import Bundle
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
import eve.client.script.parklife.states as statesConst
import inventorycommon.const as inventoryConst
from eve.client.script.parklife.states import flagForcedOn
from eve.common.lib import appConst as const
from eve.client.script.ui import eveColor
from eve.common.script.sys import idCheckers
from stargate.client.const import EMANATION_GATE_UNAVAILABLE, EMANATION_GATE_AVAILABLE
from structures import STATE_UNANCHORED, DOCKING_ACCESS_UNKNOWN, STATE_ANCHOR_VULNERABLE
from structures.types import IsFlexStructure
from utillib import KeyVal
from carbonui.uicore import uicore
EXTRA_INFO_HOME_STATION = 'isHomeStation'
EXTRA_INFO_DOCKING_RIGHTS = 'hasDockingRights'
EXTRA_INFO_GATE_LOCK = 'gateLockValue'

def GetStateFlagFromData(data):
    charID = getattr(data, 'charID', 0)
    if charID == session.charid:
        return
    fakeSlimItem = KeyVal()
    fakeSlimItem.ownerID = charID
    fakeSlimItem.charID = charID
    fakeSlimItem.corpID = data.Get('corpID', 0)
    fakeSlimItem.allianceID = data.Get('allianceID', 0)
    fakeSlimItem.warFactionID = data.Get('warFactionID', 0)
    if getattr(data, 'bounty', None):
        if data.bounty.bounty > 0.0:
            fakeSlimItem.bounty = data.bounty
    fakeSlimItem.groupID = data.Get('groupID', inventoryConst.groupCharacter)
    fakeSlimItem.categoryID = data.Get('categoryID', inventoryConst.categoryOwner)
    fakeSlimItem.securityStatus = data.Get('securityStatus', None)
    flag = sm.GetService('stateSvc').CheckStates(fakeSlimItem, 'flag')
    return flag


def AddAndSetFlagIconFromData(data, parentCont, **kwargs):
    flag = GetStateFlagFromData(data)
    return AddAndSetFlagIcon(parentCont=parentCont, flag=flag, **kwargs)


def AddAndSetFlagIcon(parentCont, *args, **kwargs):
    flag = kwargs.get('flag', 0)
    stateFlagIcon = getattr(parentCont, 'stateFlagIcon', None)
    if not flag or flag == -1:
        if stateFlagIcon and not stateFlagIcon.destroyed:
            stateFlagIcon.ModifyIcon(flagInfo=None)
        return
    flagInfo = sm.GetService('stateSvc').GetStatePropsColorAndBlink(flag)
    if stateFlagIcon and not stateFlagIcon.destroyed:
        stateFlagIcon.ModifyIcon(flagInfo=flagInfo)
    else:
        stateFlagIcon = FlagIconWithState(parent=parentCont, flagInfo=flagInfo, **kwargs)
        parentCont.stateFlagIcon = stateFlagIcon
    return stateFlagIcon


def GetFlagTexturePath(iconIdx):
    if iconIdx == 1:
        return 'res:/UI/Texture/classes/FlagIcon/8/1.png'
    if iconIdx == 2:
        return 'res:/UI/Texture/classes/FlagIcon/8/2.png'
    if iconIdx == 3:
        return 'res:/UI/Texture/classes/FlagIcon/8/3.png'
    if iconIdx == 4:
        return 'res:/UI/Texture/classes/FlagIcon/8/4.png'
    if iconIdx == 5:
        return 'res:/UI/Texture/classes/FlagIcon/8/5.png'
    if iconIdx == 6:
        return 'res:/UI/Texture/classes/FlagIcon/8/6.png'
    if iconIdx == 7:
        return 'res:/UI/Texture/classes/FlagIcon/8/7.png'
    if iconIdx == 8:
        return 'res:/UI/Texture/classes/FlagIcon/8/8.png'
    if iconIdx == 9:
        return 'res:/UI/Texture/classes/FlagIcon/8/9.png'
    if iconIdx == 10:
        return 'res:/UI/Texture/classes/FlagIcon/8/10.png'
    if iconIdx == 11:
        return 'res:/UI/Texture/classes/FlagIcon/8/11.png'
    if iconIdx == 12:
        return 'res:/UI/Texture/classes/FlagIcon/8/12.png'
    if iconIdx == 13:
        return 'res:/UI/Texture/classes/FlagIcon/8/13.png'


class FlagIcon(Container):
    default_align = uiconst.TOPRIGHT
    default_width = 10
    default_height = 10
    default_idx = 0

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        if self.width > 10:
            self.flagBackground = Frame(bgParent=self, texturePath='res:/UI/Texture/Classes/FlagIcon/bgFrame.png')
        else:
            self.flagBackground = Fill(bgParent=self)
        self.flagBackground.opacity = 0
        iconSize = 8
        self.flagIcon = Sprite(parent=self, pos=(0,
         0,
         iconSize,
         iconSize), name='flagIcon', state=uiconst.UI_DISABLED, align=uiconst.CENTER)

    def SetIconTexturePath(self, iconIdx):
        self.flagIcon.texturePath = GetFlagTexturePath(iconIdx)

    def SetBackgroundColor(self, color, opacity = 0.75):
        newColor = (color[0],
         color[1],
         color[2],
         opacity)
        self.flagBackground.SetRGBA(*newColor)

    def ChangeIconVisibility(self, display):
        self.flagIcon.display = display

    def ChangeFlagPos(self, left, top, width, height):
        self.left = left
        self.top = top
        self.width = width
        self.height = height

    def ChangeIconPos(self, left, top, width, height):
        self.flagIcon.left = left
        self.flagIcon.top = top
        self.flagIcon.width = width
        self.flagIcon.height = height


class FlagIconWithState(FlagIcon):

    def ApplyAttributes(self, attributes):
        FlagIcon.ApplyAttributes(self, attributes)
        flagInfo = attributes.flagInfo
        showHint = attributes.get('showHint', True)
        extraInfo = attributes.extraInfo
        if flagInfo is not None:
            self.ModifyIcon(flagInfo=flagInfo, showHint=showHint, extraInfo=extraInfo)

    def ModifyIcon(self, flagInfo, showHint = True, extraInfo = None):
        if not flagInfo:
            self.display = False
            return
        self.display = True
        flagProperties = flagInfo.flagProperties
        self.flagIcon.SetRGBA(*flagProperties.iconColor)
        col = flagInfo.flagColor
        blink = flagInfo.flagBlink
        if blink:
            uicore.animations.FadeTo(self, startVal=0.0, endVal=1.0, duration=0.5, loops=uiconst.ANIM_REPEAT, curveType=uiconst.ANIM_WAVE)
        else:
            self.StopAnimations()
            self.opacity = 1.0
        self.SetBackgroundColor(col)
        self.SetIconTexturePath(flagProperties.iconIndex + 1)
        if showHint and flagProperties.text:
            self.hint = flagProperties.text
            self.state = uiconst.UI_NORMAL
        if extraInfo:
            if getattr(extraInfo, EXTRA_INFO_HOME_STATION, False):
                self.SetIconTexturePath(homestation.texture.flag_icon_index)
                self.SetBackgroundColor(homestation.Color.home_station_icon_background)
            elif getattr(extraInfo, EXTRA_INFO_DOCKING_RIGHTS, DOCKING_ACCESS_UNKNOWN) not in (DOCKING_ACCESS_UNKNOWN, None):
                iconIdx = 9 if extraInfo.hasDockingRights else 10
                self.SetIconTexturePath(iconIdx)
            elif getattr(extraInfo, EXTRA_INFO_GATE_LOCK, None) is not None:
                if extraInfo.gateLockValue == EMANATION_GATE_AVAILABLE:
                    iconIdx = 13
                    col = eveColor.CRYO_BLUE
                else:
                    iconIdx = 12
                    col = (0.75, 0.0, 0.0, 1.0)
                self.SetIconTexturePath(iconIdx)
                self.SetBackgroundColor(col)

    def SetFlagID(self, flagID):
        flagInfo = sm.GetService('stateSvc').GetStatePropsColorAndBlink(flagID)
        self.ModifyIcon(flagInfo)


def GetRelationShipFlag(itemID, corpID, allianceID):
    ret = sm.GetService('addressbook').GetRelationship(itemID, corpID, allianceID)
    relationships = [(ret.persToCorp, 'UI/PeopleAndPlaces/StandingPersToCorp'),
     (ret.persToPers, 'UI/PeopleAndPlaces/StandingPersToPers'),
     (ret.persToAlliance, 'UI/PeopleAndPlaces/StandingPersToAlliance'),
     (ret.corpToPers, 'UI/PeopleAndPlaces/StandingCorpToPers'),
     (ret.corpToCorp, 'UI/PeopleAndPlaces/StandingCorpToCorp'),
     (ret.corpToAlliance, 'UI/PeopleAndPlaces/StandingCorpToAlliance'),
     (ret.allianceToPers, 'UI/PeopleAndPlaces/StandingAllianceToPers'),
     (ret.allianceToCorp, 'UI/PeopleAndPlaces/StandingAllianceToCorp'),
     (ret.allianceToAlliance, 'UI/PeopleAndPlaces/StandingAllianceToAlliance')]
    relationship = 0.0
    flagHintPath = None
    for r, hintPath in relationships:
        if r != 0.0 and r > relationship or relationship == 0.0:
            relationship = r
            flagHintPath = hintPath

    flag = GetFlagFromRelationShip(relationship)
    return (flag, flagHintPath)


def GetFlagFromRelationShip(relationship):
    flag = None
    if relationship > const.contactGoodStanding:
        flag = statesConst.flagStandingHigh
    elif const.contactNeutralStanding < relationship <= const.contactGoodStanding:
        flag = statesConst.flagStandingGood
    elif const.contactBadStanding <= relationship < const.contactNeutralStanding:
        flag = statesConst.flagStandingBad
    elif relationship < const.contactBadStanding:
        flag = statesConst.flagStandingHorrible
    return flag


def GetExtraInfoForSlimItem(slimItem):
    extraInfo = Bundle()
    extraInfo.update(GetExtraInfoForStructure(slimItem))
    extraInfo.update(GetExtraInfoForHomeStation(slimItem))
    extraInfo.update(GetExtraInfoRestrictedGates(slimItem))
    return extraInfo


def GetExtraInfoForHomeStation(slimItem):
    return {EXTRA_INFO_HOME_STATION: IsHomeStation(slimItem)}


def IsHomeStation(slimItem):
    is_station = idCheckers.IsStation(slimItem.itemID)
    is_structure = idCheckers.IsStructure(slimItem.categoryID)
    if not is_station and not is_structure:
        return False
    if is_structure and slimItem.state == STATE_UNANCHORED:
        return False
    home_station_service = homestation.Service.instance()
    if home_station_service.is_home_station_data_loaded:
        home_station = home_station_service.get_home_station()
        if home_station.id == slimItem.itemID:
            return True
    return False


def GetExtraInfoForStructure(slimItem):
    if slimItem.categoryID != const.categoryStructure or slimItem.state == STATE_UNANCHORED:
        return {}
    if IsFlexStructure(slimItem.typeID):
        return {}
    structureProximityTrackerSvc = sm.GetService('structureProximityTracker')
    if structureProximityTrackerSvc.HasDockingAccessChanged():
        hasDockingRights = DOCKING_ACCESS_UNKNOWN
    else:
        hasDockingRights = FindDockingRightsToDisplay(structureProximityTrackerSvc, slimItem)
    return {EXTRA_INFO_DOCKING_RIGHTS: hasDockingRights}


def FindDockingRightsToDisplay(structureProximityTrackerSvc, slimItem):
    if slimItem.state == STATE_UNANCHORED or IsFlexStructure(slimItem.typeID):
        return DOCKING_ACCESS_UNKNOWN
    hasDockingRights = HasDockingRights(slimItem, structureProximityTrackerSvc)
    if slimItem.state == STATE_ANCHOR_VULNERABLE and not hasDockingRights:
        hasDockingRights = DOCKING_ACCESS_UNKNOWN
    return hasDockingRights


def HasDockingRights(slimItem, structureProximityTrackerSvc):
    hasDockingRights = structureProximityTrackerSvc.IsStructureDockable(slimItem.itemID)
    return hasDockingRights


def GetExtraInfoRestrictedGates(slimItem):
    gateLockValue = GetGateLockValueForSlimItem(slimItem)
    if gateLockValue:
        return {EXTRA_INFO_GATE_LOCK: gateLockValue}
    return {}


def GetGateLockValueForSlimItem(slimItem):
    if slimItem.groupID != const.groupStargate:
        return {}
    lock_details = _GetGateLockDetails()
    if not lock_details:
        return {}
    return GetGateLockValue(lock_details.gate_id, slimItem.itemID)


def GetGateLockValue(lockedGateID, gateID):
    if gateID == lockedGateID:
        return EMANATION_GATE_AVAILABLE
    return EMANATION_GATE_UNAVAILABLE


def GetLockedToGateID():
    lock_details = _GetGateLockDetails()
    if lock_details:
        return lock_details.gate_id


def _GetGateLockDetails():
    lock_datails = sm.GetService('gatejump').GetGateLockDetails()
    if lock_datails and lock_datails.solar_system_id != session.solarsystemid:
        return None
    return lock_datails


def GetExtraInfoForNode(node):
    return Bundle(hasDockingRights=node.hasDockingRights, isHomeStation=node.isHomeStation, gateLockValue=node.gateLockValue)


def GetIconFlagAndBackgroundFlag(slimItem, stateSvc = None):
    if stateSvc is None:
        stateSvc = sm.GetService('stateSvc')
    iconFlag, backgroundFlag = stateSvc.GetIconAndBackgroundFlags(slimItem)
    if iconFlag == 0:
        if slimItem.categoryID == const.categoryStructure or IsHomeStation(slimItem) or GetGateLockValueForSlimItem(slimItem):
            iconFlag = flagForcedOn
    return (iconFlag, backgroundFlag)
