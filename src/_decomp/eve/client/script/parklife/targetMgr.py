#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\targetMgr.py
import sys
import blue
import localization
import telemetry
import uthread
from carbon.common.script.sys.service import Service
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.line import Line
from carbonui.uicore import uicore
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.parklife import states as state
from eve.client.script.parklife.targetUtils import get_closest_entity_target
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.inflight.activeitem import ActiveItem
from eve.client.script.ui.inflight.bracketsAndTargets.targetInBar import TargetInBar
from eve.client.script.ui.inflight.bracketsAndTargets.targetInBarFighter import TargetInBarFighter
from eve.client.script.ui.inflight.selectedItemWnd import SelectedItemWnd
from eve.client.script.ui.shared.pointerTool import pointerToolConst as pConst
from eve.client.script.ui.util.uix import GetBallparkRecord
from eve.common.script.sys import eveSessions, idCheckers
from eve.client.script.ui.view import overlaySettings
from eve.client.script.ui.view.viewStateConst import ViewOverlay
from eveexceptions import UserError
from menu import MenuLabel
import eve.common.lib.appConst as const
MAX_TARGET_WIDTH = 110
AVG_TARGET_HEIGHT = 200
MIN_TARGET_HEIHT = 170
TARGET_PADDING = 10

class TargetMgr(Service):
    __guid__ = 'svc.target'
    __exportedcalls__ = {'LockTarget': [],
     'UnlockTarget': [],
     'ClearTargets': [],
     'GetActiveTargetID': [],
     'GetTargets': [],
     'GetTargeting': [],
     'StartLockTarget': [],
     'FailLockTarget': [],
     'CancelAddTarget': []}
    __notifyevents__ = ['OnTarget',
     'OnTargets',
     'OnTargetClear',
     'ProcessSessionChange',
     'OnSpecialFX',
     'DoBallsAdded',
     'DoBallRemove',
     'DoBallClear',
     'OnStateChange',
     'DoBallsRemove',
     'OnFleetStateChange']
    __dependencies__ = ['michelle',
     'godma',
     'settings',
     'stateSvc']
    __update_on_reload__ = 0

    def Run(self, memStream = None):
        super(TargetMgr, self).Run(memStream)
        self.viewMode = 'normal'
        self.preViewMode = None
        self.Reset()
        if eve.session.shipid and not eve.session.stationid:
            self.godma.GetStateManager().RefreshTargets()
        self.ownerToShipIDCache = {}
        self.deadShipsBeingRemoved = set()
        self.disableSpinnyReticule = False
        self.overrideBarHeight = None

    def Stop(self, stream):
        super(TargetMgr, self).Stop(stream)
        self.viewMode = 'normal'
        self.CheckViewMode()
        self.Reset()

    def PlaceOrigin(self):
        if self.origin is not None:
            return
        self.CreateOrigin()
        self.PositionOriginWithAnchors()
        self.UpdateOriginDirection()

    def CreateOrigin(self, *args):
        if not len(self.targetsByID):
            self.origin = None
            return
        par = uicore.layer.target
        origin = Container(name='targetOrigin', parent=par, align=uiconst.RELATIVE, width=16, height=16, state=uiconst.UI_NORMAL, uniqueUiName=pConst.UNIQUE_NAME_TARGET_ANCHOR)
        origin.OnMouseDown = (self.OnOriginMD, origin)
        origin.OnMouseUp = (self.OnOriginMU, origin)
        origin.GetMenu = self.GetOriginMenu
        origin.hint = localization.GetByLabel('UI/Inflight/TargetListAnchor/TargetListAnchorHint')
        origin.leftline = Line(parent=origin, align=uiconst.RELATIVE, width=4, height=1, left=-4, top=7, color=(1.0, 1.0, 1.0, 1.0))
        origin.topline = Line(parent=origin, align=uiconst.RELATIVE, width=1, height=4, left=7, top=-4, color=(1.0, 1.0, 1.0, 1.0))
        origin.rightline = Line(parent=origin, align=uiconst.RELATIVE, width=4, height=1, left=15, top=7, color=(1.0, 1.0, 1.0, 1.0))
        origin.bottomline = Line(parent=origin, align=uiconst.RELATIVE, width=1, height=4, left=7, top=15, color=(1.0, 1.0, 1.0, 1.0))
        origin.opacity = 0.75
        Icon(icon='ui_38_16_72', parent=origin, state=uiconst.UI_DISABLED)
        self.origin = origin
        if getattr(self, 'targetPar', None) is None or self.targetPar.destroyed:
            targetPar = Container(parent=uicore.layer.target, align=uiconst.TOALL)
            self.targetPar = targetPar
            self.targetPar.rows = []

    def PositionOriginWithAnchors(self):
        if not self.origin or self.origin.destroyed:
            self.CreateOrigin()
        if not self.origin:
            return
        origin = self.origin
        (cX, cY), (toLeft, toTop) = self.GetOriginPosition(getDirection=1)
        pl, pt, pw, ph = origin.parent.GetAbsolute()
        originAlign = self.GetOriginAlign(toLeft, toTop)
        origin.SetAlign(originAlign)
        if toLeft:
            origin.left = pw - cX - 8
        else:
            origin.left = cX - 8
        if toTop:
            origin.top = ph - cY - 8
        else:
            origin.top = cY - 8

    def GetOriginMenu(self):
        if settings.user.ui.Get('targetOriginLocked', 0):
            m = [(MenuLabel('UI/Inflight/TargetListAnchor/UnlockAnchor'), self.UnlockOrigin)]
        else:
            m = [(MenuLabel('UI/Inflight/TargetListAnchor/LockAnchor'), self.LockOrigin)]
        if settings.user.ui.Get('targetPositionLocked', 0):
            m += [(MenuLabel('UI/Inflight/TargetListAnchor/UnlockTargets'), self.ToggleLockTargetPosition)]
        else:
            m += [(MenuLabel('UI/Inflight/TargetListAnchor/LockTargets'), self.ToggleLockTargetPosition)]
        if settings.user.ui.Get('alignHorizontally', 1):
            m += [(MenuLabel('UI/Inflight/TargetListAnchor/ArrangeTargetsVertically'), self.ToggleAlignment)]
        else:
            m += [(MenuLabel('UI/Inflight/TargetListAnchor/ArrangeTargetsHorizontally'), self.ToggleAlignment)]
        if overlaySettings.IsFullscreenOverlayModeEnabled(ViewOverlay.Target):
            m += [(MenuLabel('/Carbon/UI/Controls/Window/DisableOverlayMode'), lambda : overlaySettings.DisableFullscreenOverlayMode(ViewOverlay.Target))]
        else:
            m += [(MenuLabel('/Carbon/UI/Controls/Window/EnableOverlayMode'), lambda : overlaySettings.EnableFullscreenOverlayMode(ViewOverlay.Target))]
        m += [(MenuLabel('UI/Commands/CmdUnlockTargetItems'), sm.GetService('cmd').CmdUnlockTargetItems)]
        return m

    def UnlockOrigin(self, *args):
        settings.user.ui.Set('targetOriginLocked', 0)

    def LockOrigin(self, *args):
        settings.user.ui.Set('targetOriginLocked', 1)

    def ToggleLockTargetPosition(self, *args):
        current = settings.user.ui.Get('targetPositionLocked', 0)
        settings.user.ui.Set('targetPositionLocked', not current)

    def ToggleAlignment(self, *args):
        current = settings.user.ui.Get('alignHorizontally', 1)
        settings.user.ui.Set('alignHorizontally', not current)
        self.ArrangeTargets()

    def GetTargetLayerAbsolutes(self):
        d = uicore.desktop
        wnd = uicore.layer.target
        if wnd and not wnd.state == uiconst.UI_HIDDEN:
            pl, pt, pw, ph = wnd.GetAbsolute()
        else:
            pl, pt, pw, ph = d.GetAbsolute()
        return (wnd,
         pl,
         pt,
         pw,
         ph)

    def GetOriginPosition(self, inPixels = 1, getDirection = 0):
        d = uicore.desktop
        wnd, pl, pt, pw, ph = self.GetTargetLayerAbsolutes()
        myPrefs = settings.user.ui.Get('targetOrigin', None)
        if myPrefs is None:
            selecteditem = SelectedItemWnd.GetIfOpen()
            if selecteditem and selecteditem.display and not selecteditem.IsMinimized():
                stack = getattr(selecteditem.sr, 'stack', None)
                if stack:
                    selecteditem = stack
                topAlignedWindows = selecteditem.FindConnectingWindows('top')
                left, top, width, height = selecteditem.GetGroupAbsolute(topAlignedWindows)
                dw = d.width
                dh = d.height
            else:
                left, top, width, height, dw, dh = SelectedItemWnd.GetRegisteredPositionAndSizeByClass()
            left -= 15
            portionalCY = top / float(dh)
            if left + width < d.width / 2:
                portionalCX = (left + width - pl) / float(pw)
            elif left >= d.width / 2:
                portionalCX = (left - pl) / float(pw)
            else:
                portionalCX = (d.width - 300) / float(dw)
                portionalCY = 16 / float(d.height)
        else:
            portionalCX, portionalCY = myPrefs
        if inPixels:
            ret = (int(portionalCX * pw), int(portionalCY * ph))
        else:
            ret = (portionalCX, portionalCY)
        if getDirection:
            return (ret, (bool(portionalCX > 0.5), bool(portionalCY > 0.5)))
        return ret

    def OnOriginMU(self, origin, btn, *args):
        if btn != 0 or settings.user.ui.Get('targetOriginLocked', 0):
            return
        if uicore.uilib.mouseOver == self.origin:
            par, tl, tt, tw, th = self.GetTargetLayerAbsolutes()
            origin.left = uicore.uilib.x - origin.grab[0]
            origin.top = uicore.uilib.y - origin.grab[1]
            origin.opacity = 0.75
            d = uicore.desktop
            l, t, w, h = origin.GetAbsolute()
            cX = l - tl + w / 2
            cY = t - tt + h / 2
            pcX = cX / float(tw)
            pcY = cY / float(th)
            settings.user.ui.Set('targetOrigin', (pcX, pcY))
        self.ArrangeTargets()
        sm.GetService('ui').ForceCursorUpdate()
        origin.dragging = 0
        uicore.uilib.UnclipCursor()
        origin.hint = localization.GetByLabel('UI/Inflight/TargetListAnchor/TargetListAnchorHint')

    def OnOriginMD(self, origin, btn, *args):
        if btn != 0 or settings.user.ui.Get('targetOriginLocked', 0):
            return
        origin.opacity = 1.0
        l, t, w, h = origin.GetAbsolute()
        pl, pt, pw, ph = origin.parent.GetAbsolute()
        origin.grab = [uicore.uilib.x - l, uicore.uilib.y - t]
        origin.dragging = 1
        origin.SetAlign(uiconst.ABSOLUTE)
        origin.left = l
        origin.top = t
        uthread.new(self.BeginDrag, origin)
        d = uicore.desktop
        gx, gy = origin.grab
        uicore.uilib.ClipCursor(gx, gy, d.width - (origin.width - gx), d.height - (origin.height - gy))

    def GetBaseLeftAndTop(self, *args):
        (cX, cY), (toLeft, toTop) = self.GetOriginPosition(getDirection=1)
        par, pl, pt, pw, ph = self.GetTargetLayerAbsolutes()
        if toLeft:
            baseleft = pw - cX
        else:
            baseleft = cX
        if toTop:
            basetop = ph - cY
        else:
            basetop = cY
        return (baseleft, basetop)

    def UpdateOriginDirection(self):
        if not self.origin:
            return
        origin = self.origin
        d = uicore.desktop
        l, t, w, h = origin.GetAbsolute()
        cX = l + w / 2
        cY = t + h / 2
        if cX > d.width / 2:
            origin.leftline.state = uiconst.UI_NORMAL
            origin.rightline.state = uiconst.UI_HIDDEN
        else:
            origin.rightline.state = uiconst.UI_NORMAL
            origin.leftline.state = uiconst.UI_HIDDEN
        if cY > d.height / 2:
            origin.topline.state = uiconst.UI_NORMAL
            origin.bottomline.state = uiconst.UI_HIDDEN
        else:
            origin.bottomline.state = uiconst.UI_NORMAL
            origin.topline.state = uiconst.UI_HIDDEN

    def BeginDrag(self, origin):
        while self.origin and not origin.destroyed and getattr(origin, 'dragging', 0):
            uicore.uilib.SetCursor(uiconst.UICURSOR_NONE)
            origin.left = uicore.uilib.x - origin.grab[0]
            origin.top = uicore.uilib.y - origin.grab[1]
            self.UpdateOriginDirection()
            if uicore.uilib.mouseOver == self.origin:
                self.origin.hint = localization.GetByLabel('UI/Inflight/TargetListAnchor/AnchorIsMoving')
            else:
                self.origin.hint = ''
            blue.pyos.synchro.SleepWallclock(1)

    def Reset(self):
        self.dogmaLM = None
        self.allTargets = []
        self.rowDict = {}
        self.ClearingTargets()
        self.pendingTargets = []
        self.pendingTargeters = []
        self.targeting = {}
        self.autoTargeting = []
        self.weaponsOnMe = {}
        self.needtarget = []
        self.teams = [[], []]
        self.origin = None
        self.ownerToShipIDCache = {}
        self.ClearTargetedBy()
        uicore.layer.target.Flush()

    def CheckViewMode(self):
        toggleWnds = {'main': [ child for child in uicore.layer.main.children ],
         'inflight': [ child for child in uicore.layer.inflight.children if child.name is not 'l_target' ]}
        if self.viewMode == 'normal':
            if self.origin:
                self.origin.state = uiconst.UI_NORMAL
            if self.preViewMode:
                for wnd in toggleWnds:
                    layer = uicore.layer.Get(wnd)
                    for wndState, name in self.preViewMode:
                        wnd = layer.FindChild(name)
                        if wnd:
                            wnd.state = wndState

            self.preViewMode = None
        else:
            if self.origin:
                self.origin.state = uiconst.UI_HIDDEN
            self.preViewMode = []
            for layer, children in toggleWnds.iteritems():
                for wnd in children:
                    if wnd and wnd.name not in 'l_bracket':
                        self.preViewMode.append((wnd.state, wnd.name))
                        wnd.state = uiconst.UI_HIDDEN

    def IsObserving(self):
        return bool(self.viewMode == 'observe')

    def ToggleTeam(self, itemID):
        current = self.GetTeam(itemID)
        if itemID in self.teams[current]:
            self.teams[current].remove(itemID)
        new = not current
        if itemID not in self.teams[new]:
            self.teams[new].append(itemID)
        settings.user.ui.Set('targetTeamsII', self.teams[:])
        self.ArrangeTargets()

    def RemoveFromTeam(self, itemID, reset = 0):
        obs = self.IsObserving()
        if obs:
            if reset:
                settings.user.ui.Set('targetTeamsII', [[], []])
            current = self.GetTeam(itemID)
            if itemID in self.teams[current]:
                self.teams[current].remove(itemID)

    def MoveUp(self, itemID):
        current = self.GetTeam(itemID)
        teamOrder = self.teams[current]
        idx = 0
        if itemID in teamOrder:
            idx = teamOrder.index(itemID) - 1
        self.SetTeamOrder(itemID, idx)
        self.ArrangeTargets()

    def MoveDown(self, itemID):
        current = self.GetTeam(itemID)
        teamOrder = self.teams[current]
        idx = 0
        if itemID in teamOrder:
            idx = teamOrder.index(itemID) + 1
        self.SetTeamOrder(itemID, idx)
        self.ArrangeTargets()

    def GetTeam(self, itemID):
        return itemID not in self.teams[0]

    def GetTeamOrder(self, itemID):
        current = self.GetTeam(itemID)
        teamOrder = self.teams[current]
        if itemID in teamOrder:
            return teamOrder.index(itemID)
        return -1

    def SetTeamOrder(self, itemID, idx):
        idx = max(0, idx)
        current = self.GetTeam(itemID)
        if itemID in self.teams[current]:
            self.teams[current].remove(itemID)
        self.teams[current].insert(idx, itemID)

    def ToggleViewMode(self):
        self.viewMode = ['normal', 'observe'][self.viewMode == 'normal']
        self.Reset()
        if eve.session.shipid and not eve.session.stationid:
            self.godma.GetStateManager().RefreshTargets()
        self.CheckViewMode()
        if self.viewMode == 'observe':
            sm.GetService('infoPanel').ShowHideSidePanel(hide=True)
        else:
            sm.GetService('infoPanel').ShowHideSidePanel(hide=False)

    def Show(self):
        wnd = uicore.layer.target
        if wnd:
            for each in wnd.children:
                each.state = uiconst.UI_NORMAL

    def GetDogmaLM(self):
        if self.dogmaLM is None:
            self.dogmaLM = self.godma.GetDogmaLM()
        return self.dogmaLM

    def OnSpecialFX(self, shipID, moduleID, moduleTypeID, targetID, otherTypeID, guid, isOffensive, start, active, duration = -1, repeat = None, startTime = None, timeFromStart = 0, graphicInfo = None):
        if isOffensive and targetID == eve.session.shipid:
            self.weaponsOnMe[shipID] = self.weaponsOnMe.get(shipID, 0) + (-1, +1)[start]

    def OnStateChange(self, itemID, flag, true, *args):
        if flag == state.selected and true and self.needtarget and len(self.needtarget) > 0:
            if not self.IsTarget(itemID):
                self.HideTargetingCursor()
                target = self.needtarget[0]
                if hasattr(target, 'GetDefaultEffect'):
                    effect = self.needtarget[0].GetDefaultEffect()
                    if effect is not None and effect.effectName == 'targetPassively':
                        uthread.pool('TargetManager::OnStateChange-->ActivateTargetPassively', self.LockTargetPassively, itemID, self.needtarget[0])
                    else:
                        uthread.pool('TargetManager::OnStateChange-->LockTarget', self.TryLockTarget, itemID)
                elif target is None:
                    self.LogError("target doesn't have a GetDefaultEffect because it None")
                elif hasattr(target, '__class__'):
                    self.LogError(target.__class__.__name__, "doesn't have GetDefaultEffect attr")
                else:
                    self.LogError(target, "doesn't have GetDefaultEffect attr")
                self.needtarget = []

    def ProcessSessionChange(self, isRemote, session, change):
        if not isRemote:
            return
        spaceShipChange = 'ship' in change and 'solarsystemid' not in change
        if not sm.GetService('connection').IsConnected() or eve.session.stationid is not None or eve.session.charid is None:
            self.CleanUp()
        elif spaceShipChange and change['shipid'][0] is not None:
            self.OnTargetClear()
            self.pendingTargeters = []
        if 'solarsystemid' in change:
            self.deadShipsBeingRemoved = set()
        if 'fleetid' in change and change['fleetid'][1] is None:
            self.UpdateFleetTags()
        changingShipsInSpace = spaceShipChange and session.solarsystemid and session.shipid
        loggingDirectlyIntoSpace = change.get('solarsystemid', (1, 1))[0] is None and not eve.session.stationid
        undocking = eveSessions.IsUndockingSessionChange(session, change)
        if changingShipsInSpace or loggingDirectlyIntoSpace or undocking:
            for otherID in self.targetedBy:
                self.stateSvc.SetState(otherID, state.threatTargetsMe, 0)

            if session.shipid:
                uthread.new(self.godma.GetStateManager().RefreshTargets)
        self.dogmaLM = None

    def CleanUp(self):
        self.viewMode = 'normal'
        self.CheckViewMode()
        self.ClearingTargets()
        self.dogmaLM = None
        self.ClearTargetedBy()

    def ClearingTargets(self, *args):
        if getattr(self, 'targetsByID', None) is not None:
            for target in self.targetsByID.values():
                target.Close()

        self.targetsByID = {}
        self.groupIdByTarget = {}
        self.deadShipsBeingRemoved = set()

    def DoBallsAdded(self, *args, **kw):
        import stackless
        import blue
        t = stackless.getcurrent()
        timer = t.PushTimer(blue.pyos.taskletTimer.GetCurrent() + '::targetMgr')
        try:
            return self.DoBallsAdded_(*args, **kw)
        finally:
            t.PopTimer(timer)

    def DoBallsAdded_(self, lst):
        for ball, slimItem in lst:
            if ball.id in self.pendingTargets:
                self.OnTargetAdded(ball.id)
            if ball.id in self.pendingTargeters:
                self.OnTargetByOther(ball.id)

    @telemetry.ZONE_METHOD
    def DoBallsRemove(self, pythonBalls, isRelease):
        if isRelease:
            if len(self.pendingTargets) or len(self.autoTargeting) or len(self.targeting):
                sm.GetService('audio').StopSoundLoop('TargetLocking', 'msg_TargetLocked_play')
            for targetID, target in self.targetsByID.iteritems():
                target.Close()

            if self.origin is not None and not self.origin.destroyed:
                self.origin.Close()
                self.origin = None
            self.targetsByID = {}
            self.groupIdByTarget = {}
            self.pendingTargets = []
            self.rowDict = {}
            self.deadShipsBeingRemoved = set()
            return
        for ball, slimItem, terminal in pythonBalls:
            self.DoBallRemove(ball, slimItem, terminal)

    def DoBallRemove(self, ball, slimItem, terminal):
        if ball is None:
            return
        tid = ball.id
        if tid in self.pendingTargets or tid in self.autoTargeting or tid in self.targeting:
            sm.GetService('audio').StopSoundLoop('TargetLocking', 'msg_TargetLocked_play')
        if tid not in self.deadShipsBeingRemoved:
            self.ClearTarget(tid)

    def DoBallClear(self, solitem):
        self.CleanUp()

    def OnTargets(self, targets):
        for each in targets:
            self.OnTarget(*each[1:])

    def OnTarget(self, what, tid = None, reason = None):
        if what == 'add':
            self.OnTargetAdded(tid)
        elif what == 'clear':
            self.OnTargetClear()
        elif what == 'lost':
            uthread.new(self.OnTargetLost, tid, reason)
        elif what == 'otheradd':
            self.OnTargetByOther(tid)
        elif what == 'otherlost':
            self.OnTargetByOtherLost(tid, reason)
        sm.ChainEvent('ProcessTargetChanged', what, tid, reason)

    def OnTargetAdded(self, tid):
        if self.origin is None:
            self.PlaceOrigin()
        if tid in self.targeting:
            del self.targeting[tid]
        if tid in self.autoTargeting:
            self.autoTargeting.remove(tid)
        sm.GetService('audio').StopSoundLoop('TargetLocking', 'msg_TargetLocked_play')
        slimItem = None
        bp = sm.GetService('michelle').GetBallpark()
        if bp is not None:
            slimItem = bp.GetInvItem(tid)
        if bp is None or slimItem is None:
            if tid not in self.pendingTargets:
                self.pendingTargets.append(tid)
            return
        self.stateSvc.SetState(tid, state.targeting, 0)
        self.stateSvc.SetState(tid, state.targeted, 1)
        if tid in self.pendingTargets:
            self.pendingTargets.remove(tid)
        sm.ScatterEvent('OnClientEvent_LockItem', slimItem)
        if tid in self.targetsByID:
            self.ClearTarget(tid)
        obs = self.IsObserving()
        if obs and not (tid in self.teams[0] or tid in self.teams[1]):
            self.teams[1].append(tid)
        if settings.user.ui.Get('alignHorizontally', 1):
            padBottom = 0
        else:
            padBottom = TARGET_PADDING
        targetClass = self.GetTargetClassForSlimItem(slimItem)
        target = targetClass(name='target', parent=uicore.layer.target, align=uiconst.TOPRIGHT, width=[110, 160][obs], height=[150, 80][obs], state=uiconst.UI_PICKCHILDREN, padBottom=padBottom)
        target.Startup(slimItem)
        targetID = slimItem.itemID
        self.targetsByID[targetID] = target
        self.groupIdByTarget[targetID] = slimItem.groupID
        bracket = sm.GetService('bracket').GetBracket(tid)
        if bracket and bracket.sr.targetItem:
            bracket.sr.targetItem.state = [uiconst.UI_DISABLED, uiconst.UI_HIDDEN][obs]
        self.ArrangeTargets()
        if not self.GetActiveTargetID():
            self.stateSvc.SetState(tid, state.activeTarget, 1)
            if self.stateSvc.GetExclState(state.selected) is None:
                self.stateSvc.SetState(tid, state.selected, 1)

    def GetTargetClassForSlimItem(self, slimItem):
        if slimItem.categoryID == const.categoryFighter:
            return TargetInBarFighter
        else:
            return TargetInBar

    def OnFleetStateChange(self, fleetState):
        if not fleetState:
            return
        for itemID, tag in fleetState.targetTags.iteritems():
            target = self.GetTarget(itemID)
            if target:
                target.SetFleetTag(tag)

    def UpdateFleetTags(self):
        fleetSvc = sm.GetService('fleet')
        for eachID, eachTarget in self.GetTargets().iteritems():
            tag = fleetSvc.GetTargetTag(eachID)
            eachTarget.SetFleetTag(tag)

    def OrderTarget(self, who):
        if who not in self.needtarget[:]:
            self.needtarget.append(who)
        self.ShowTargetingCursor()

    def IsSomeModuleWaitingForTargetClick(self):
        return bool(self.needtarget)

    def CancelTargetOrder(self, who = None):
        if not who and len(self.needtarget):
            for each in self.needtarget:
                if each and not each.destroyed:
                    each.waitingForActiveTarget = 0

            self.needtarget = []
        elif who in self.needtarget:
            self.needtarget.remove(who)
            who.waitingForActiveTarget = 0
        if not len(self.needtarget):
            self.HideTargetingCursor()

    def ShowTargetingCursor(self):
        uicore.layer.inflight.sr.tcursor.state = uiconst.UI_DISABLED

    def HideTargetingCursor(self):
        uicore.layer.inflight.sr.tcursor.state = uiconst.UI_HIDDEN

    def GetOriginAlign(self, toLeft, toTop):
        if toLeft:
            if toTop:
                align = uiconst.BOTTOMRIGHT
            else:
                align = uiconst.TOPRIGHT
        elif toTop:
            align = uiconst.BOTTOMLEFT
        else:
            align = uiconst.TOPLEFT
        return align

    def PrepareRowsOrColumns(self, originAlign, baseleft, basetop, *args):
        targetPar = self.targetPar
        alignmentDict = {(0, uiconst.TOPLEFT): (uiconst.TOLEFT, uiconst.TOTOP, (baseleft,
                                 basetop,
                                 0,
                                 0)),
         (0, uiconst.TOPRIGHT): (uiconst.TORIGHT, uiconst.TOTOP, (0,
                                  basetop,
                                  baseleft,
                                  0)),
         (0, uiconst.BOTTOMLEFT): (uiconst.TOLEFT, uiconst.TOBOTTOM, (baseleft,
                                    0,
                                    0,
                                    basetop)),
         (0, uiconst.BOTTOMRIGHT): (uiconst.TORIGHT, uiconst.TOBOTTOM, (0,
                                     0,
                                     baseleft,
                                     basetop)),
         (1, uiconst.TOPLEFT): (uiconst.TOTOP, uiconst.TOLEFT, (baseleft,
                                 basetop,
                                 0,
                                 0)),
         (1, uiconst.TOPRIGHT): (uiconst.TOTOP, uiconst.TORIGHT, (0,
                                  basetop,
                                  baseleft,
                                  0)),
         (1, uiconst.BOTTOMLEFT): (uiconst.TOBOTTOM, uiconst.TOLEFT, (baseleft,
                                    0,
                                    0,
                                    basetop)),
         (1, uiconst.BOTTOMRIGHT): (uiconst.TOBOTTOM, uiconst.TORIGHT, (0,
                                     0,
                                     baseleft,
                                     basetop))}
        horizontally = settings.user.ui.Get('alignHorizontally', 1)
        rowAlignment, targetAlignment, targetParPadding = alignmentDict[horizontally, originAlign]
        widthAvailable = uicore.desktop.width - baseleft
        heightAvailable = uicore.desktop.height - basetop
        if horizontally:
            availableSpace = heightAvailable
            maxHeight = AVG_TARGET_HEIGHT
            maxWidth = 0
            maxRowsPossible = availableSpace / maxHeight
        else:
            availableSpace = widthAvailable
            maxHeight = 0
            maxWidth = MAX_TARGET_WIDTH
            maxRowsPossible = availableSpace / maxWidth
        counter = 0
        for eachRow in targetPar.children:
            if not isinstance(eachRow, Container):
                continue
            if counter >= maxRowsPossible:
                eachRow.display = False
                counter += 1
                continue
            eachRow.display = True
            if eachRow.align != rowAlignment:
                eachRow.SetAlign(rowAlignment)
                eachRow.height = maxHeight
                eachRow.width = maxWidth
            for eachTarget in eachRow.children:
                if not isinstance(eachTarget, TargetInBar):
                    continue
                eachTarget.SetAlign(targetAlignment)
                if horizontally:
                    eachTarget.padBottom = 0
                else:
                    eachTarget.padBottom = max(TARGET_PADDING, eachTarget.padBottom)

            counter += 1

        newRowList = []
        for i in xrange(maxRowsPossible):
            aRow = getattr(targetPar, 'aRow_%s' % i, None)
            if not aRow or aRow.destroyed:
                aRow = Container(parent=targetPar, align=rowAlignment, height=maxHeight, width=maxWidth, name='aRowx_%s' % i, state=uiconst.UI_PICKCHILDREN)
                aRow.numRow = i
                setattr(targetPar, 'aRow_%s' % i, aRow)
            newRowList.append(aRow)

        targetPar.rows = newRowList
        targetPar.padding = targetParPadding
        return targetAlignment

    def ArrangeTargets(self):
        self.PositionOriginWithAnchors()
        self.UpdateOriginDirection()
        if self.origin:
            self.origin.state = uiconst.UI_NORMAL
        targetPar = getattr(self, 'targetPar', None)
        if targetPar is None or getattr(self, 'origin', None) is None:
            return
        (cX, cY), (toLeft, toTop) = self.GetOriginPosition(getDirection=1)
        originAlign = self.GetOriginAlign(toLeft, toTop)
        baseleft, basetop = self.GetBaseLeftAndTop()
        targetAlignment = self.PrepareRowsOrColumns(originAlign, baseleft, basetop)
        targetsThatDontFit = []
        targetsAdded = []
        rows = targetPar.rows
        for key, targetIDs in self.rowDict.iteritems():
            if len(rows) >= key + 1:
                cont = rows[key]
            else:
                targetsThatDontFit += targetIDs
                self.rowDict[key] = []
                continue
            newTargetList = []
            counter = 0
            for eachTargetID in targetIDs:
                eachTarget = self.GetTarget(eachTargetID)
                if getattr(eachTarget, 'isDragging', False):
                    continue
                if eachTarget is None or eachTarget.destroyed:
                    continue
                if not self.DoesTargetFit(cont, baseleft, basetop, counter + 1, excludedTargetID=eachTargetID):
                    targetsThatDontFit.append(eachTargetID)
                    counter += 1
                    continue
                eachTarget.SetAlign(targetAlignment)
                eachTarget.SetParent(cont)
                targetsAdded.append(eachTarget.id)
                newTargetList.append(eachTargetID)
                counter += 1

            self.rowDict[key] = newTargetList

        horizontally = settings.user.ui.Get('alignHorizontally', 1)
        wnd, pl, pt, pw, ph = self.GetTargetLayerAbsolutes()
        for targetID, target in self.targetsByID.iteritems():
            if not isinstance(target, TargetInBar):
                continue
            if targetID in targetsAdded:
                continue
            if getattr(target, 'isDragging', False):
                continue
            myCont, numTargets = self.FindRow(rows, baseleft, basetop)
            target.state = uiconst.UI_PICKCHILDREN
            target.SetAlign(targetAlignment)
            if myCont:
                target.SetParent(myCont)
                targetList = self.rowDict.get(myCont.numRow, [])
                targetList.append(targetID)
                self.rowDict[myCont.numRow] = targetList
                if targetID in targetsThatDontFit:
                    targetsThatDontFit.remove(targetID)

        if len(targetsThatDontFit) > 0:
            self.LogError('did not add the following targets: ', targetsThatDontFit)
        uthread.new(self.AdjustRowSize)
        sm.ScatterEvent('OnTargetsArranged')

    def FindRow(self, possibleContainers, baseLeft, baseTop, *args):
        for cont in possibleContainers:
            if self.DoesTargetFit(cont, baseLeft, baseTop):
                numTargets = len([ child for child in cont.children if isinstance(child, TargetInBar) ])
                return (cont, numTargets)

        return (None, 0)

    def AdjustRowSize(self):
        if self.IsObserving():
            return
        targetPar = getattr(self, 'targetPar', None)
        if targetPar is None:
            return
        blue.pyos.synchro.Yield()
        horizontally = settings.user.ui.Get('alignHorizontally', 1)
        if horizontally:
            for eachRow in targetPar.rows:
                if not eachRow.display:
                    continue
                if self.overrideBarHeight is None:
                    maxHeight = self.GetRowMaxHeight(eachRow, MIN_TARGET_HEIHT)
                    uicore.animations.MorphScalar(eachRow, 'height', eachRow.height, maxHeight + TARGET_PADDING, duration=0.3)
                else:
                    eachRow.height = self.overrideBarHeight

        else:
            maxLineHeights = self.GetLinesMaxHeights()
            for lineIdx, values in maxLineHeights.iteritems():
                maxH = max([ h for h, targetID in values ])
                maxH = maxH
                for h, targetID in values:
                    target = self.GetTarget(targetID)
                    if target:
                        padBottom = maxH - target.height
                        uicore.animations.MorphScalar(target, 'padBottom', target.padBottom, padBottom, duration=0.5)

    def GetRowMaxHeight(self, targetRow, minSize, *args):
        horizontally = settings.user.ui.Get('alignHorizontally', 1)
        if horizontally:
            maxHeight = max([minSize] + [ target.height for target in targetRow.children if isinstance(target, TargetInBar) ])
            return maxHeight

    def GetLinesMaxHeights(self, *args):
        heightByLineIdx = {}
        for rowKey, targetIDs in self.rowDict.iteritems():
            if not targetIDs:
                continue
            for lineIdx, targetID in enumerate(targetIDs):
                target = self.GetTarget(targetID)
                if targetID:
                    heightList = heightByLineIdx.get(lineIdx, [])
                    heightList.append((target.height + TARGET_PADDING, targetID))
                    heightByLineIdx[lineIdx] = heightList

        return heightByLineIdx

    def DoesTargetFit(self, cont, baseLeft, baseTop, idx = None, excludedTargetID = None, *args):
        horizontally = settings.user.ui.Get('alignHorizontally', 1)
        if horizontally:
            parSize = uicore.desktop.width - baseLeft
            commonTargetSize = MAX_TARGET_WIDTH
        else:
            parSize = uicore.desktop.height - baseTop
            commonTargetSize = AVG_TARGET_HEIGHT
        numTargets = 0
        for child in cont.children[:idx]:
            if not isinstance(child, TargetInBar):
                continue
            if child.id == excludedTargetID:
                continue
            numTargets += 1

        totalSizeOfTargets = numTargets * commonTargetSize
        return totalSizeOfTargets + commonTargetSize < parSize

    def OnMoveTarget(self, target, *args):
        if settings.user.ui.Get('targetPositionLocked', 0):
            return
        targetPar = getattr(self, 'targetPar', None)
        if targetPar is None or targetPar.destroyed:
            return targetPar
        wnd, pl, pt, pw, ph = self.GetTargetLayerAbsolutes()
        tl, tt, tw, th = targetPar.GetAbsolute()
        clipper = (tl - 10,
         tt - 5,
         tl + tw + 20,
         tt + th + 10)
        uthread.new(self.DoRepositionDrag, target, clipper)

    def DoRepositionDrag(self, myTarget, cursorClipper):
        if uicore.uilib.leftbtn and uicore.uilib.mouseOver == myTarget.barAndImageCont:
            uicore.uilib.ClipCursor(*cursorClipper)
        else:
            return
        horizontalAlign = settings.user.ui.Get('alignHorizontally', True)
        repositionLine = Line(align=uiconst.TORIGHT_NOPUSH, weight=2, color=(1, 1, 1, 0.5))
        oldParentRowOrColumn = getattr(myTarget.parent, 'numRow', None)
        if oldParentRowOrColumn is None:
            for rowKey, row in self.rowDict.iteritems():
                if myTarget.id in row:
                    oldParentRowOrColumn = rowKey
                    break

        myTarget.opacity = 0.3
        myTarget.isDragging = True
        targetSvc = sm.GetService('target')
        targetPar = getattr(self, 'targetPar', None)
        if not targetPar:
            return
        myRow = None
        posIndex = 0
        while uicore.uilib.leftbtn:
            (originX, originY), (toLeft, toTop) = targetSvc.GetOriginPosition(getDirection=1)
            lessThanAll = True
            for row in targetPar.children:
                if not isinstance(row, Container):
                    continue
                tl, tt, tw, th = row.GetAbsolute()
                if tl - 2 <= uicore.uilib.x <= tl + tw + 2 and tt - 2 <= uicore.uilib.y <= tt + th + 2:
                    myRow = row
                    break

            if not myRow:
                blue.pyos.synchro.Yield()
                continue
            counter = 0
            mouseX = uicore.uilib.x
            mouseY = uicore.uilib.y
            for target in myRow.children:
                if not isinstance(target, TargetInBar):
                    continue
                counter += 1
                tl, tt, tw, th = target.GetAbsolute()
                isOverTarget = tl <= mouseX < tl + tw and tt <= mouseY < tt + th
                if isOverTarget:
                    if horizontalAlign:
                        if toLeft:
                            repositionLine.SetAlign(uiconst.TORIGHT_NOPUSH)
                            posIndex = counter
                        else:
                            posIndex = counter - 1
                            repositionLine.SetAlign(uiconst.TOLEFT_NOPUSH)
                    elif toTop:
                        posIndex = counter
                        repositionLine.SetAlign(uiconst.TOBOTTOM_NOPUSH)
                    else:
                        posIndex = counter - 1
                        repositionLine.SetAlign(uiconst.TOTOP_NOPUSH)
                    repositionLine.SetParent(myRow)
                    repositionLine.SetOrder(posIndex)
                    lessThanAll = False
                    break

            if lessThanAll:
                posIndex = -1
                if horizontalAlign:
                    if toLeft:
                        if originX < mouseX:
                            posIndex = 0
                        repositionLine.SetAlign(uiconst.TORIGHT_NOPUSH)
                    else:
                        if originX > mouseX:
                            posIndex = 0
                        repositionLine.SetAlign(uiconst.TOLEFT_NOPUSH)
                elif toTop:
                    if originY < mouseY:
                        posIndex = 0
                    repositionLine.SetAlign(uiconst.TOBOTTOM_NOPUSH)
                else:
                    if originY > mouseY:
                        posIndex = 0
                    repositionLine.SetAlign(uiconst.TOTOP_NOPUSH)
                repositionLine.SetParent(myRow)
                repositionLine.SetOrder(posIndex)
            self.ColorRepositionLine(myRow, myTarget.id, repositionLine)
            blue.pyos.synchro.Yield()

        uicore.uilib.UnclipCursor()
        if myRow:
            doAddTarget = True
            if oldParentRowOrColumn is not None:
                old = self.rowDict.get(oldParentRowOrColumn, [])
                if myTarget.id in old:
                    targetsCurrentPos = (posIndex, posIndex - 1)
                    if oldParentRowOrColumn == myRow.numRow:
                        oldIndex = old.index(myTarget.id)
                        if oldIndex in targetsCurrentPos:
                            doAddTarget = False
                        elif oldIndex < posIndex:
                            posIndex -= 1
                    if doAddTarget:
                        old.remove(myTarget.id)
                self.rowDict[oldParentRowOrColumn] = old
            if doAddTarget:
                posIndex = max(-1, posIndex)
                newRow = self.rowDict.get(myRow.numRow, [])
                if posIndex < 0:
                    newRow.append(myTarget.id)
                else:
                    newRow.insert(posIndex, myTarget.id)
                self.rowDict[myRow.numRow] = newRow
        myTarget.isDragging = False
        repositionLine.Close()
        myTarget.opacity = 1.0
        targetSvc.ArrangeTargets()

    def ColorRepositionLine(self, myRow, excludedTargetID, repositionLine, *args):
        baseLeft, baseTop = self.GetBaseLeftAndTop()
        if self.DoesTargetFit(myRow, baseLeft, baseTop, excludedTargetID=excludedTargetID):
            repositionLine.SetRGBA(1, 1, 1, 0.5)
        else:
            repositionLine.SetRGBA(1, 0.5, 0, 0.5)

    def SelectNextTarget(self):
        activeID = self.GetActiveTargetID()
        if activeID is None:
            return
        nextTarget = self.FindNextTarget(activeID, direction=1)
        if nextTarget:
            self._SetSelected(nextTarget)

    def SelectPrevTarget(self):
        activeID = self.GetActiveTargetID()
        if activeID is None:
            return
        prevTarget = self.FindNextTarget(activeID, direction=-1)
        if prevTarget:
            self._SetSelected(prevTarget)

    def FindNextTarget(self, activeID, direction = 1):
        allTargetIDsInOrder = self.GetSortedTargetList()
        if not allTargetIDsInOrder:
            return None
        elif activeID not in allTargetIDsInOrder:
            return allTargetIDsInOrder[0]
        activeIndex = allTargetIDsInOrder.index(activeID)
        if direction == 1:
            if activeIndex == len(allTargetIDsInOrder) - 1:
                return allTargetIDsInOrder[0]
            return allTargetIDsInOrder[activeIndex + 1]
        else:
            return allTargetIDsInOrder[activeIndex - 1]

    def GetSortedTargetList(self, *args):
        sortedLists = []
        for rowKey, targetIDs in self.rowDict.iteritems():
            validTargetIDs = filter(lambda x: x not in self.deadShipsBeingRemoved, targetIDs)
            sortedLists.append((rowKey, validTargetIDs))

        sortedLists = SortListOfTuples(sortedLists)
        allTargetIDsInOrder = []
        for eachList in sortedLists:
            allTargetIDsInOrder += eachList

        return allTargetIDsInOrder

    def _SetSelected(self, targetID):
        self.stateSvc.SetState(targetID, state.selected, 1)
        self.stateSvc.SetState(targetID, state.activeTarget, 1)

    def OnTargetLost(self, tid, reason):
        (self.stateSvc.SetState(tid, state.targeted, 0), self.stateSvc.GetExclState(state.activeTarget))
        if self.stateSvc.GetExclState(state.activeTarget) == tid:
            self.stateSvc.SetState(tid, state.activeTarget, 0)
        if tid in self.pendingTargets:
            self.pendingTargets.remove(tid)
            sm.GetService('audio').StopSoundLoop('TargetLocking', 'msg_TargetLocked_play')
        self.LogInfo('OnTargetLost ', tid)
        if reason == 'Exploding':
            self.ClearDeadTarget(targetID=tid, reason=reason)
        else:
            self.ClearTarget(tid, reason=reason)

    def ClearDeadTarget(self, targetID, reason = None, *args):
        if targetID in self.targetsByID and targetID not in self.deadShipsBeingRemoved:
            try:
                self.deadShipsBeingRemoved.add(targetID)
                t = self.targetsByID[targetID]
                self.SetFirstTargetActiveIfNoActive()
                t.StartDeathAnimation()
            except:
                self.LogException()
            finally:
                self.ClearTarget(targetID, reason=reason)

    def OnTargetByOther(self, otherID):
        self.stateSvc.SetState(otherID, state.threatTargetsMe, 1)
        if otherID in self.targetedBy:
            self.LogError('already targeted by', otherID)
        else:
            self.AddTargetedBy(otherID)
        bp = sm.GetService('michelle').GetBallpark()
        if bp is not None:
            slimItem = bp.GetInvItem(otherID)
            if slimItem is not None:
                if slimItem.ownerID:
                    self.ownerToShipIDCache[slimItem.ownerID] = otherID
        if bp is None or slimItem is None:
            if otherID not in self.pendingTargeters:
                self.pendingTargeters.append(otherID)
            return
        if otherID in self.pendingTargeters:
            self.pendingTargeters.remove(otherID)
        tgts = self.GetTargets().keys() + self.targeting.keys()
        if otherID != eve.session.shipid and otherID not in tgts and otherID not in self.autoTargeting and min(settings.user.ui.Get('autoTargetBack', 0), sm.GetService('godma').GetItem(session.charid).maxLockedTargets, sm.GetService('godma').GetItem(session.shipid).maxLockedTargets) > len(tgts):
            if len(self.autoTargeting) < settings.user.ui.Get('autoTargetBack', 0):
                self.autoTargeting.append(otherID)
                uthread.pool('TargetManages::OnTargetByOther-->LockTarget', self.LockTarget, otherID, autotargeting=1)

    def GetTarget(self, targetID):
        return self.targetsByID.get(targetID, None)

    def OnTargetByOtherLost(self, otherID, reason):
        self.stateSvc.SetState(otherID, state.threatTargetsMe, 0)
        if otherID in self.pendingTargeters:
            self.pendingTargeters.remove(otherID)
        try:
            self.RemoveTargetedBy(otherID)
        except ValueError:
            self.LogInfo('was not targeted by', otherID)
            sys.exc_clear()

        bp = sm.GetService('michelle').GetBallpark()
        if bp is not None:
            slimItem = bp.GetInvItem(otherID)
            if slimItem is not None:
                if slimItem.ownerID and slimItem.ownerID in self.ownerToShipIDCache:
                    del self.ownerToShipIDCache[slimItem.ownerID]

    def OnTargetClear(self, targetsToSkip = None):
        for tid in self.targetsByID.keys():
            if targetsToSkip and tid in targetsToSkip:
                continue
            self.stateSvc.SetState(tid, state.activeTarget, 0)
            self.stateSvc.SetState(tid, state.targeting, 0)
            self.stateSvc.SetState(tid, state.targeted, 0)
            self.CancelTargetOrder()
            self.ClearTarget(tid)

    def GetTargetedBy(self):
        return self.targetedBy

    def IsTargeted(self):
        return len(self.targetedBy) > 0

    def GetTargeting(self):
        return self.targeting.keys()

    def ClearTarget(self, tid, reason = None):
        removedTarget = False
        if tid in self.targetsByID:
            t = self.targetsByID[tid]
            del self.targetsByID[tid]
            groupID = self.groupIdByTarget[tid]
            del self.groupIdByTarget[tid]
            self.deadShipsBeingRemoved.discard(tid)
            t.Close()
            self.ArrangeTargets()
            removedTarget = True
            sm.ScatterEvent('OnClientEvent_UnlockItem', tid)
        if tid in self.pendingTargets:
            self.pendingTargets.remove(tid)
        if removedTarget and not self.targetsByID:
            if self.origin is not None and not self.origin.destroyed:
                self.origin.Close()
                self.origin = None
            self.stateSvc.SetState(tid, state.activeTarget, 0)
        for rowKey, row in self.rowDict.iteritems():
            if tid in row:
                row.remove(tid)
                self.rowDict[rowKey] = row
                break

        if self.targetsByID:
            self.SetFirstTargetActiveIfNoActive()

    def SetFirstTargetActiveIfNoActive(self):
        active = self.stateSvc.GetExclState(state.activeTarget)
        if active is None and self.targetsByID:
            allTargetIDsInOrder = self.GetSortedTargetList()
            if allTargetIDsInOrder:
                targetToSelect = allTargetIDsInOrder[0]
                self.stateSvc.SetState(targetToSelect, state.activeTarget, 1)

    def GetTargetingStartTime(self, targetID):
        return self.targeting.get(targetID, None)

    def BeingTargeted(self, targetID):
        return targetID in self.targeting

    def StartLockTarget(self, tid, autotargeting = 0):
        if tid in self.GetTargets():
            self.ClearTarget(tid)
            self.stateSvc.SetState(tid, state.targeting, 0)
            sm.GetService('audio').StopSoundLoop('TargetLocking')
        if tid in self.targeting:
            return
        self.LogInfo('targetMgr: Locking Target for ', tid)
        sm.GetService('audio').StartSoundLoop('TargetLocking')
        sm.ScatterEvent('OnTargetLockStarted', GetBallparkRecord(tid))
        self.stateSvc.SetState(tid, state.targeting, 1)
        self.targeting[tid] = blue.os.GetSimTime()

    def FailLockTarget(self, tid):
        if tid in self.targeting:
            del self.targeting[tid]
        if tid in self.autoTargeting:
            self.autoTargeting.remove(tid)
        self.stateSvc.SetState(tid, state.targeted, 0)
        self.stateSvc.SetState(tid, state.targeting, 0)
        sm.GetService('audio').StopSoundLoop('TargetLocking')
        sm.ScatterEvent('OnFailLockTarget', tid)

    def CancelAddTarget(self, tid):
        self.stateSvc.SetState(tid, state.targeted, 0)
        self.stateSvc.SetState(tid, state.targeting, 0)
        sm.GetService('audio').StopSoundLoop('TargetLocking')
        sm.ScatterEvent('OnFailLockTarget', tid)
        self.GetDogmaLM().CancelAddTarget(tid)

    def TryLockTarget(self, itemID):
        if itemID in self.GetTargeting() or itemID in self.targetsByID:
            return
        slimItem = GetBallparkRecord(itemID)
        if not slimItem:
            return
        if slimItem.groupID in const.nonTargetableGroups:
            return
        if itemID == session.shipid and session.shipid == session.structureid:
            return
        self.LockTarget(itemID)

    def GetDistanceToTarget(self, itemID):
        if session.shipid is None or session.solarsystemid is None:
            raise RuntimeError('Failed to get distance to target. Must be in ship in space (shipID: %s, solarSystemID: %s).' % (session.shipid, session.solarsystemid))
        if itemID is None or itemID == session.shipid or idCheckers.IsUniverseCelestial(itemID):
            raise ValueError('Failed to get distance to target. Target item is not valid (itemID: %s).' % itemID)
        bp = sm.GetService('michelle').GetBallpark()
        if bp is None:
            return RuntimeError('Failed to get distance to target. Ballpark is not available.')
        otherBall = bp and bp.GetBall(itemID) or None
        if otherBall is None:
            return RuntimeError('Failed to get distance to target. Target ball is not available (itemID: %s).' % itemID)
        distanceToTarget = max(0, otherBall.surfaceDist)
        return distanceToTarget

    def GetMaxTargetRange(self):
        shipItem = sm.GetService('godma').GetStateManager().GetItem(session.shipid)
        if shipItem is None:
            return
        return shipItem.maxTargetRange

    def IsInTargetingRange(self, itemID):
        try:
            distanceToTarget = self.GetDistanceToTarget(itemID)
        except (RuntimeError, ValueError):
            return False

        maxTargetRange = self.GetMaxTargetRange()
        if maxTargetRange is None:
            return False
        return distanceToTarget < maxTargetRange

    def LockTarget(self, tid, autotargeting = 0):
        try:
            self._LockTarget(tid, autotargeting)
        except StandardError:
            self.FailLockTarget(tid)
            sys.exc_clear()

    def _LockTarget(self, tid, autotargeting = 0):
        self.StartLockTarget(tid, autotargeting)
        try:
            flag, targetList = self.GetDogmaLM().AddTarget(tid)
            if not flag:
                self.OnTargetAdded(tid)
        except UserError as e:
            self.FailLockTarget(tid)
            if autotargeting:
                sys.exc_clear()
                return
            if e.msg in ('DeniedShipChanged', 'TargetingAttemptCancelled'):
                sys.exc_clear()
                return
            eve.Message(e.msg, e.dict)
            raise

        self.LogInfo('targetMgr: Locking Target for ', tid, ' done')

    def UnlockTarget(self, tid):
        if tid in self.targetsByID:
            self.GetDogmaLM().RemoveTarget(tid)
            self.RemoveFromTeam(tid)

    def UnlockTargets(self):
        targetsToUnlock = self.targetsByID.keys()
        if targetsToUnlock:
            self.GetDogmaLM().RemoveTargets(targetsToUnlock)
            for tID in targetsToUnlock:
                self.RemoveFromTeam(tID)

    def ToggleLockTarget(self, targetID):
        if self.IsTarget(targetID):
            self.UnlockTarget(targetID)
        else:
            self.TryLockTarget(targetID)

    def LockTargetPassively(self, tid, smb):
        self.StartLockTarget(tid, 0)
        try:
            smb.OnStateChange(tid, state.activeTarget, True)
        except UserError as e:
            self.FailLockTarget(tid)
            if e.msg == 'DeniedShipChanged':
                sys.exc_clear()
                return
            raise

        self.LogInfo('targetMgr: PassiveLocking Target for ', tid, ' done')

    def ClearTargets(self):
        self.GetDogmaLM().ClearTargets()

    def GetActiveTargetID(self):
        selected = self.stateSvc.GetExclState(state.activeTarget)
        if selected and selected in self.targetsByID:
            return selected

    def GetTargets(self):
        return self.targetsByID

    def IsTarget(self, targetID):
        return targetID in self.targetsByID

    def GetNumAdditionalTargetsAllowed(self):
        maxTargets = sm.GetService('godma').GetItem(session.shipid).maxLockedTargets
        currTargets = len(self.GetTargets())
        return maxTargets - currTargets

    def FindClosestEntity(self, targetPriority = None):
        return get_closest_entity_target(targetPriority)

    def AddTargetedBy(self, enemyID):
        self.targetedBy.append(enemyID)
        sm.ScatterEvent('OnClientEvent_TargetedByChanged')

    def RemoveTargetedBy(self, enemyID):
        self.targetedBy.remove(enemyID)
        sm.ScatterEvent('OnClientEvent_TargetedByChanged')

    def ClearTargetedBy(self):
        self.targetedBy = []
        sm.ScatterEvent('OnClientEvent_TargetedByChanged')
