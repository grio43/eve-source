#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\infoPanelLocationInfo.py
import log
import telemetry
import carbonui.const as uiconst
import carbonui.fontconst
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
import eveformat.client
import evelink.client
import localization
import threadutils
import trinity
import uthread2
from carbon.common.script.util import timerstuff
from carbon.common.script.util.commonutils import StripTags
from carbon.common.script.util.format import FmtAmt
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from entosis.occupancyCalculator import GetOccupancyMultiplier
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelSmall, EveLabelLarge
from eve.client.script.ui.inflight.tidiIndicator import TiDiIndicator
from eve.client.script.ui.shared.infoPanels.InfoPanelBase import InfoPanelBase
from eve.client.script.ui.shared.infoPanels.const import infoPanelUIConst
from eve.client.script.ui.shared.infoPanels.const.infoPanelConst import PANEL_LOCATION_INFO
from eve.client.script.ui.shared.infoPanels.listSurroundingsBtn import ListSurroundingsBtn
from eve.client.script.ui.shared.infoPanels.locationInfoConst import SYSTEM_INFO_SHOW_NEAREST_SETTING, SYSTEM_INFO_SHOW_SOVEREIGNTY
from eve.client.script.ui.shared.pointerTool.pointerToolConst import UNIQUE_NAME_LOCATION_INFO_PANEL
from eve.common.lib import appConst
from eve.common.script.sys import idCheckers
from eve.common.script.sys.idCheckers import IsAbyssalSpaceSystem
from eve.common.script.sys.idCheckers import IsKnownSpaceSystem
from eve.common.script.sys.idCheckers import IsVoidSpaceSystem
from eve.common.script.sys.idCheckers import IsWormholeSystem
from eveservices.menu import GetMenuService
from factionwarfare.client.text import GetLocalVictoryPointStateText
from pirateinsurgency.client.dashboard.const import CORRUPTION_STAGES
from solarsysteminterference.client.ui.interference_indicator import InterferenceIndicator
from solarsysteminterference.util import SystemCanHaveInterference
from sovDashboard import ShouldUpdateStructureInfo, GetSovStructureInfoByTypeID
from sovDashboard.cynoJammerIcon import CynoJammerIcon
from sovDashboard.dashboardSovHolderIcon import SovHolderIcon
from sovDashboard.defenseMultiplierIcon import DefenseMultiplierIcon
from stackless_response_router.exceptions import TimeoutException
from stargate.client import get_gate_lock_messenger
from stargate.client.gateLockController import GateLockController
from uihider import UiHiderMixin
from uthread2 import call_after_simtime_delay, StartTasklet
from utillib import KeyVal

