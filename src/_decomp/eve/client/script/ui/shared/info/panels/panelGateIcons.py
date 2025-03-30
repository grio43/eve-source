#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\panels\panelGateIcons.py
import itertoolsext
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.entries.mouse_inside_scroll_entry import MouseInsideScrollEntry
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveIcon import GetLogoIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.eveScroll import Scroll
from eve.common.lib import appConst as const
import evegraphics.gateLogoConst as gateLogoConst
from eveservices.menu import GetMenuService
from eveuniverse.security import securityClassHighSec, securityClassLowSec, securityClassZeroSec, SecurityClassFromLevel
from localization import GetByLabel
import carbonui.const as uiconst

def is_hazardous_security_transition(sourceSecurity, destinationSecurity):
    currentSecurityClass = SecurityClassFromLevel(sourceSecurity)
    destSecurityClass = SecurityClassFromLevel(destinationSecurity)
    return (currentSecurityClass, destSecurityClass) in HAZARDOUS_SECURITY_TRANSITIONS


def is_there_any_warning(destinationSecurity, destinationSystemStatusIcons):
    sourceSecurity = cfg.mapSystemCache[session.solarsystemid2].pseudoSecurity
    isHazardousSecurityTransition = is_hazardous_security_transition(sourceSecurity, destinationSecurity)
    return isHazardousSecurityTransition or itertoolsext.any(destinationSystemStatusIcons, lambda x: x in gateLogoConst.HAZARDOUS_STATUS_ICONS)


