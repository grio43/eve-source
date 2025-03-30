#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\activeitem.py
from collections import OrderedDict
import blue
import telemetry
import carbonui.const as uiconst
import eveformat.client
import evetypes
import localization
import structures
import uthread
import utillib
from brennivin import itertoolsext
from carbon.common.script.util.format import FmtDate, FmtDist
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import fontconst, TextColor
from carbonui.control.contextMenu.menuConst import DISABLED_ENTRY0
from carbonui.control.contextMenu.menuEntryData import MenuEntryData
from carbonui.window.widget import WidgetWindow
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from eve.client.script.parklife import states as state
from eve.client.script.ui.control import eveIcon, eveLabel
from eve.client.script.ui.inflight import actionPanelDefaults
from eve.client.script.ui.inflight.selectedItemConst import ICON_ID_AND_CMD_BY_ACTIONID, RESET_ACTIONS
from eve.client.script.ui.services import menuAction
from eve.client.script.ui.services.menuSvcExtras.movementFunctions import GetDefaultWarpToLabel
from eve.client.script.ui.shared import killRights
from eve.client.script.ui.shared.pointerTool import pointerToolConst
from eve.client.script.ui.util import uix
from eve.common.lib import appConst as const
from eve.common.script.sys import idCheckers
from eve.common.script.util import eveFormat
from eveservices.menu import GetMenuService, StartMenuService
from menu import MenuLabel
from npcs.client.components.entity_bounty import get_entity_bounty
from spacecomponents.client.components import cargobay
from spacecomponents.common.helper import HasCargoBayComponent
from spacecomponents.common.helper import HasItemTrader
from uihider import UiHiderMixin