class InfoPanelLocationInfo(UiHiderMixin, InfoPanelBase):
    default_name = 'InfoPanelLocationInfo'
    uniqueUiName = UNIQUE_NAME_LOCATION_INFO_PANEL
    panelTypeID = PANEL_LOCATION_INFO
    label = 'UI/Neocom/SystemInfo'
    default_iconTexturePath = 'res:/UI/Texture/Classes/InfoPanels/LocationInfo.png'
    __notifyevents__ = InfoPanelBase.__notifyevents__[:]
    __notifyevents__.extend(['OnSolarsystemSovStructureChanged',
     'OnCapitalSystemChanged',
     'OnCynoJammerChanged',
     'OnCurrentSystemSecurityChanged',
     'OnDynamicBountyUpdate_Local',
     'OnWarzoneOccupationStateUpdated_Local',
     'OnCorruptionValueChanged_local',
     'OnSuppressionValueChanged_local',
     'OnEmanationLockUpdated'])

    def ApplyAttributes(self, attributes):
        super(InfoPanelLocationInfo, self).ApplyAttributes(attributes)
        self.fwWarzoneSvc = sm.GetService('fwWarzoneSvc')
        self.fwVictoryPointSvc = sm.GetService('fwVictoryPointSvc')
        self.sovSvc = sm.GetService('sov')
        self.infoPanelService = sm.GetService('infoPanel')
        self.dynamicResourceSvc = sm.GetService('dynamicResourceSvc')
        self.systemInterferenceSvc = sm.GetService('solarsystemInterferenceSvc')
        self.corruptionSuppressionSvc = sm.GetService('corruptionSuppressionSvc')
        self.validNearBy = [appConst.groupAsteroidBelt,
         appConst.groupMoon,
         appConst.groupPlanet,
         appConst.groupStargate]
        self.nearby = None
        self.locationTimer = None
        self.lastLocationID = None
        self.sovHolderIcons = []
        self.bonusIcon = None
        self.cynoJammerIcon = None
        self.tidiIndicator = TiDiIndicator(parent=self.headerCont, name='tidiIndicator', align=uiconst.CENTERLEFT, pos=(0, 0, 24, 24))
        self.headerLabelCont = ContainerAutoSize(name='headerLabelCont', parent=self.headerCont, align=uiconst.CENTERLEFT, height=23, alignMode=uiconst.TOLEFT)
        self.headerLabelSystemName = self.headerCls(name='headerLabelSystemName', parent=self.headerLabelCont, align=uiconst.TOLEFT, uniqueUiName=pConst.UNIQUE_NAME_SYSTEM_NAME_BTN)
        self.headerLabelSecStatus = self.headerCls(name='headerLabelSecStatus', parent=self.headerLabelCont, align=uiconst.TOLEFT, padLeft=6, uniqueUiName=pConst.UNIQUE_NAME_SYSTEM_SECURITY_BTN)
        self.headerLabelLocationTrace = self.headerCls(name='headerLabelLocationTrace', parent=self.headerLabelCont, align=uiconst.TOLEFT, padLeft=2)
        self.nearestLocationInfo = eveLabel.EveLabelMedium(name='nearestLocationInfo', parent=self.mainCont, align=uiconst.TOTOP)
        self.dynamicResourceInfoContainer = Container(parent=self.mainCont, align=uiconst.TOTOP, height=20, padTop=2)
        self.sovInfoContainer = Container(parent=self.mainCont, align=uiconst.TOTOP, height=42, padTop=2)
        self.emanationLockInfoContainer = Container(name='emanationLockInfoContainer', parent=self.mainCont, align=uiconst.TOTOP, height=22, padTop=2)

    def GetHeaderTextMaxWidth(self):
        return infoPanelUIConst.PANELWIDTH - infoPanelUIConst.LEFTPAD

    @staticmethod
    def IsAvailable():
        return True

    def ConstructHeaderButton(self):
        btn = ListSurroundingsBtn(parent=self.headerBtnCont, align=uiconst.TOPRIGHT, pos=(0,
         0,
         self.topCont.height,
         self.topCont.height), texturePath=self.default_iconTexturePath, iconSize=16, showIcon=True, useDynamicMapItems=True, uniqueUiName=pConst.UNIQUE_NAME_LOCATION_ITEMS)
        btn.hint = localization.GetByLabel('UI/Neocom/ListItemsInSystem')
        btn.sr.owner = self
        btn.sr.groupByType = 1
        btn.filterCurrent = 1
        btn.SetSolarsystemID(session.solarsystemid2)
        return btn

    def ConstructNormal(self):
        self.UpdateLocationInfo()

    def ConstructCompact(self):
        self.UpdateMainLocationInfo()

    @telemetry.ZONE_METHOD
    def UpdateLocationInfo(self):
        if session.solarsystemid2 and session.charid:
            self.UpdateMainLocationInfo()
            self.UpdateNearestOrStationLocationInfo()
            self.UpdateDynamicResourceInfo()
            self.UpdateSOVLocationInfo()
            self.UpdateEmanationLockInfo()

    @telemetry.ZONE_METHOD
    def UpdateMainLocationInfo(self):
        if session.solarsystemid2:
            if IsAbyssalSpaceSystem(session.solarsystemid2):
                abyssSvc = sm.GetService('abyss')
                text = abyssSvc.get_mangled_system_name(session.solarsystemid2, session.charid)
                self.headerLabelSystemName.fontPath = carbonui.fontconst.TRIGLAVIAN
                self.headerLabelSystemName.state = uiconst.UI_DISABLED
                self.headerLabelSystemName.text = text
            elif IsVoidSpaceSystem(session.solarsystemid2):
                self.headerLabelSystemName.fontPath = None
                self.headerLabelSystemName.state = uiconst.UI_NORMAL
                self.headerLabelSystemName.text = localization.GetByLabel('UI/Common/Unknown')
            else:
                systemNameText = evelink.location_link(session.solarsystemid2, hint=StripTags(localization.GetByLabel('UI/Neocom/Autopilot/CurrentLocationType', itemType=appConst.typeSolarSystem)))
                try:
                    corruptionStage = self.corruptionSuppressionSvc.GetCurrentSystemCorruption_Cached()
                    lawless = corruptionStage == CORRUPTION_STAGES
                except TimeoutException:
                    lawless = False

                secStatusHintText = localization.GetByLabel('UI/Map/StarMap/SecurityStatus')
                if lawless:
                    secStatusHintText = localization.GetByLabel('UI/PirateInsurgencies/lawlessSecurityWarning')
                secStatusText = eveformat.hint(hint=secStatusHintText, text=eveformat.solar_system_security_status(session.solarsystemid2, lawless=lawless))
                systemRegionAndConstellationTraceText = self.infoPanelService.GetSolarSystemRegionAndConstellationTraceDisplayString(session.solarsystemid2)
                self.headerLabelSystemName.fontPath = None
                self.headerLabelSystemName.state = uiconst.UI_NORMAL
                self.headerLabelSecStatus.fontPath = None
                self.headerLabelSecStatus.state = uiconst.UI_NORMAL
                self.headerLabelLocationTrace.fontPath = None
                self.headerLabelLocationTrace.state = uiconst.UI_NORMAL
                self.headerLabelSystemName.text = systemNameText
                self.headerLabelSecStatus.text = secStatusText
                if SystemCanHaveInterference(session.solarsystemid2):
                    self.headerLabelSystemName.LoadTooltipPanel = self._interference_tooltip_panel
                self.headerLabelLocationTrace.text = systemRegionAndConstellationTraceText
                self.headerLabelLocationTrace.top = 5
            newTidiLeft = self.headerLabelSystemName.left + self.headerLabelSystemName.textwidth + self.headerLabelSecStatus.left + 6 + self.headerLabelSecStatus.textwidth + self.headerLabelLocationTrace.left + 2 + self.headerLabelLocationTrace.textwidth + 4
            headerTextMaxWidth = self.GetHeaderTextMaxWidth()
            locationTraceMaxWidth = headerTextMaxWidth - (self.headerLabelSystemName.textwidth + self.headerLabelSecStatus.textwidth)
            fadeWidth = self.HEADER_FADE_WIDTH
            if newTidiLeft + self.tidiIndicator.width > headerTextMaxWidth:
                locationTraceMaxWidth -= self.tidiIndicator.width + 2
                newTidiLeft = headerTextMaxWidth - self.tidiIndicator.width
                fadeWidth = 4
            self.tidiIndicator.left = newTidiLeft
            self.headerLabelLocationTrace.SetRightAlphaFade(locationTraceMaxWidth, fadeWidth)
            self.headerButton.SetSolarsystemID(session.solarsystemid2)

    def _interference_tooltip_panel(self, panel, *args):
        grid = LayoutGrid(columns=2, rows=2, state=uiconst.UI_NORMAL)
        grid.AddCell(EveLabelLarge(text=localization.GetByLabel('UI/Neocom/Autopilot/CurrentLocationType', itemType=appConst.typeSolarSystem), bold=True), colSpan=2)
        interferenceCont = ContainerAutoSize(align=uiconst.TOLEFT)
        (InterferenceIndicator(parent=interferenceCont, name='tooltipInterferenceIndicator', state=uiconst.UI_NORMAL, align=uiconst.TOLEFT, systemInterferenceSvc=self.systemInterferenceSvc, top=-2, left=4),)
        (EveLabelLarge(parent=interferenceCont, text=localization.GetByLabel('UI/Common/Percentage', percentage=FmtAmt(self.systemInterferenceSvc.GetLocalInterferenceStateNow().normalisedInterferenceLevel * 100, showFraction=0)), align=uiconst.TOLEFT, padLeft=6),)
        grid.AddCell(EveLabelLarge(text=localization.GetByLabel('UI/Neocom/interference')), cellPadding=(0, 5, 0, 0), colSpan=1)
        grid.AddCell(interferenceCont, cellPadding=(0, 5, 0, 0), colSpan=1)
        panel.AddCell(grid, columns=panel.columns, cellPadding=(5, 5, 5, 5))

    @telemetry.ZONE_METHOD
    def UpdateNearestOrStationLocationInfo(self, nearestBall = None):
        if IsAbyssalSpaceSystem(session.solarsystemid2) or IsVoidSpaceSystem(session.solarsystemid2):
            self.nearestLocationInfo.state = uiconst.UI_HIDDEN
            return
        nearestOrStationLabel = ''
        if SYSTEM_INFO_SHOW_NEAREST_SETTING.is_enabled() and session.solarsystemid2:
            if session.stationid or session.structureid:
                try:
                    if session.stationid:
                        itemID = session.stationid
                        typeID = sm.GetService('station').stationItem.stationTypeID
                    else:
                        itemID = session.structureid
                        typeID = sm.GetService('structureDirectory').GetStructureInfo(itemID).typeID
                    stationName = cfg.evelocations.Get(itemID).name
                    nearestOrStationLabel = "<url=showinfo:%d//%d alt='%s'>%s</url>" % (typeID,
                     itemID,
                     localization.GetByLabel('UI/Generic/CurrentStation'),
                     stationName)
                except AttributeError as e:
                    log.LogException('Failed when getting station/structure name')

            else:
                nearestBall = nearestBall or self.GetNearestBall()
                if nearestBall:
                    self.nearby = nearestBall.id
                    slimItem = sm.StartService('michelle').GetItem(nearestBall.id)
                    if slimItem:
                        nearestOrStationLabel = "<url=showinfo:%d//%d alt='%s'>%s</url>" % (slimItem.typeID,
                         slimItem.itemID,
                         localization.GetByLabel('UI/Neocom/Nearest'),
                         cfg.evelocations.Get(nearestBall.id).locationName)
                if self.locationTimer is None:
                    self.locationTimer = timerstuff.AutoTimer(1313, self.CheckNearest)
        if nearestOrStationLabel:
            self.nearestLocationInfo.text = nearestOrStationLabel
            self.nearestLocationInfo.state = uiconst.UI_NORMAL
        else:
            self.nearestLocationInfo.state = uiconst.UI_HIDDEN

    def FlushSovInfoContainer(self):
        self.sovInfoContainer.Flush()
        self.sovHolderIcons = []

    def _UpdateDynamicResourceInfoAsync(self):
        dynamicBountyOutput, dbsIsActive = self.dynamicResourceSvc.GetDynamicBountySettingForCurrentSystem()
        if dbsIsActive:
            percentageOutput = dynamicBountyOutput * 100
            self.dynamicResourceInfoContainer.display = True
            bounties = EveLabelSmall(parent=self.dynamicResourceInfoContainer, text=localization.GetByLabel('UI/Neocom/SystemBountyOutputLabel', output=percentageOutput), align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL)
            bounties.hint = localization.GetByLabel('UI/Neocom/SystemBountyOutputHint', output=percentageOutput)

    def UpdateDynamicResourceInfo(self):
        self.dynamicResourceInfoContainer.Flush()
        self.dynamicResourceInfoContainer.display = False
        StartTasklet(self._UpdateDynamicResourceInfoAsync)

    @telemetry.ZONE_METHOD
    def UpdateSOVLocationInfo(self):
        self.FlushSovInfoContainer()
        isKnownSpace = IsKnownSpaceSystem(session.solarsystemid2)
        isWormhole = IsWormholeSystem(session.solarsystemid2)
        if SYSTEM_INFO_SHOW_SOVEREIGNTY.is_enabled() and session.solarsystemid2 and (isKnownSpace or isWormhole):
            self.sovInfoContainer.display = True
            if isWormhole:
                self.DrawWormholeInfo()
                return
            fwOccupationState = self.fwWarzoneSvc.GetLocalOccupationState()
            factionID = self._GetSolarsystemFactionID(session.solarsystemid2, fwOccupationState)
            if factionID:
                self.DrawUnclaimableSystemInfo(factionID, fwOccupationState is not None)
            else:
                solarsystemStructureInfo = self.sovSvc.GetSovStructuresInfoForSolarSystem(session.solarsystemid2)
                self.DrawClaimableSystemInfo(solarsystemStructureInfo)
        else:
            self.sovInfoContainer.display = False

    def _GetSolarsystemFactionID(self, solarsystemID, fwOccupationState):
        if fwOccupationState is not None:
            return fwOccupationState.occupierID
        solarSystem = cfg.mapSystemCache.get(solarsystemID, None)
        if solarSystem:
            return getattr(solarSystem, 'factionID', None)

    def GetAllianceIDFromCorpID(self, corpID):
        if corpID:
            return sm.GetService('corp').GetCorporation(corpID).allianceID

    def ShowMultiplyBonusesIcon(self, parent, isCapital, left, capitalOwnerID):
        devIndexInfo = self.sovSvc.GetIndexInfoForSolarsystem(session.solarsystemid2)
        multiplier = 1 / GetOccupancyMultiplier(devIndexInfo.industrialIndexLevel, devIndexInfo.militaryIndexLevel, devIndexInfo.strategicIndexLevel, isCapital)
        devIndexLevelInfo = (devIndexInfo.militaryIndexLevel, devIndexInfo.industrialIndexLevel, devIndexInfo.strategicIndexLevel)
        if self.bonusIcon and not self.bonusIcon.destroyed:
            self.bonusIcon.SetStatusFromMultiplier(multiplier, devIndexLevelInfo)
            self.bonusIcon.ChangeCapitalState(isCapital=isCapital)
        else:
            self.bonusIcon = DefenseMultiplierIcon(parent=parent, iconSize=32, align=uiconst.CENTERLEFT, pos=(left,
             0,
             60,
             60), currentMultiplier=multiplier, devIndexes=devIndexLevelInfo, isCapital=isCapital, capitalOwnerID=capitalOwnerID)

    def DrawWormholeInfo(self):
        self.sovInfoContainer.height = 10
        EveLabelMedium(parent=self.sovInfoContainer, text=localization.GetByLabel('UI/Neocom/Unclaimable'), align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL)

    def DrawUnclaimableSystemInfo(self, factionID, isFacWar):
        tcuIcon = SovHolderIcon(parent=self.sovInfoContainer, align=uiconst.CENTERLEFT, structureInfo=KeyVal(typeID=appConst.typeTerritorialClaimUnit, solarSystemID=session.solarsystemid2, ownerID=factionID))
        factionText = localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=cfg.eveowners.Get(factionID).name, info=('showinfo', appConst.typeFaction, factionID))
        if isFacWar:
            victoryPointState = self.fwVictoryPointSvc.GetLocalVictoryPointState()
            victoryPointStateText = GetLocalVictoryPointStateText(victoryPointState)
            factionText = '%s %s' % (factionText, victoryPointStateText)
        EveLabelMedium(parent=self.sovInfoContainer, text=factionText, left=tcuIcon.width + 4, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL)
        if sm.GetService('incursion').GetActiveIncursionData():
            self.cynoJammerIcon = CynoJammerIcon(parent=self.sovInfoContainer, iconSize=28, align=uiconst.CENTERRIGHT, pos=(0, 0, 32, 32), useBackground=False)

    def DrawClaimableSystemInfo(self, solarsystemStructureInfo):
        structureInfosByTypeID = GetSovStructureInfoByTypeID(solarsystemStructureInfo)

        def GetMouseDownFunction(sovHolderIcon):

            def OnMouseDownFunction(button):
                SovHolderIcon.OnMouseDown(sovHolderIcon, button)
                itemID = sovHolderIcon.structureInfo.get('itemID', None)
                if itemID:
                    GetMenuService().TryExpandActionMenu(itemID, sovHolderIcon)

            return OnMouseDownFunction

        xPos = -4
        for structureTypeID, structureInfo in structureInfosByTypeID.iteritems():
            sovHolderIcon = SovHolderIcon(parent=self.sovInfoContainer, left=xPos, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL, structureInfo=structureInfo, showStructureStatusBar=True)
            sovHolderIcon.OnMouseDown = GetMouseDownFunction(sovHolderIcon)
            self.sovHolderIcons.append(sovHolderIcon)
            xPos += sovHolderIcon.width + 6

        tcuInfo = structureInfosByTypeID[appConst.typeTerritorialClaimUnit]
        isCapital = tcuInfo.get('isCapital', False)
        capitalOwnerID = tcuInfo.get('allianceID', None)
        self.cynoJammerIcon = CynoJammerIcon(parent=self.sovInfoContainer, iconSize=32, align=uiconst.CENTERLEFT, pos=(xPos,
         0,
         40,
         40))
        xPos += self.cynoJammerIcon.width + 6
        self.ShowMultiplyBonusesIcon(self.sovInfoContainer, isCapital, xPos, capitalOwnerID)

    def CheckNearest(self):
        if not session.solarsystemid or not self.headerLabelCont:
            self.locationTimer = None
            return
        nearestBall = self.GetNearestBall()
        if nearestBall and self.nearby != nearestBall.id:
            self.UpdateNearestOrStationLocationInfo(nearestBall)

    def GetNearestBall(self, fromBall = None, getDist = 0):
        ballPark = sm.GetService('michelle').GetBallpark()
        if not ballPark:
            return
        lst = []
        for ballID, ball in ballPark.balls.iteritems():
            slimItem = ballPark.GetInvItem(ballID)
            if slimItem and slimItem.groupID in self.validNearBy:
                if fromBall:
                    dist = trinity.TriVector(ball.x - fromBall.x, ball.y - fromBall.y, ball.z - fromBall.z).Length()
                    lst.append((dist, ball))
                else:
                    lst.append((ball.surfaceDist, ball))

        lst.sort()
        if getDist:
            return lst[0]
        if lst:
            return lst[0][1]

    def OnSolarsystemSovStructureChanged(self, solarsystemID, whatChanged, sourceItemID = None):
        if sourceItemID is None:
            if session.solarsystemid2 == solarsystemID and session.charid:
                self.UpdateSOVLocationInfo()
            return
        for buttonIcon in self.sovHolderIcons:
            if ShouldUpdateStructureInfo(buttonIcon.structureInfo, sourceItemID):
                newStructureInfo = self.sovSvc.GetSpecificSovStructuresInfoInSolarSystem(solarsystemID, sourceItemID)
                buttonIcon.SolarsystemSovStructureChanged(sourceItemID, newStructureInfo, whatChanged)
                return

    def OnCapitalSystemChanged(self, change):
        allianceID, oldSolarSystemID, newSolarSystemID = change
        if oldSolarSystemID is None:
            call_after_simtime_delay(self.UpdateSOVLocationInfo, 30)
        else:
            self.UpdateSOVLocationInfo()

    def OnCynoJammerChanged(self, solarsystemID, onlineSimTime):
        if solarsystemID != session.solarsystemid2:
            return
        if self.cynoJammerIcon:
            self.cynoJammerIcon.UpdateIconState(onlineSimTime)

    def OnCurrentSystemSecurityChanged(self):
        self.UpdateMainLocationInfo()

    def OnWarzoneOccupationStateUpdated_Local(self):
        self.UpdateLocationInfo()

    def OnDynamicBountyUpdate_Local(self):
        self.UpdateDynamicResourceInfo()

    def UpdateEmanationLockInfo(self):
        lock_details = GateLockController.get_instance(get_gate_lock_messenger(sm.GetService('publicGatewaySvc'))).get_current_system_lock()
        self.emanationLockInfoContainer.Flush()
        self.emanationLockInfoContainer.display = False
        if lock_details is None:
            return
        self.emanationLockInfoContainer.display = True
        gateID = lock_details.gate_id
        gateName = cfg.evelocations.Get(gateID).locationName
        gateTypeID = self._GetStargateTypeID(gateID)
        if not gateTypeID:
            return
        gateLabelText = "<url=showinfo:%d//%d alt='%s'>%s</url>" % (gateTypeID,
         gateID,
         localization.GetByLabel('UI/Map/StarMap/EmanationLockMarkerTooltip', gate_name=gateName),
         localization.GetByLabel('UI/Common/ItemTypes/Gate', gate_name=gateName))
        spriteLayoutCont = Container(parent=self.emanationLockInfoContainer, name='detailsCont', align=uiconst.CENTERLEFT, pos=(0, 0, 40, 40))
        Sprite(parent=spriteLayoutCont, align=uiconst.CENTER, texturePath='res:/UI/Texture/eveicon/system_icons/link_16px.png', pos=(0, 0, 16, 16))
        gateLabel = EveLabelMedium(parent=self.emanationLockInfoContainer, text=gateLabelText, left=spriteLayoutCont.width + 4, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL)
        gateLabel.OnMouseDownWithUrl = self._on_mouse_down_with_url

    def _GetStargateTypeID(self, gateID):
        slimItem = sm.GetService('michelle').GetItem(gateID)
        if slimItem and slimItem.typeID:
            return slimItem.typeID
        systemInfo = cfg.mapSolarSystemContentCache.get(session.solarsystemid2, None)
        if not systemInfo:
            return
        gateInfo = systemInfo.stargates.get(gateID, None)
        if not gateInfo:
            return
        return gateInfo.typeID

    @threadutils.threaded
    def _on_mouse_down_with_url(self, url, *args):
        try:
            parsed = evelink.parse_show_info_url(url)
        except Exception:
            log.LogWarn('Failed to parse URL')
            return

        if parsed.item_id is None or not idCheckers.IsStargate(parsed.item_id):
            return
        GetMenuService().TryExpandActionMenu(itemID=parsed.item_id, clickedObject=self, typeID=parsed.type_id)

    def OnEmanationLockUpdated(self, lock_details):
        self.UpdateEmanationLockInfo()