class PanelGateIcons(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.gateIconData = attributes.gateIconData

    def Load(self):
        self.Flush()
        entries = self.GetOwnerEntries()
        self.scroll = Scroll(parent=self, padding=const.defaultPadding)
        self.scroll.Load(contentList=entries)

    def GetOwnerEntries(self):
        entries = []
        sourceSecurity = cfg.mapSystemCache[session.solarsystemid2].pseudoSecurity
        destinationSecurity = cfg.mapSystemCache[self.gateIconData.destinationSolarSystemID].pseudoSecurity
        isHazardousSecurityTransition = is_hazardous_security_transition(sourceSecurity, destinationSecurity)
        isThereAnyWarning = is_there_any_warning(destinationSecurity, self.gateIconData.destinationSystemStatusIcons)
        originSystemOwnerID = self.gateIconData.originSystemOwnerID
        if originSystemOwnerID:
            ownerInfo = cfg.eveowners.Get(originSystemOwnerID)
            text = GetByLabel('UI/GateIcons/CurrentSystemOwner', ownerName=ownerInfo.name)
            entry = GetFromClass(GateOwnerEntry, {'ownerID': originSystemOwnerID,
             'text': text,
             'ownerTypeID': ownerInfo.typeID,
             'isThereAnyWarning': isThereAnyWarning})
            entries.append(entry)
        destSystemOwnerID = self.gateIconData.destinationSystemOwnerID
        if destSystemOwnerID:
            ownerInfo = cfg.eveowners.Get(destSystemOwnerID)
            text = GetByLabel('UI/GateIcons/DestSystemOwner', ownerName=ownerInfo.name)
            entry = GetFromClass(GateOwnerEntry, {'ownerID': destSystemOwnerID,
             'text': text,
             'ownerTypeID': ownerInfo.typeID,
             'isThereAnyWarning': isThereAnyWarning})
            entries.append(entry)
        for eachIcon in self.gateIconData.destinationSystemStatusIcons:
            if eachIcon.startswith('SEC_'):
                isHazard = isHazardousSecurityTransition
            else:
                isHazard = eachIcon in gateLogoConst.HAZARDOUS_STATUS_ICONS
            entry = GetFromClass(GateIconEntry, data={'texturePath': GetFullTexturePath(gateLogoConst.SYSTEM_STATUS_ICONS.get(eachIcon, None)),
             'text': GetByLabel(TEXT_FOR_SYSTEM_STATUS_ICONS.get(eachIcon, '')),
             'isHazard': isHazard,
             'isThereAnyWarning': isThereAnyWarning})
            entries.append(entry)

        return entries


class GateOwnerEntry(MouseInsideScrollEntry):
    ENTRYHEIGHT = 50

    def ApplyAttributes(self, attributes):
        MouseInsideScrollEntry.ApplyAttributes(self, attributes)
        self.node = attributes.node
        isThereAnyWarning = self.node.isThereAnyWarning
        if isThereAnyWarning:
            iconLeft = 42
        else:
            iconLeft = 6
        ownerID = self.node.ownerID
        self.ownerIcon = GetLogoIcon(itemID=ownerID, parent=self, acceptNone=False, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL, pos=(iconLeft,
         0,
         48,
         48), ignoreSize=True)
        if isThereAnyWarning:
            labelLeft = 96
        else:
            labelLeft = 58
        EveLabelMedium(parent=self, text=self.node.text, align=uiconst.CENTERLEFT, left=labelLeft)

    def Load(self, node):
        pass

    def GetMenu(self):
        return GetMenuService().GetMenuFromItemIDTypeID(self.node.ownerID, self.node.ownerTypeID)


class GateIconEntry(MouseInsideScrollEntry):
    ENTRYHEIGHT = 50
    ICONSIZE = 48
    ICON_CROP = 5
    WARNING_PATH = 'res:/UI/Texture/classes/gatenotifications/Stargate_TravelWarning3_tri.png'

    def ApplyAttributes(self, attributes):
        MouseInsideScrollEntry.ApplyAttributes(self, attributes)
        self.node = attributes.node
        isThereAnyWarning = self.node.isThereAnyWarning
        isHazard = self.node.isHazard
        iconLeft = 10
        if isThereAnyWarning:
            iconLeft += 36
            if isHazard:
                hint = GetByLabel('UI/GateIcons/Hazardous')
                hazardIcon = Sprite(parent=self, name='hazardIcon', texturePath=self.WARNING_PATH, pos=(10, 0, 32, 32), align=uiconst.CENTERLEFT, opacity=0.75, hint=hint)
        texturePath = self.node.texturePath
        croppedSize = self.ICONSIZE - 2 * self.ICON_CROP
        spriteCont = Container(parent=self, name='spriteCont', pos=(iconLeft,
         0,
         croppedSize,
         croppedSize), align=uiconst.CENTERLEFT, clipChildren=True)
        Sprite(parent=spriteCont, name='icon', texturePath=texturePath, pos=(0,
         0,
         self.ICONSIZE,
         self.ICONSIZE), align=uiconst.CENTER, opacity=0.75)
        EveLabelMedium(parent=self, text=self.node.text, align=uiconst.CENTERLEFT, left=spriteCont.left + spriteCont.width + 10)

    def Load(self, node):
        pass


def GetFullTexturePath(textureName):
    return gateLogoConst.SYSTEM_STATUS_DIR + textureName


TEXT_FOR_SYSTEM_STATUS_ICONS = {gateLogoConst.INCURSION: 'UI/GateIcons/Incursion',
 gateLogoConst.TRIGLAVIAN_INVASION_LEVEL_0: 'UI/GateIcons/Invasion',
 gateLogoConst.TRIGLAVIAN_INVASION_LEVEL_1: 'UI/GateIcons/Invasion',
 gateLogoConst.TRIGLAVIAN_INVASION_LEVEL_2: 'UI/GateIcons/Invasion',
 gateLogoConst.FW_NORMAL: 'UI/GateIcons/FwNormal',
 gateLogoConst.FW_CONTESTED: 'UI/GateIcons/FwContested',
 gateLogoConst.SOV_NORMAL: 'UI/GateIcons/SovNormal',
 gateLogoConst.SOV_CONTESTED: 'UI/GateIcons/SovContested',
 gateLogoConst.DANGER_NORMAL: 'UI/GateIcons/DangerNormal',
 gateLogoConst.DANGER_CAUTION: 'UI/GateIcons/DangerCaution',
 gateLogoConst.DANGER_HIGH: 'UI/GateIcons/DangerHigh',
 gateLogoConst.SECURITY_0_0: 'UI/GateIcons/SecurityStatus',
 gateLogoConst.SECURITY_0_1: 'UI/GateIcons/SecurityStatus',
 gateLogoConst.SECURITY_0_2: 'UI/GateIcons/SecurityStatus',
 gateLogoConst.SECURITY_0_3: 'UI/GateIcons/SecurityStatus',
 gateLogoConst.SECURITY_0_4: 'UI/GateIcons/SecurityStatus',
 gateLogoConst.SECURITY_0_5: 'UI/GateIcons/SecurityStatus',
 gateLogoConst.SECURITY_0_6: 'UI/GateIcons/SecurityStatus',
 gateLogoConst.SECURITY_0_7: 'UI/GateIcons/SecurityStatus',
 gateLogoConst.SECURITY_0_8: 'UI/GateIcons/SecurityStatus',
 gateLogoConst.SECURITY_0_9: 'UI/GateIcons/SecurityStatus',
 gateLogoConst.SECURITY_1_0: 'UI/GateIcons/SecurityStatus',
 gateLogoConst.GATE_CLOSED: 'UI/GateIcons/GateClosed',
 gateLogoConst.GATE_OPEN: 'UI/GateIcons/GateOpen',
 gateLogoConst.TRAFFIC_LOW: 'UI/GateIcons/TrafficLow',
 gateLogoConst.TRAFFIC_MEDIUM: 'UI/GateIcons/TrafficMedium',
 gateLogoConst.TRAFFIC_HIGH: 'UI/GateIcons/TrafficHigh'}
HAZARDOUS_SECURITY_TRANSITIONS = [(securityClassHighSec, securityClassLowSec), (securityClassHighSec, securityClassZeroSec), (securityClassLowSec, securityClassZeroSec)]