class ActiveItem(UiHiderMixin, WidgetWindow):
    __guid__ = 'form.ActiveItem'
    uniqueUiName = pointerToolConst.UNIQUE_NAME_SELECTED_ITEM_VIEW
    __notifyevents__ = ['OnDronesSelected',
     'ProcessSessionChange',
     'OnStateChange',
     'DoBallRemove',
     'OnDistSettingsChange',
     'OnPlanetViewChanged',
     'DoBallsRemove',
     'OnActiveTrackingChange']
    default_minSize = (256, 100)
    default_windowID = 'selecteditemview'
    default_open = True
    default_isKillable = False
    default_captionLabelPath = 'UI/Inflight/ActiveItem/SelectedItem'

    @staticmethod
    def default_left(*args):
        return actionPanelDefaults.GetActiveItemLeft()

    @staticmethod
    def default_top(*args):
        return actionPanelDefaults.GetActiveItemTop()

    @staticmethod
    def default_width():
        return actionPanelDefaults.GetActiveItemWidth()

    @staticmethod
    def default_height():
        return actionPanelDefaults.GetActiveItemHeight()

    def ApplyAttributes(self, attributes):
        super(ActiveItem, self).ApplyAttributes(attributes)
        panelname = attributes.panelname
        self.scope = uiconst.SCOPE_INFLIGHT
        self.canAnchorToOthers = 0
        self.lastActionSerial = None
        self.lastSessionChange = None
        self.laseUpdateWidth = None
        self.lastIcon = None
        self.lastBountyCheck = None
        self.bounty = None
        self.sr.actions = None
        self.sr.updateTimer = None
        self.itemIDs = []
        self.panelname = panelname
        self.lastActionDist = None
        self.lastCloakingStatus = False
        self.sr.noSelectedHint = None
        self.sr.blink = None
        self.UpdateActions()
        self._ConstructGroupData()
        if self.destroyed:
            return
        self.sr.toparea = Container(name='toparea', align=uiconst.TOTOP, parent=self.sr.main, height=36)
        self.sr.utilMenuArea = Container(name='utilMenuArea', align=uiconst.TORIGHT, parent=self.sr.toparea, width=20)
        self.utilMenu = killRights.KillRightsUtilMenu(menuAlign=uiconst.TOPRIGHT, parent=self.sr.utilMenuArea, align=uiconst.TOPRIGHT)
        self.sr.utilMenuArea.display = False
        self.sr.actions = Container(name='actions', align=uiconst.TOTOP, parent=self.sr.main, left=0, top=0)
        self.sr.actions.isTabStop = 1
        self.sr.iconpar = Container(name='iconpar', align=uiconst.TOPLEFT, parent=self.sr.toparea, width=32, height=32, left=1, top=2, state=uiconst.UI_HIDDEN)
        self.sr.icon = eveIcon.Icon(parent=self.sr.iconpar, align=uiconst.TOALL)
        self.sr.icon.OnClick = (self.ShowInfo, self.sr.icon)
        self.sr.icon.GetMenu = (self.GetIconMenu, self.sr.icon)
        self.sr.icon.GetDragData = self.GetShipDragData
        self.sr.chariconpar = Container(name='chariconpar', align=uiconst.TOPLEFT, parent=self.sr.toparea, width=32, height=32, left=37, top=2, state=uiconst.UI_HIDDEN)
        self.sr.charicon = eveIcon.Icon(parent=self.sr.chariconpar, align=uiconst.TOALL)
        self.sr.charicon.GetDragData = self.GetCharDragData
        self.sr.charicon.OnClick = (self.ShowInfo, self.sr.charicon)
        self.sr.pushCont = Container(name='push', width=39, parent=self.sr.toparea, align=uiconst.TOLEFT)
        self.sr.text = eveLabel.EveLabelSmall(text='', parent=self.sr.toparea, align=uiconst.TOTOP, left=const.defaultPadding, top=const.defaultPadding, state=uiconst.UI_NORMAL)
        self.inited = 1
        self.bountySvc = sm.GetService('bountySvc')
        selected = None
        stateSvc = sm.GetServiceIfRunning('stateSvc')
        if stateSvc:
            selected = stateSvc.GetExclState(state.selected)
        if selected:
            self.OnMultiSelect([selected])
        else:
            self.UpdateAll()

    def _ConstructGroupData(self):
        self.postorder = ['UI/Inflight/OrbitObject',
         'UI/Inflight/Submenus/KeepAtRange',
         ('UI/Inflight/LockTarget', 'UI/Inflight/UnlockTarget'),
         ('UI/Inflight/LookAtObject', 'UI/Inflight/ResetCamera'),
         'UI/Inflight/SetAsCameraInterest',
         'UI/Commands/ShowInfo']
        self.typeActions = {const.typeUpwellSmallStargate: ['UI/Inflight/JumpUsingBridge', 'UI/Inflight/BoardStructure', 'UI/Inflight/AccessHangarTransfer']}
        for typeID in structures.FLEX_STRUCTURE_TYPES:
            if typeID not in self.typeActions:
                self.typeActions[typeID] = []
            self.typeActions[typeID].extend(['UI/Inflight/BoardStructure', 'UI/Inflight/AccessHangarTransfer'])

        self.groups = {const.groupStation: ['UI/Inflight/DockInStation'],
         const.groupWreck: ['UI/Commands/OpenCargo'],
         const.groupCargoContainer: ['UI/Commands/OpenCargo'],
         const.groupMissionContainer: ['UI/Commands/OpenCargo'],
         const.groupSecureCargoContainer: ['UI/Commands/OpenCargo'],
         const.groupAuditLogSecureContainer: ['UI/Commands/OpenCargo'],
         const.groupFreightContainer: ['UI/Commands/OpenCargo'],
         const.groupSpawnContainer: ['UI/Commands/OpenCargo'],
         const.groupSpewContainer: ['UI/Commands/OpenCargo'],
         const.groupDeadspaceOverseersBelongings: ['UI/Commands/OpenCargo'],
         const.groupPlanetaryCustomsOffices: ['UI/PI/Common/AccessCustomOffice'],
         const.groupOrbitalConstructionPlatforms: ['UI/DustLink/OpenUpgradeHold'],
         const.groupMoon: ['UI/Inflight/WarpToMoonMiningPoint'],
         const.groupReprocessingArray: ['UI/Inflight/POS/AccessPOSRefinery'],
         const.groupCompressionArray: ['UI/Inflight/POS/AccessPOSCompression'],
         const.groupMobileReactor: ['UI/Inflight/POS/AccessPOSStorage'],
         const.groupControlTower: ['UI/Inflight/POS/AccessPOSFuelBay', 'UI/Inflight/POS/AccessPOSStrontiumBay'],
         const.groupSilo: ['UI/Inflight/POS/AccessPOSStorage'],
         const.groupAssemblyArray: ['UI/Inflight/POS/AccessPOSStorage'],
         const.groupMobileLaboratory: ['UI/Inflight/POS/AccessPOSStorage'],
         const.groupCorporateHangarArray: ['UI/Inflight/POS/AccessPOSStorage'],
         const.groupPersonalHangar: ['UI/Inflight/POS/AccessPOSStorage'],
         const.groupMobileMissileSentry: ['UI/Inflight/POS/AccessPOSAmmo'],
         const.groupMobileHybridSentry: ['UI/Inflight/POS/AccessPOSAmmo'],
         const.groupMobileProjectileSentry: ['UI/Inflight/POS/AccessPOSAmmo'],
         const.groupMobileLaserSentry: ['UI/Inflight/POS/AccessPOSCrystalStorage'],
         const.groupShipMaintenanceArray: ['UI/Inflight/POS/AccessPOSVessels'],
         const.groupStargate: ['UI/Inflight/Jump'],
         const.groupWormhole: ['UI/Inflight/EnterWormhole'],
         const.groupWarpGate: ['UI/Inflight/ActivateGate'],
         const.groupAbyssalTraces: ['UI/Inflight/ActivateGate'],
         const.groupBillboard: ['UI/Commands/ReadNews'],
         const.groupAgentsinSpace: ['UI/Chat/StartConversation'],
         const.groupDestructibleAgentsInSpace: ['UI/Chat/StartConversation'],
         const.groupMiningDrone: ['UI/Drones/MineWithDrone', 'UI/Drones/ReturnDroneAndOrbit', ('UI/Drones/LaunchDrones', 'UI/Drones/ReturnDroneToBay', 'UI/Drones/ScoopDroneToBay')],
         const.groupSalvageDrone: ['UI/Drones/Salvage', 'UI/Drones/ReturnDroneAndOrbit', ('UI/Drones/LaunchDrones', 'UI/Drones/ReturnDroneToBay', 'UI/Drones/ScoopDroneToBay')]}
        structureOptions = ['UI/Inflight/DockInStation', 'UI/Inflight/AccessHangarTransfer']
        self.categories = {const.categoryShip: ['UI/Inflight/BoardShip'],
         const.categoryStructure: structureOptions,
         const.categoryDrone: ['UI/Drones/EngageTarget', 'UI/Drones/ReturnDroneAndOrbit', ('UI/Drones/LaunchDrones', 'UI/Drones/ReturnDroneToBay', 'UI/Drones/ScoopDroneToBay')]}

    def UpdateActions(self):
        self.actions = ICON_ID_AND_CMD_BY_ACTIONID.copy()
        self.subMenus = ['UI/Inflight/MoonMiningPoint']

    def Blink(self, on_off = 1):
        if on_off and self.sr.blink is None:
            self.sr.blink = Fill(parent=self.sr.top, padding=(1, 1, 1, 1), color=(1.0, 1.0, 1.0, 0.25))
        if on_off:
            sm.GetService('ui').BlinkSpriteA(self.sr.blink, 0.25, 500, None, passColor=0)
        elif self.sr.blink:
            sm.GetService('ui').StopBlink(self.sr.blink)
            b = self.sr.blink
            self.sr.blink = None
            b.Close()

    def BlinkBtn(self, key):
        for btn in self.sr.actions.children:
            if btn.name.replace(' ', '').lower() == key.replace(' ', '').lower():
                sm.GetService('ui').BlinkSpriteA(btn.children[0], 1.0, 500, None, passColor=0)
            else:
                sm.GetService('ui').StopBlink(btn.children[0])

    def OnResizeUpdate(self, *args):
        self.CheckActions(forceSizeUpdate=1, ignoreScaling=1)

    def OnActiveTrackingChange(self, isActivelyTracking):
        self.AdjustUIToActiveTrackingStatus(isActivelyTracking)

    def AdjustUIToActiveTrackingStatus(self, isTracking):
        caption = localization.GetByLabel('UI/Inflight/ActiveItem/SelectedItem')
        if isTracking:
            caption += ' - ' + localization.GetByLabel('UI/Inflight/ActiveItem/Tracking')
        self.SetCaption(caption)

    @telemetry.ZONE_METHOD
    def CheckActions(self, forceSizeUpdate = 0, ignoreScaling = 0):
        if self.destroyed or not self.sr.actions:
            return
        self.sr.toparea.height = max(40, self.sr.text.textheight + self.sr.text.top * 2)
        scaling = getattr(self, 'scaling', 0) if ignoreScaling == 0 else 0
        if forceSizeUpdate and not scaling and self.ImVisible():
            l, t, w, h = self.GetAbsolute()
            al, at = self.sr.actions.GetAbsolutePosition()
            maxHeight = t + h - at - 8
            self.LayoutButtons(self.sr.actions, uiconst.UI_PICKCHILDREN, maxHeight)
            gl, gt, gr, gb = self.GetGroupRect(self.sr.actions.children)
            diff = gb - (t + h - 6)
            if diff > 0:
                self.SetHeight_PushOrPullWindowsBelow(self.height + diff)

    @telemetry.ZONE_METHOD
    def LayoutButtons(self, parent, state = None, maxHeight = None):
        if parent is None:
            return
        l, t, w, h = parent.GetAbsolute()
        colwidth = 33
        if w <= colwidth:
            return
        perRow = w / colwidth
        isSmall = len(parent.children) / float(perRow) > 2.0
        iconSize = 24 if isSmall else 32
        if maxHeight and iconSize > maxHeight:
            iconSize = 24
        if len(parent.children) * (iconSize + 1) + 1 > w:
            iconSize = 24
        left = 1
        top = 0
        parent.height = iconSize + 1
        for icon in parent.children:
            if l + left + iconSize + 1 >= l + w:
                left = 1
                top += iconSize + 1
                parent.height += iconSize + 1
            icon.left = left
            icon.top = top
            icon.width = iconSize
            icon.height = iconSize
            if state is not None:
                icon.state = state
            left += iconSize + 1

    def _OnClose(self, *args):
        self.sr.updateTimer = None

    def ProcessSessionChange(self, isRemote, session, change):
        self.lastActionSerial = None
        self.lastActionDist = None
        self.lastCloakingStatus = None
        self.lastSessionChange = blue.os.GetWallclockTime()

    def OnDronesSelected(self, itemIDs):
        self.OnMultiSelect(itemIDs)

    def OnMultiSelect(self, itemIDs):
        self.itemIDs = itemIDs
        self.lastActionSerial = None
        self.lastActionDist = None
        self.lastBountyCheck = None
        self.bounty = None
        if self.ImVisible():
            uthread.pool('ActiveItem::UpdateAll', self.UpdateAll, 1)

    def OnStateChange(self, itemID, flag, true, *args):
        if itemID != eve.session.shipid and not self.destroyed:
            uthread.new(self._OnStateChange, itemID, flag, true)

    @telemetry.ZONE_METHOD
    def _OnStateChange(self, itemID, flag, true):
        if flag == state.selected and true:
            self.OnMultiSelect([itemID])
        if itemID in self.itemIDs and flag not in (state.selected, state.mouseOver):
            self.lastActionSerial = None
            self.lastActionDist = None
            self.UpdateAll()

    def OnDistSettingsChange(self):
        uthread.new(self._OnDistSettingsChange)

    @telemetry.ZONE_METHOD
    def _OnDistSettingsChange(self):
        self.ResetLastActionAndCloakingAndUpdateAll()

    def ResetLastActionAndCloakingAndUpdateAll(self):
        self.lastActionSerial = None
        self.lastCloakingStatus = None
        self.UpdateAll(1)

    def TryGetInvItem(self, itemID):
        if eve.session.shipid is None:
            return
        ship = sm.GetService('invCache').GetInventoryFromId(eve.session.shipid)
        if ship:
            for invItem in ship.List():
                if invItem.itemID == itemID:
                    return invItem

    def GetItem(self, itemID):
        item = uix.GetBallparkRecord(itemID)
        if not item:
            item = self.TryGetInvItem(itemID)
        return item

    def Load(self, itemID):
        pass

    def OnTabSelect(self, *args):
        if not getattr(self, 'inited', 0):
            return
        self.ResetLastActionAndCloakingAndUpdateAll()

    def OnExpanded(self, *args):
        if not getattr(self, 'inited', 0):
            return
        super(ActiveItem, self).OnExpanded(*args)
        self.ResetLastActionAndCloakingAndUpdateAll()

    def OnEndMaximize_(self, *args):
        if not getattr(self, 'inited', 0):
            return
        self.ResetLastActionAndCloakingAndUpdateAll()

    def FadeInSelf(self):
        self.opacity = 0.001
        super(ActiveItem, self).FadeInSelf()
        if not getattr(self, 'inited', 0):
            return
        self.ResetLastActionAndCloakingAndUpdateAll()

    def ShowNoSelectedHint(self, hint = None):
        if self.sr.noSelectedHint is None and hint:
            self.sr.noSelectedHint = eveLabel.EveCaptionMedium(text=hint, parent=self.sr.main, align=uiconst.RELATIVE, left=16, top=18, width=256, color=TextColor.SECONDARY)
        elif self.sr.noSelectedHint:
            if hint:
                self.sr.noSelectedHint.text = hint
                self.sr.noSelectedHint.state = uiconst.UI_DISABLED
            else:
                self.sr.noSelectedHint.state = uiconst.UI_HIDDEN

    def FlushContent(self):
        self.SetText('')
        self.ShowNoSelectedHint(localization.GetByLabel('UI/Inflight/ActiveItem/NoObjectSelected'))
        self.sr.actions.Flush()
        self.sr.iconpar.state = uiconst.UI_HIDDEN
        self.sr.chariconpar.state = uiconst.UI_HIDDEN

    @telemetry.ZONE_METHOD
    def UpdateAll(self, updateActions = 0):
        if not self or self.destroyed:
            return
        if eve.session.shipid in self.itemIDs:
            self.itemIDs.remove(eve.session.shipid)
        bp = sm.GetService('michelle').GetBallpark()
        if not self.ImVisible() or not bp or not self.itemIDs:
            self.sr.updateTimer = None
            self.FlushContent()
            return
        goForSlim = 1
        slimItems = []
        invItems = []
        fleetMember = None
        for itemID in self.itemIDs:
            blue.pyos.BeNice()
            if sm.GetService('fleet').IsMember(itemID):
                fleetMember = cfg.eveowners.Get(itemID)
                break
            slimItem = None
            if goForSlim:
                slimItem = uix.GetBallparkRecord(itemID)
                if slimItem:
                    slimItems.append(slimItem)
            if not slimItem:
                invItem = self.TryGetInvItem(itemID)
                if invItem:
                    invItems.append(invItem)
                    goForSlim = 0

        if not slimItems and not invItems and not fleetMember:
            self.itemIDs = []
            self.lastActionSerial = None
            self.lastActionDist = None
            self.FlushContent()
            return
        if not self or self.destroyed:
            return
        text = ''
        blue.pyos.BeNice()
        updateActions = updateActions or 0
        typeID = None
        fleetSlim = None
        if fleetMember:
            multi = 1
            text = fleetMember.name
            typeID = fleetMember.typeID
            fleetSlim = self.GetSlimItemForCharID(fleetMember.id)
            blue.pyos.BeNice()
        elif invItems:
            text = uix.GetItemName(invItems[0])
            typeID = invItems[0].typeID
            multi = len(invItems)
            blue.pyos.BeNice()
        elif slimItems:
            text = uix.GetSlimItemName(slimItems[0])
            typeID = slimItems[0].typeID
            multi = len(slimItems)
            if multi == 1:
                slimItem = slimItems[0]
                itemID = slimItem.itemID
                ball = bp.GetBall(itemID)
                if not ball:
                    self.itemIDs = []
                    self.sr.updateTimer = None
                    self.FlushContent()
                    return
                if slimItem.groupID == const.groupStargate:
                    text = u'{text} ({security_status})'.format(text=text, security_status=eveformat.solar_system_security_status(slimItem.jumps[0].locationID))
                dist = ball.surfaceDist
                if dist is not None:
                    md = None
                    myball = bp.GetBall(eve.session.shipid)
                    if myball:
                        md = myball.mode
                        if self.lastCloakingStatus is None or self.lastCloakingStatus != myball.isCloaked:
                            updateActions = 1
                        self.lastCloakingStatus = myball.isCloaked
                    text += '<br>' + localization.GetByLabel('UI/Inflight/ActiveItem/SelectedItemDistance', distToItem=FmtDist(dist, maxdemicals=1))
                    if not self.lastActionDist or md != self.lastActionDist[1] or self.CheckDistanceUpdate(self.lastActionDist[0], dist):
                        self.lastActionDist = (dist, md)
                        updateActions = 1
                sec = slimItem.securityStatus
                if sec:
                    text += '<br>' + localization.GetByLabel('UI/Inflight/ActiveItem/SelectedItemSecurity', secStatus=sec)
                if slimItem.categoryID == const.categoryStructure:
                    timerText = self.GetStructureTimerText(slimItem)
                    if timerText:
                        text += timerText
                        updateActions = 1
            blue.pyos.BeNice()
        corpID = None
        charID = None
        categoryID = None
        bountyItemID = None
        bountyTypeID = None
        bountySlim = None
        displayUtilMenu = False
        if multi > 1:
            text += '<br>' + localization.GetByLabel('UI/Inflight/ActiveItem/MultipleItems', itemCount=multi)
            blue.pyos.BeNice()
        elif multi == 1:
            if slimItems:
                slim = slimItems[0]
                if slim.categoryID == const.categoryShip:
                    if idCheckers.IsCharacter(slim.charID):
                        charID = slim.charID
                        categoryID = slim.categoryID
                if slim.categoryID == const.categoryEntity:
                    bountyTypeID = slim.typeID
                    bountySlim = slim
                elif slim.charID:
                    bountyItemID = slim.charID
                    bountySlim = slim
                killRightID, price = self.bountySvc.GetBestKillRight(slim.charID)
                self.utilMenu.UpdateKillRightInfo(killRightID, price, slim.charID, slim.itemID)
                stateSvc = sm.GetService('stateSvc')
                if killRightID is not None and not (stateSvc.CheckSuspect(slim) or stateSvc.CheckCriminal(slim)) and slim.categoryID != const.categoryStructure:
                    displayUtilMenu = True
            blue.pyos.BeNice()
        self.sr.utilMenuArea.display = displayUtilMenu
        self.utilMenu.display = displayUtilMenu
        if self.lastIcon != (typeID, itemID, charID):
            uthread.pool('ActiveItem::GetIcon', self.GetIcon, typeID, itemID, charID, corpID, categoryID)
            self.lastIcon = (typeID, itemID, charID)
        else:
            self.sr.iconpar.state = uiconst.UI_PICKCHILDREN
            if categoryID == const.categoryShip and charID:
                self.sr.chariconpar.state = uiconst.UI_PICKCHILDREN
        if (bountyItemID, bountyTypeID) != self.lastBountyCheck:
            bounty, bountyHint, reducedBountyIndication = self.CheckBounty(bountyTypeID, bountySlim)
            blue.pyos.BeNice()
            if bounty:
                self.bounty = localization.GetByLabel('UI/Common/BountyAmount', bountyAmount=eveFormat.FmtISK(bounty, 0))
            else:
                self.bounty = None
            self.lastBountyCheck = (bountyItemID, bountyTypeID)
            self.lastBountyInfo = (bountyHint, reducedBountyIndication)
        else:
            bountyHint, reducedBountyIndication = self.lastBountyInfo
        if self.bounty:
            text += '<br>'
            text += self.bounty
        if reducedBountyIndication:
            text += reducedBountyIndication
        if updateActions:
            self.ReloadActions(slimItems, invItems, fleetMember, fleetSlim)
        else:
            self.CheckActions(1)
        self.SetText(text, bountyHint)
        self.ShowNoSelectedHint()
        blue.pyos.BeNice()
        self.laseUpdateWidth = self.absoluteRight - self.absoluteLeft
        if not self.sr.updateTimer and not invItems:
            self.sr.updateTimer = AutoTimer(500, self.UpdateAll)

    def GetStructureTimerText(self, slimItem):
        timerText = ''
        isVulnerable = structures.STATE_VULNERABILITY.get(slimItem.state, None)
        if isVulnerable is not False:
            return timerText
        if slimItem.timer:
            start, end, paused = slimItem.timer
            if paused:
                end = end + blue.os.GetWallclockTime() - paused
            stateText = localization.GetByLabel(structures.STATE_LABELS[slimItem.state])
            label = localization.GetByLabel('UI/Inflight/ActiveItem/InStateUntil', structureState=stateText, timestamp=FmtDate(end))
            timerText = '<br>%s' % label
        return timerText

    @telemetry.ZONE_METHOD
    def DoBallsRemove(self, pythonBalls, isRelease):
        for ball, slimItem, terminal in pythonBalls:
            self.DoBallRemove(ball, slimItem, terminal)

    def DoBallRemove(self, ball, slimItem, terminal):
        if self.ImVisible() and ball and ball.id in self.itemIDs:
            uthread.pool('ActiveItem::UpdateAll', self.UpdateAll, 1)

    def SetText(self, text, hint = None):
        if text != self.sr.text.text:
            self.sr.text.text = text
            self.sr.text.hint = hint
            self.CheckActions(1)

    def GetIcon(self, typeID, itemID, charID, corpID, categoryID):
        self.sr.icon.LoadIconByTypeID(typeID, itemID=itemID, ignoreSize=True)
        self.sr.icon.typeID = typeID
        self.sr.icon.itemID = itemID
        self.sr.icon.categoryID = categoryID
        self.sr.iconpar.state = uiconst.UI_PICKCHILDREN
        self.sr.chariconpar.state = uiconst.UI_HIDDEN
        self.sr.pushCont.width = 39
        if categoryID == const.categoryShip and charID:
            typeID = cfg.eveowners.Get(charID).typeID
            self.sr.charicon.LoadIconByTypeID(typeID, itemID=charID, ignoreSize=True)
            self.sr.charicon.typeID = typeID
            self.sr.charicon.itemID = charID
            self.sr.pushCont.width = 75
            self.sr.chariconpar.state = uiconst.UI_PICKCHILDREN

    def GetShipDragData(self):
        categoryID = self.sr.icon.categoryID
        if categoryID != const.categoryShip:
            return []
        typeID = self.sr.icon.typeID
        fakeNode = utillib.KeyVal()
        fakeNode.__guid__ = 'listentry.Item'
        fakeNode.typeID = typeID
        fakeNode.itemID = self.sr.icon.itemID
        label = evetypes.GetName(typeID)
        charID = self.sr.charicon.itemID
        if charID:
            label = '%s (%s)' % (cfg.eveowners.Get(charID).name, label)
        fakeNode.genericDisplayLabel = label
        return [fakeNode]

    def GetCharDragData(self, *args):
        charID = self.sr.charicon.itemID
        if not charID:
            return []
        fakeNode = utillib.KeyVal()
        fakeNode.charID = charID
        fakeNode.typeID = self.sr.charicon.typeID
        fakeNode.itemID = charID
        fakeNode.info = cfg.eveowners.Get(charID)
        fakeNode.__guid__ = 'listentry.User'
        return [fakeNode]

    def CheckBounty(self, bountyTypeID, slimItem):
        bounty = None
        bountyHint = None
        reducedBountyIndication = None
        if bountyTypeID:
            bountyAmount = get_entity_bounty(bountyTypeID, slimItem.itemID)
            if bountyAmount:
                bounty, bountyHint, reducedBountyIndication = self.GetNpcBounty(bountyAmount)
        elif slimItem:
            if self.bountySvc.CanHaveBounty(slimItem):
                bounty = self.bountySvc.GetBounty(slimItem.charID, slimItem.corpID, slimItem.allianceID)
        return (bounty, bountyHint, reducedBountyIndication)

    def GetNpcBounty(self, bountyAmount):
        return (bountyAmount, None, None)

    def GetSlimItemForCharID(self, charID):
        ballpark = sm.GetService('michelle').GetBallpark()
        if ballpark:
            for itemID, rec in ballpark.slimItems.iteritems():
                if rec.charID == charID:
                    return rec

    def ShowInfo(self, btn, *args):
        if btn and btn.typeID:
            sm.GetService('info').ShowInfo(btn.typeID, btn.itemID)

    def GetIconMenu(self, btn, *args):
        if btn and btn.typeID:
            return GetMenuService().GetMenuFromItemIDTypeID(getattr(btn, 'itemID', None), btn.typeID)

    def CheckDistanceUpdate(self, lastdist, dist):
        diff = abs(lastdist - dist)
        if not diff:
            return False
        elif dist:
            return bool(diff / dist > 0.01)
        else:
            return bool(lastdist != dist)

    def ImVisible(self):
        return bool(not self.IsCollapsed() and not self.IsMinimized() and self.opacity > 0 and self.display)

    @telemetry.ZONE_METHOD
    def ReloadActions(self, slimItems, invItems, fleetMember, fleetSlim):
        if not self or self.destroyed:
            return
        if not self.ImVisible():
            self.sr.updateTimer = None
            return
        itemIDsAtStart = self.itemIDs[:]
        actions = []
        if invItems:
            data = [ (invItem, 0, None) for invItem in invItems ]
            actions = StartMenuService().InvItemMenu(data)
        elif slimItems:
            if len(slimItems) == 1:
                actions = GetMenuService().UnmergedCelestialMenu(slimItems[0])
            else:
                actions = GetMenuService().CelestialMenu([ (slimItem.itemID,
                 None,
                 slimItem,
                 None,
                 None) for slimItem in slimItems ])
        elif fleetSlim:
            actions = GetMenuService().CelestialMenu(fleetSlim.itemID, slimItem=fleetSlim)
        elif fleetMember:
            actions = GetMenuService().CharacterMenu(fleetMember.id)
        if itemIDsAtStart != self.itemIDs:
            return
        reasonsWhyNotAvailable = getattr(actions, 'reasonsWhyNotAvailable', {})
        warptoLabel = GetDefaultWarpToLabel()[0]
        if not self or self.destroyed:
            return
        allActions = self.GetAllActionsFromMenus(actions)
        serial = ''
        valid = {}
        for each in allActions:
            name = self._FindNameForAction(each)
            if name in self.actions:
                valid[name] = each
                if type(each[1]) not in (str, unicode):
                    serial += '%s_' % name

        blue.pyos.BeNice()
        if serial != self.lastActionSerial:
            if self.absoluteLeft == 0:
                blue.pyos.synchro.Yield()
            if self.destroyed:
                return
            self.sr.actions.Flush()
            self.sr.actions.height = 0
            typeID = None
            groupID = None
            categoryID = None
            if slimItems:
                typeID = slimItems[0].typeID
                groupID = slimItems[0].groupID
                categoryID = slimItems[0].categoryID
            elif invItems:
                typeID = invItems[0].typeID
                groupID = invItems[0].groupID
                categoryID = invItems[0].categoryID
            isAlignDisabled = type(valid.get('UI/Inflight/AlignTo', ('', ''))[1]) in (str, unicode)
            if isAlignDisabled:
                approachLabelPath = 'UI/Inflight/ApproachObject'
            else:
                approachLabelPath = 'UI/Inflight/AlignTo'
            order = [approachLabelPath, warptoLabel]
            if typeID and typeID in self.typeActions:
                order += self.typeActions[typeID]
            elif groupID and groupID in self.groups:
                order += self.groups[groupID]
            elif categoryID and categoryID in self.categories:
                order += self.categories[categoryID]
            item = self.ChooseItem(slimItems, invItems)
            if item:
                if HasCargoBayComponent(typeID) and not HasItemTrader(typeID):
                    if cargobay.IsAccessibleByCharacter(item, session.charid):
                        order.append('UI/Commands/OpenCargo')
                if HasItemTrader(typeID):
                    order.append('UI/Inflight/SpaceComponents/ItemTrader/Access')
            order = itertoolsext.remove_duplicates_and_preserve_order(order)
            order += self.postorder
            if groupID == const.groupPlanet:
                order += [('UI/PI/Common/ViewInPlanetMode', 'UI/PI/Common/ExitPlanetMode')]
            for actionName in order:
                if actionName is None:
                    continue
                if isinstance(actionName, tuple):
                    action = None
                    for each in actionName:
                        tryaction = valid.get(each, None)
                        if tryaction and type(tryaction[1]) not in (str, unicode):
                            actionName = each
                            action = tryaction
                            break

                    if action is None:
                        actionName = actionName[0]
                        if actionName in valid:
                            action = valid.get(actionName)
                        elif actionName in reasonsWhyNotAvailable:
                            action = (actionName, reasonsWhyNotAvailable.get(actionName))
                        else:
                            action = (actionName, localization.GetByLabel('UI/Menusvc/MenuHints/NoReasonGiven'))
                elif actionName in valid:
                    action = valid.get(actionName)
                elif actionName in reasonsWhyNotAvailable:
                    action = (actionName, reasonsWhyNotAvailable.get(actionName))
                else:
                    action = (actionName, localization.GetByLabel('UI/Menusvc/MenuHints/NoReasonGiven'))
                disabled = type(action[1]) in (str, unicode)
                if isinstance(action[0], MenuLabel):
                    actionID = action[0][0]
                else:
                    actionID = action[0]
                par = Container(parent=self.sr.actions, align=uiconst.TOPLEFT, width=32, height=32, state=uiconst.UI_HIDDEN)
                actionObject = self.actions[actionID]
                par.name = actionObject.uniqueUiName or actionID
                cmdName = actionObject.cmdName or ''
                icon = menuAction.Action(icon=actionObject.iconPath, parent=par, align=uiconst.TOALL, disabled=disabled)
                icon.uniqueUiName = actionObject.uniqueUiName
                icon.actionID = actionID
                icon.action = action
                icon.itemIDs = self.itemIDs[:]
                icon.cmdName = cmdName
                if disabled:
                    icon.opacity = 0.5
                if actionID in RESET_ACTIONS:
                    eveIcon.Icon(icon='ui_44_32_8', parent=par, pos=(1, 1, 0, 0), align=uiconst.TOALL, state=uiconst.UI_DISABLED, idx=0)

            self.lastActionSerial = serial
        self.CheckActions(1)

    def GetAllActionsFromMenus(self, actions):
        allActionsDict = OrderedDict()
        subMenuActions = []
        for each in actions:
            if not each or self._IsDisabledEntry(each):
                continue
            name = self._FindNameForAction(each)
            allActionsDict[name] = each
            if name in self.subMenus:
                for eachSubOption in each[1]:
                    subMenuActions.append(eachSubOption)

        for eachSubOption in subMenuActions:
            name = self._FindNameForAction(eachSubOption)
            if name not in allActionsDict:
                allActionsDict[name] = eachSubOption

        allActions = allActionsDict.values()
        return allActions

    def _IsDisabledEntry(self, each):
        if isinstance(each, MenuEntryData):
            return each.IsEnabled()
        else:
            return each[1] == DISABLED_ENTRY0

    def _FindNameForAction(self, each):
        if isinstance(each[0], tuple):
            name = each[0][0]
        else:
            name = each[0]
        return name

    def ChooseItem(self, slimItems, invItems):
        if slimItems:
            return slimItems[0]
        if invItems:
            return invItems[0]

    def OnPlanetViewChanged(self, newPlanetID, oldPlanetID):
        for planetID in (newPlanetID, oldPlanetID):
            if planetID in self.itemIDs:
                self.OnMultiSelect(self.itemIDs)
