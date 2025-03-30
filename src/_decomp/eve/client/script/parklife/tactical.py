#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\tactical.py
import sys
from collections import defaultdict
import blue
import log
import telemetry
import dogma.effects
import evecamera
import evetypes
import localization
import uthread
from caching.memoize import Memoize
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import SERVICE_RUNNING
from carbonui import uiconst
from carbonui.control.window import Window
from carbonui.uicore import uicore
from carbonui.util.bunch import Bunch
from dogma.const import falloffEffectivnessModuleGroups
from eve.client.script.parklife import states as state
from eve.client.script.parklife import tacticalOverlay
from eve.client.script.ui.inflight.activeitem import ActiveItem
from eve.client.script.ui.inflight.drone import DroneView
from eve.client.script.ui.inflight.drones.dronesWindow import DronesWindow
from eve.client.script.ui.inflight.overview.overviewWindow import OverviewWindow
from eve.client.script.ui.inflight.overview.overviewWindowUtil import OpenOverview
from eve.client.script.ui.inflight.selectedItemWnd import SelectedItemWnd
from eve.client.script.ui.shared.export import ExportOverviewWindow, ImportOverviewWindow
from eve.client.script.ui.util import uix
from eve.client.script.ui.view.viewStateConst import ViewState
from eve.common.lib import appConst as const
from eve.common.script.sys import eveCfg, idCheckers
from eveDrones.droneDamageTracker import InBayDroneDamageTracker
from inventorycommon.const import categoryEntity
from overviewPresets import overviewSettingsConst
BRACKETBORDER = 17
OVERVIEW_CONFIGNAME = 0
OVERVIEW_GROUPDATA = 1
BRACKETS_CONFIGNAME = 2
BRACKETS_GROUPDATA = 3
INVISIBLE_TYPES = [const.typeUnlitModularEffectBeacon]
WARP_SCRAMBLE_MESSAGE_ATTACKER = 'OnWarpScrambleAttacker'
WARP_SCRAMBLE_MESSAGE_DEFENDER = 'OnWarpScrambleDefender'
WARP_SCRAMBLE_MESSAGE_OTHER = 'OnWarpScrambleOther'
WARP_DISRUPT_MESSAGE_ATTACKER = 'OnWarpDisruptAttacker'
WARP_DISRUPT_MESSAGE_DEFENDER = 'OnWarpDisruptDefender'
WARP_DISRUPT_MESSAGE_OTHER = 'OnWarpDisruptOther'
TACTICAL_OVERLAY_DISALLOWED_CAMERAS = (evecamera.CAM_SHIPPOV, evecamera.CAM_SHIPORBIT_RESTRICTED, evecamera.CAM_JUMP)

@Memoize
def GetCacheByLabel(key):
    return localization.GetByLabel(key)


def _SendWarpScrambleMessages(shipID, targetID):
    _SendWarpMessages(shipID, targetID, WARP_SCRAMBLE_MESSAGE_ATTACKER, WARP_SCRAMBLE_MESSAGE_DEFENDER, WARP_SCRAMBLE_MESSAGE_OTHER)


def _SendWarpDisruptionMessages(shipID, targetID):
    _SendWarpMessages(shipID, targetID, WARP_DISRUPT_MESSAGE_ATTACKER, WARP_DISRUPT_MESSAGE_DEFENDER, WARP_DISRUPT_MESSAGE_OTHER)


def _SendWarpMessages(shipID, targetID, attackerMessageID, defenderMessageID, otherMessageID):
    attackerName = sm.GetService('bracket').GetBracketName2(shipID)
    defenderName = sm.GetService('bracket').GetBracketName2(targetID)
    if attackerName and defenderName:
        if eve.session.shipid == targetID:
            sm.GetService('logger').AddCombatMessage(defenderMessageID, {'attacker': attackerName})
        elif eve.session.shipid == shipID:
            sm.GetService('logger').AddCombatMessage(attackerMessageID, {'defender': defenderName})
        else:
            sm.GetService('logger').AddCombatMessage(otherMessageID, {'attacker': attackerName,
             'defender': defenderName})


class TacticalSvc(Service):
    __guid__ = 'svc.tactical'
    __update_on_reload__ = 0
    __notifyevents__ = ['DoBallsAdded',
     'DoBallRemove',
     'OnOverviewPresetLoaded',
     'OnStateChange',
     'OnStateSetupChange',
     'ProcessSessionChange',
     'OnSessionChanged',
     'OnSessionReset',
     'OnClientEvent_JumpStarted',
     'OnClientEvent_JumpExecuted',
     'OnSpecialFX',
     'ProcessOnUIAllianceRelationshipChanged',
     'OnSetCorpStanding',
     'OnSetAllianceStanding',
     'OnSuspectsAndCriminalsUpdate',
     'OnDisapprovalUpdate',
     'OnSlimItemChange',
     'OnDroneStateChange2',
     'OnDroneControlLost',
     'OnItemChange',
     'OnBallparkCall',
     'OnEwarStart',
     'OnEwarEnd',
     'OnEwarOnConnect',
     'OnContactChange',
     'OnCrimewatchEngagementUpdated',
     'DoBallsRemove',
     'OnHideUI',
     'OnShowUI',
     'OnCombatMessage',
     'OnOverviewTabsChanged']
    __startupdependencies__ = ['settings', 'tacticalNavigation', 'viewState']
    __dependencies__ = ['clientDogmaStaticSvc',
     'stateSvc',
     'bracket',
     'overviewPresetSvc',
     'godma']

    def __init__(self):
        Service.__init__(self)
        self._clearModuleTasklet = None

    def Run(self, *etc):
        Service.Run(self, *etc)
        self.tacticalOverlay = tacticalOverlay.TacticalOverlay(self, self.tacticalNavigation)
        self.logme = 0
        self.jammers = {}
        self.jammersByJammingType = {}
        self.filterFuncs = None
        self.CleanUp()
        self.Setup()
        self.hideUI = False
        self.flagsAreDirty = False
        self.dirtyFlags = set()
        self.flagCheckingThread = uthread.new(self.FlagsDirtyCheckingLoop)
        self.inBayDroneDamageTracker = None

    def Setup(self):
        self.CleanUp()
        self.AssureSetup()
        if eveCfg.InSpace():
            if self.IsTacticalOverlayActive():
                self.tacticalOverlay.Initialize()
            self.Open()

    def Stop(self, *etc):
        Service.Stop(self, *etc)
        self.CleanUp()

    def OnCombatMessage(self, messageName, messageArgs):
        if 'specialObject' in messageArgs:
            objectName = sm.GetService('bracket').GetBracketName2(messageArgs['specialObject'])
            messageArgs['specialObject'] = objectName
        sm.GetService('logger').AddCombatMessage(messageName, messageArgs)

    @telemetry.ZONE_METHOD
    def OnBallparkCall(self, eventName, argTuple):
        if self.sr is None:
            return
        if eventName == 'SetBallInteractive' and argTuple[1] == 1:
            bp = sm.GetService('michelle').GetBallpark()
            if not bp:
                return
            slimItem = bp.GetInvItem(argTuple[0])
            if not slimItem:
                return
            self.MarkFlagsForSpecificItemsAsDirty({slimItem.itemID})

    @telemetry.ZONE_METHOD
    def OnItemChange(self, item, change, location):
        if (const.ixFlag in change or const.ixLocationID in change) and item.flagID == const.flagDroneBay:
            droneview = self.GetPanel('droneview')
            if droneview:
                droneview.CheckReloadDronesScroll()
            else:
                self.CheckInitDrones()

    @telemetry.ZONE_METHOD
    def ProcessSessionChange(self, isRemote, session, change):
        doResetJammers = False
        if self.logme:
            self.LogInfo('Tactical::ProcessSessionChange', isRemote, session, change)
        if 'stationid' in change:
            doResetJammers = True
        if 'solarsystemid' in change:
            self.TearDownOverlay()
            doResetJammers = True
        if 'shipid' in change:
            for itemID in self.attackers:
                self.stateSvc.SetState(itemID, state.threatAttackingMe, 0)

            self.attackers = {}
            doResetJammers = True
            droneview = self.GetPanel('droneview')
            if droneview:
                if getattr(self, '_initingDrones', False):
                    self.LogInfo('Tactical: ProcessSessionChange: busy initing drones, cannot close the window')
                else:
                    droneview.Close()
        if doResetJammers:
            self.ResetJammers()

    def ResetJammers(self):
        self.jammers = {}
        self.jammersByJammingType = {}
        sm.ScatterEvent('OnRefreshBuffBar')

    def RemoveBallFromJammers(self, ball, *args):
        ballID = ball.id
        effectsFromBall = self.jammers.get(ballID)
        if getattr(self, 'fighterService', None) is None:
            setattr(self, 'fighterService', sm.GetService('fighters'))
        self.fighterService.shipFighterState.KillEffectsFromBall(ballID)
        if effectsFromBall is None:
            return
        doUpdate = False
        for effectName, effectSet in self.jammersByJammingType.iteritems():
            if effectName not in effectsFromBall:
                continue
            tuplesToRemove = set()
            for effectTuple in effectSet:
                effectBallID, moduleID = effectTuple
                if effectBallID == ballID:
                    tuplesToRemove.add(effectTuple)

            if tuplesToRemove:
                effectSet.difference_update(tuplesToRemove)
                doUpdate = True

        self.jammers.pop(ballID, None)
        if doUpdate:
            sm.ScatterEvent('OnEwarEndFromTactical')

    def OnSessionChanged(self, isRemote, session, change):
        if eveCfg.InSpace():
            if sm.GetService('subway').InJump():
                return
            self.AssureSetup()
            self.Open()
            if self.IsTacticalOverlayActive() and not self.hideUI:
                self.tacticalOverlay.Initialize()
            self.CheckInitDrones()
            self.MarkFlagsAsDirty()
            if 'shipid' in change:
                self.tacticalOverlay.OnShipChange()
        else:
            self.CleanUp()

    def OnSessionReset(self):
        self.inBayDroneDamageTracker = None

    def OnClientEvent_JumpStarted(self, *args):
        if self.IsTacticalOverlayActive():
            self.TearDownOverlay()
            self.ResetJammers()

    def OnClientEvent_JumpExecuted(self, itemID):
        self.AssureSetup()
        self.Open()
        if self.IsTacticalOverlayActive() and not self.hideUI:
            self.tacticalOverlay.Initialize()
        self.CheckInitDrones()
        self.MarkFlagsAsDirty()

    @telemetry.ZONE_METHOD
    def OnSlimItemChange(self, oldSlim, newSlim):
        if not eveCfg.InSpace():
            return
        update = 0
        if getattr(newSlim, 'allianceID', None) and newSlim.allianceID != getattr(oldSlim, 'allianceID', None):
            update = 1
        elif newSlim.corpID and newSlim.corpID != oldSlim.corpID:
            update = 2
        elif newSlim.charID != oldSlim.charID:
            update = 3
        elif newSlim.ownerID != oldSlim.ownerID:
            update = 4
        elif getattr(newSlim, 'lootRights', None) != getattr(oldSlim, 'lootRights', None):
            update = 5
        elif getattr(newSlim, 'isEmpty', None) != getattr(oldSlim, 'isEmpty', None):
            update = 6
        if update:
            if session.charid in (newSlim.charID, oldSlim.charID):
                self.MarkFlagsAsDirty()
            else:
                self.MarkFlagsForSpecificItemsAsDirty({oldSlim.itemID, newSlim.itemID})

    def ProcessOnUIAllianceRelationshipChanged(self, *args):
        if self.InSpace():
            self.MarkFlagsAsDirty()

    def OnContactChange(self, contactIDs, contactType = None):
        if eveCfg.InSpace():
            self.MarkFlagsAsDirty()

    def OnSetCorpStanding(self, *args):
        if eveCfg.InSpace():
            self.MarkFlagsAsDirty()

    def OnSetAllianceStanding(self, *args):
        if eveCfg.InSpace():
            self.MarkFlagsAsDirty()

    def OnCrimewatchEngagementUpdated(self, otherCharId, timeout):
        if eveCfg.InSpace():
            uthread.new(self.DelayedFlagStateUpdate)

    def OnSuspectsAndCriminalsUpdate(self, criminalizedCharIDs, decriminalizedCharIDs):
        if eveCfg.InSpace():
            uthread.new(self.DelayedFlagStateUpdate)

    def OnDisapprovalUpdate(self, newCharID, removedCharIDs):
        if eveCfg.InSpace():
            uthread.new(self.DelayedFlagStateUpdate)

    def DelayedFlagStateUpdate(self):
        if getattr(self, 'delayedFlagStateUpdate', False):
            return
        setattr(self, 'delayedFlagStateUpdate', True)
        blue.pyos.synchro.SleepWallclock(1000)
        self.MarkFlagsAsDirty()
        setattr(self, 'delayedFlagStateUpdate', False)

    def OnHideUI(self):
        self.hideUI = True
        if self.IsTacticalOverlayActive():
            self.tacticalOverlay.TearDown()

    def OnShowUI(self):
        self.hideUI = False
        if eveCfg.InSpace() and self.IsTacticalOverlayActive():
            self.tacticalOverlay.Initialize()

    @telemetry.ZONE_METHOD
    def OnSpecialFX(self, shipID, moduleID, moduleTypeID, targetID, otherTypeID, guid, isOffensive, start, active, duration = -1, repeat = None, startTime = None, timeFromStart = 0, graphicInfo = None):
        if targetID == eve.session.shipid and isOffensive:
            attackerID = shipID
            attackTime = startTime
            attackRepeat = repeat
            shipItem = sm.StartService('michelle').GetItem(shipID)
            if shipItem and shipItem.categoryID == const.categoryStarbase:
                attackerID = moduleID
                attackTime = 0
                attackRepeat = 0
            data = self.attackers.get(attackerID, [])
            key = (moduleID,
             guid,
             attackTime,
             duration,
             attackRepeat)
            if start and shipID != session.shipid:
                if key not in data:
                    data.append(key)
                self.stateSvc.SetState(attackerID, state.threatAttackingMe, 1)
            else:
                toRemove = None
                for signature in data:
                    if signature[0] == key[0] and signature[1] == key[1] and signature[2] == key[2] and signature[3] == key[3]:
                        toRemove = signature
                        break

                if toRemove is not None:
                    data.remove(toRemove)
                if not data:
                    self.stateSvc.SetState(attackerID, state.threatAttackingMe, 0)
            self.attackers[attackerID] = data
        if start:
            if settings.user.ui.Get('notifyMessagesEnabled', 1) or eve.session.shipid in (shipID, targetID):
                if guid == 'effects.WarpDisrupt':
                    _SendWarpDisruptionMessages(shipID, targetID)
                elif guid == 'effects.WarpScramble':
                    _SendWarpScrambleMessages(shipID, targetID)

    def CheckInitDrones(self):
        mySlim = uix.GetBallparkRecord(eve.session.shipid)
        if not mySlim:
            return
        if mySlim.groupID == const.groupCapsule:
            return
        dronesInBay = sm.GetService('invCache').GetInventoryFromId(session.shipid).ListDroneBay()
        if dronesInBay:
            self.InitDrones()
        else:
            myDrones = sm.GetService('michelle').GetDrones()
            if myDrones:
                self.InitDrones()

    @telemetry.ZONE_METHOD
    def Open(self):
        self.InitSelectedItem()
        OpenOverview()
        self.CheckInitDrones()

    def GetMain(self):
        if self and getattr(self.sr, 'mainParent', None):
            return self.sr.mainParent

    def OnStateChange(self, itemID, flag, true, *args):
        uthread.new(self._OnStateChange, itemID, flag, true, *args)

    def _OnStateChange(self, itemID, flag, true, *args):
        if not eveCfg.InSpace():
            return
        if not self or getattr(self, 'sr', None) is None:
            return
        if self.logme:
            self.LogInfo('Tactical::OnStateChange', itemID, flag, true, *args)
        self.tacticalOverlay.CheckState(itemID, flag, true)

    def OnOverviewPresetLoaded(self, label, set):
        uthread.new(self.InitConnectors).context = 'tactical::OnOverviewPresetLoaded-->InitConnectors'

    def OnStateSetupChange(self, what):
        self.MarkFlagsAsDirty()
        self.InitConnectors()

    def Toggle(self):
        pass

    def BlinkHeader(self, key):
        if not self or self.sr is None:
            return
        panel = getattr(self.sr, key.lower(), None)
        if panel:
            panel.Blink()

    def IsExpanded(self, key):
        panel = getattr(self.sr, key.lower(), None)
        if panel:
            return panel.sr.main.state == uiconst.UI_PICKCHILDREN

    def AssureSetup(self):
        if self.logme:
            self.LogInfo('Tactical::AssureSetup')
        if getattr(self, 'setupAssured', None):
            return
        if getattr(self, 'sr', None) is None:
            self.sr = Bunch()
        self.setupAssured = 1

    def CleanUp(self):
        if self.logme:
            self.LogInfo('Tactical::CleanUp')
        self.sr = None
        self.targetingRanges = None
        self.toggling = 0
        self.setupAssured = 0
        self.lastFactor = None
        self.groupList = None
        self.groupIDs = []
        self.intersections = []
        self.threats = {}
        self.attackers = {}
        self.TearDownOverlay()
        uicore.layer.tactical.Flush()
        self.dronesInited = 0
        self.busy = 0

    def GetFilterFuncs(self):
        if self.filterFuncs is None:
            stateSvc = sm.GetService('stateSvc')
            self.filterFuncs = {'Criminal': stateSvc.CheckCriminal,
             'Suspect': stateSvc.CheckSuspect,
             'Outlaw': stateSvc.CheckOutlaw,
             'Dangerous': stateSvc.CheckDangerous,
             'StandingHigh': stateSvc.CheckStandingHigh,
             'StandingGood': stateSvc.CheckStandingGood,
             'StandingNeutral': stateSvc.CheckStandingNeutral,
             'StandingBad': stateSvc.CheckStandingBad,
             'StandingHorrible': stateSvc.CheckStandingHorrible,
             'NoStanding': stateSvc.CheckNoStanding,
             'SameFleet': stateSvc.CheckSameFleet,
             'SamePlayerCorp': stateSvc.CheckSamePlayerCorp,
             'SameNpcCorp': stateSvc.CheckSameNpcCorp,
             'SameAlliance': stateSvc.CheckSameAlliance,
             'SameMilitia': stateSvc.CheckSameMilitia,
             'AtWarCanFight': stateSvc.CheckAtWarCanFight,
             'AtWarMilitia': stateSvc.CheckAtWarMilitia,
             'IsWanted': stateSvc.CheckIsWanted,
             'HasKillRight': stateSvc.CheckHasKillRight,
             'WreckViewed': stateSvc.CheckWreckViewed,
             'WreckEmpty': stateSvc.CheckWreckEmpty,
             'LimitedEngagement': stateSvc.CheckLimitedEngagement,
             'AlliesAtWar': stateSvc.CheckAlliesAtWar,
             'AgentInteractable': stateSvc.CheckAgentInteractable}
        return self.filterFuncs

    def CheckFiltered(self, slimItem, filtered, alwaysShow):
        stateSvc = sm.GetService('stateSvc')
        if len(filtered) + len(alwaysShow) > 3:
            ownerID = slimItem.ownerID
            if ownerID is None or ownerID == const.ownerSystem or idCheckers.IsNPC(ownerID):
                checkArgs = (slimItem, None)
            else:
                checkArgs = (slimItem, stateSvc._GetRelationship(slimItem))
        else:
            checkArgs = (slimItem,)
        functionDict = self.GetFilterFuncs()
        for functionName in alwaysShow:
            f = functionDict.get(functionName, None)
            if f is None:
                self.LogError('CheckFiltered got bad functionName: %r' % functionName)
                continue
            if f(*checkArgs):
                return False

        for functionName in filtered:
            f = functionDict.get(functionName, None)
            if f is None:
                self.LogError('CheckFiltered got bad functionName: %r' % functionName)
                continue
            if f(*checkArgs):
                return True

        return False

    def UpdateStates(self, slimItem, uiwindow):
        print 'Deprecated, TacticalSvc.UpdateStates, call UpdateFlagAndBackground on the uiwindow instead'

    def UpdateBackground(self, slimItem, uiwindow):
        print 'Deprecated, TacticalSvc.UpdateBackground, call on the uiwindow instead'

    def UpdateIcon(self, slimItem, uiwindow):
        print 'Deprecated, TacticalSvc.UpdateIcon, call UpdateIconColor on the uiwindow instead'

    def UpdateFlag(self, slimItem, uiwindow):
        print 'Deprecated, TacticalSvc.UpdateFlag, call on the uiwindow instead'

    def GetFlagUI(self, parent):
        print 'Deprecated, TacticalSvc.GetFlagUI, make the icon yourself'

    def UpdateFlagPositions(self, uiwindow, icon = None):
        print 'Deprecated, TacticalSvc.UpdateFlagPositions, call on the uiwindow instead'

    def MarkFlagsAsDirty(self):
        self.dirtyFlags.clear()
        self.flagsAreDirty = True

    def MarkFlagsForSpecificItemsAsDirty(self, itemIDs):
        self.dirtyFlags.update(itemIDs)

    @telemetry.ZONE_METHOD
    def FlagsDirtyCheckingLoop(self):
        while self.state == SERVICE_RUNNING:
            try:
                if self.flagsAreDirty:
                    self.flagsAreDirty = False
                    self.InvalidateFlags()
                elif self.dirtyFlags:
                    itemIDs = self.dirtyFlags
                    self.dirtyFlags = set()
                    self.InvalidateFlagsForSpecificItems(itemIDs)
            except Exception:
                log.LogException(extraText='Error invalidating tactical flags')
                sys.exc_clear()

            blue.pyos.synchro.SleepWallclock(500)

    def InvalidateFlags(self):
        if not eveCfg.InSpace():
            return
        sm.ScatterEvent('OnFlagsInvalidated', None)
        sm.GetService('bracket').RenewFlags()

    def InvalidateFlagsForSpecificItems(self, itemIDs):
        if not eveCfg.InSpace():
            return
        sm.ScatterEvent('OnFlagsInvalidated', itemIDs)
        sm.GetService('bracket').RenewFlagForItemIDs(itemIDs)

    def InvalidateFlagsExtraLimited(self, charID):
        if eveCfg.InSpace():
            sm.GetService('bracket').RenewSingleFlagForCharID(charID)

    def GetFilteredStatesFunctionNames(self, isBracket = False, presetName = None):
        return [ self.stateSvc.GetStateProps(flag).label for flag in self.overviewPresetSvc.GetFilteredStates(isBracket=isBracket, presetName=presetName) ]

    def GetAlwaysShownStatesFunctionNames(self, isBracket = False, presetName = None):
        return [ self.stateSvc.GetStateProps(flag).label for flag in self.overviewPresetSvc.GetAlwaysShownStates(isBracket=isBracket, presetName=presetName) ]

    def Get(self, what, default):
        if self.logme:
            self.LogInfo('Tactical::Get', what, default)
        return getattr(self, what, default)

    def OpenSettings(self, *args):
        uicore.cmd.OpenOverviewSettings()

    def ToggleOnOff(self):
        current = self.IsTacticalOverlayActive()
        if not current:
            self.ShowTacticalOverlay()
        elif self.tacticalOverlay.IsInitialized():
            self.HideTacticalOverlay()

    def HideTacticalOverlay(self):
        self._SetTacticalOverlayActive(False)
        self.TearDownOverlay()
        sm.ScatterEvent('OnTacticalOverlayChange')

    def _SetTacticalOverlayActive(self, isActive):
        cam = sm.GetService('sceneManager').GetActiveSpaceCamera()
        if cam.cameraID == evecamera.CAM_TACTICAL:
            settings.user.overview.Set('viewTactical_camTactical', isActive)
        elif cam.cameraID in (evecamera.CAM_SHIPORBIT, evecamera.CAM_SHIPORBIT_ABYSSAL_SPACE, evecamera.CAM_SHIPORBIT_HAZARD):
            settings.user.overview.Set('viewTactical', isActive)

    def ShowTacticalOverlay(self):
        if not self.IsTacticalOverlayAllowed():
            return
        self._SetTacticalOverlayActive(True)
        if not self.hideUI:
            self.tacticalOverlay.Initialize()
        sm.ScatterEvent('OnTacticalOverlayChange')

    def IsTacticalOverlayAllowed(self):
        cam = sm.GetService('sceneManager').GetActiveSpaceCamera()
        return cam.cameraID not in TACTICAL_OVERLAY_DISALLOWED_CAMERAS

    def IsTacticalOverlayActive(self):
        cameraID = self.viewState.GetView(ViewState.Space).GetRegisteredCameraID()
        if cameraID == evecamera.CAM_TACTICAL:
            return settings.user.overview.Get('viewTactical_camTactical', True)
        elif cameraID in TACTICAL_OVERLAY_DISALLOWED_CAMERAS:
            return False
        else:
            return settings.user.overview.Get('viewTactical', False)

    def CheckInit(self):
        if eveCfg.InSpace() and self.IsTacticalOverlayActive() and not self.hideUI:
            self.tacticalOverlay.Initialize()

    def TearDownOverlay(self):
        if self.targetingRanges:
            self.targetingRanges.KillTimer()
        self.tacticalOverlay.TearDown()

    def GetOverlay(self):
        return self.tacticalOverlay

    def ShowModuleRange(self, module, charge = None):
        if self._clearModuleTasklet is not None:
            self._clearModuleTasklet.kill()
        self._clearModuleTasklet = None
        self.tacticalOverlay.UpdateModuleRange(module, charge)

    def ClearModuleRange(self):

        def _task():
            blue.synchro.SleepSim(500)
            if self._clearModuleTasklet is not None:
                self._clearModuleTasklet = None
                self.tacticalOverlay.UpdateModuleRange()

        self._clearModuleTasklet = uthread.new(_task)

    def FindMaxRange(self, module, charge, dogmaLocation = None, *args):
        maxRange = 0
        falloffDist = 0
        bombRadius = 0
        cynoRadius = 0
        if not dogmaLocation:
            dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        try:
            effectID = self.clientDogmaStaticSvc.GetDefaultEffect(module.typeID)
        except KeyError:
            pass
        else:
            effect = self.clientDogmaStaticSvc.GetEffect(effectID)
            if effect.rangeAttributeID is not None:
                maxRange = dogmaLocation.GetAccurateAttributeValue(module.itemID, effect.rangeAttributeID)
                if module.groupID in falloffEffectivnessModuleGroups:
                    falloffDist = dogmaLocation.GetAccurateAttributeValue(module.itemID, const.attributeFalloffEffectiveness)
                else:
                    falloffDist = dogmaLocation.GetAccurateAttributeValue(module.itemID, const.attributeFalloff)

        if module.groupID == const.groupCynosuralField:
            isCovert = dogmaLocation.GetAttributeValue(module.itemID, const.attributeIsCovert)
            beaconRadius = 0.0
            if isCovert:
                beaconRadius = evetypes.GetRadius(const.typeCovertCynosuralFieldI)
            else:
                beaconRadius = evetypes.GetRadius(const.typeCynosuralFieldI)
            cynoRadius = dogmaLocation.GetAccurateAttributeValue(module.itemID, const.attributeCynosuralFieldSpawnRadius)
            cynoRadius += 2.0 * beaconRadius
        excludedChargeGroups = [const.groupScannerProbe, const.groupSurveyProbe]
        if not maxRange and charge and charge.groupID not in excludedChargeGroups:
            flightTime = dogmaLocation.GetAccurateAttributeValue(charge.itemID, const.attributeExplosionDelay)
            velocity = dogmaLocation.GetAccurateAttributeValue(charge.itemID, const.attributeMaxVelocity)
            bombRadius = dogmaLocation.GetAccurateAttributeValue(charge.itemID, const.attributeEmpFieldRange)
            maxRange = flightTime * velocity / 1000.0
            if dogmaLocation.dogmaStaticMgr.TypeHasAttribute(charge.typeID, const.attributeMaxFOFTargetRange):
                maxFofRange = dogmaLocation.GetAccurateAttributeValue(charge.itemID, dogma.const.attributeMaxFOFTargetRange)
                maxRange = min(maxRange, maxFofRange)
        return (maxRange,
         falloffDist,
         bombRadius,
         cynoRadius)

    def GetPanelForUpdate(self, what):
        panel = self.GetPanel(what)
        if panel and not panel.IsCollapsed() and not panel.IsMinimized():
            return panel

    def GetPanel(self, what):
        wnd = Window.GetIfOpen(what)
        if wnd and not wnd.destroyed:
            return wnd

    def InitDrones(self):
        if getattr(self, '_initingDrones', False):
            return
        self._initingDrones = True
        try:
            if not DronesWindow.GetIfOpen():
                DronesWindow.OpenBehindFullscreenViews(showActions=False, panelName=localization.GetByLabel('UI/Drones/Drones'))
        finally:
            self._initingDrones = False

    def OnOverviewTabsChanged(self):
        windowInstanceIDs = self.overviewPresetSvc.GetWindowInstanceIDs()
        self._CloseOverviewWindowsWithNoTabs(windowInstanceIDs)
        OpenOverview()

    def _CloseOverviewWindowsWithNoTabs(self, windowInstanceIDs):
        openWindows = uicore.registry.GetWindowsByClass(OverviewWindow)
        for wnd in openWindows:
            if wnd.windowInstanceID not in windowInstanceIDs:
                wnd.Close()

    def InitSelectedItem(self):
        if not SelectedItemWnd.GetIfOpen():
            SelectedItemWnd.OpenBehindFullscreenViews(panelname=localization.GetByLabel('UI/Inflight/ActiveItem/SelectedItem'))

    def InitConnectors(self):
        if self.logme:
            self.LogInfo('Tactical::InitConnectors')
        if not self.tacticalOverlay.IsInitialized():
            return
        self.tacticalOverlay.InitConnectors()

    def WantIt(self, slimItem, filtered = None, alwaysShown = None, isBracket = False):
        if not slimItem:
            return False
        if slimItem.typeID in INVISIBLE_TYPES:
            return False
        overviewOverride = self.overviewPresetSvc.GetOverrideState(slimItem)
        if overviewOverride is not None:
            return overviewOverride
        if isBracket and self.overviewPresetSvc.GetActiveBracketPresetName() in (None, overviewSettingsConst.BRACKET_FILTER_SHOWALL):
            return True
        if self.logme:
            self.LogInfo('Tactical::WantIt', slimItem)
        if slimItem.itemID == session.shipid:
            return isBracket
        filterGroups = self.overviewPresetSvc.GetValidGroups(isBracket=isBracket)
        if slimItem.groupID in filterGroups:
            if self.stateSvc.CheckIfFilterItem(slimItem) and self.CheckFiltered(slimItem, filtered, alwaysShown):
                return False
            return True
        return False

    def DoBallsAdded(self, *args, **kw):
        import stackless
        import blue
        t = stackless.getcurrent()
        timer = t.PushTimer(blue.pyos.taskletTimer.GetCurrent() + '::tactical')
        try:
            return self.DoBallsAdded_(*args, **kw)
        finally:
            t.PopTimer(timer)

    def DoBallsAdded_(self, lst):
        if not self or getattr(self, 'sr', None) is None:
            return
        uthread.pool('Tactical::DoBallsAdded', self._DoBallsAdded, lst)

    def _DoBallsAdded(self, lst):
        if not self or self.sr is None:
            return
        if self.logme:
            self.LogInfo('Tactical::DoBallsAdded', lst)
        self.LogInfo('Tactical - adding balls, num balls:', len(lst))
        inCapsule = 0
        mySlim = uix.GetBallparkRecord(eve.session.shipid)
        if mySlim and mySlim.groupID == const.groupCapsule:
            inCapsule = 1
        checkDrones = 0
        filtered = self.GetFilteredStatesFunctionNames()
        alwaysShown = self.GetAlwaysShownStatesFunctionNames()
        for each in lst:
            if each[1].itemID == eve.session.shipid:
                checkDrones = 1
            if not checkDrones and not inCapsule and each[1].categoryID == const.categoryDrone:
                drone = sm.GetService('michelle').GetDroneState(each[1].itemID)
                if drone and (drone.ownerID == eve.session.charid or drone.controllerID == eve.session.shipid):
                    checkDrones = 1
            if not self.WantIt(each[1], filtered, alwaysShown):
                continue
            self.tacticalOverlay.AddConnector(each[0], each[1])

        if checkDrones:
            droneview = self.GetPanel('droneview')
            if droneview:
                droneview.CheckReloadDronesScroll()
            else:
                self.CheckInitDrones()

    def OnDroneStateChange2(self, droneID, oldState, newState):
        self.InitDrones()
        droneview = self.GetPanel('droneview')
        if droneview:
            droneview.CheckReloadDronesScroll()

    def OnDroneControlLost(self, droneID):
        droneview = self.GetPanel('droneview')
        if droneview:
            droneview.CheckReloadDronesScroll()

    @telemetry.ZONE_METHOD
    def DoBallsRemove(self, pythonBalls, isRelease):
        for ball, slimItem, terminal in pythonBalls:
            self.DoBallRemove(ball, slimItem, terminal)

    def DoBallRemove(self, ball, slimItem, terminal):
        if not self or getattr(self, 'sr', None) is None:
            return
        if ball is None:
            return
        if not eveCfg.InSpace():
            return
        self.RemoveBallFromJammers(ball)
        if not self.GetDroneViewForSlimItem(slimItem) and not self.tacticalOverlay.HasConnector(ball.id):
            return
        if self.logme:
            self.LogInfo('Tactical::DoBallRemove', ball.id)
        uthread.pool('tactical::DoBallRemoveThread', self.DoBallRemoveThread, ball, slimItem, terminal)

    def GetDroneViewForSlimItem(self, slimItem):
        if slimItem.categoryID == const.categoryDrone and slimItem.ownerID == eve.session.charid:
            return self.GetPanel('droneview')

    def DoBallRemoveThread(self, ball, slimItem, terminal):
        self.tacticalOverlay.RemoveConnector(ball.id)
        droneview = self.GetDroneViewForSlimItem(slimItem)
        if droneview:
            droneview.CheckReloadDronesScroll()

    def OnEwarStart(self, sourceBallID, moduleID, targetBallID, jammingType):
        if not jammingType:
            self.LogError('Tactical::OnEwarStart', sourceBallID, jammingType)
            return
        if not hasattr(self, 'jammers'):
            self.jammers = {}
        if not hasattr(self, 'jammersByJammingType'):
            self.jammersByJammingType = {}
        if targetBallID == session.shipid:
            if sourceBallID not in self.jammers:
                self.jammers[sourceBallID] = {}
            self.jammers[sourceBallID][jammingType] = self.stateSvc.GetEwarFlag(jammingType)
            if jammingType not in self.jammersByJammingType:
                self.jammersByJammingType[jammingType] = set()
            self.jammersByJammingType[jammingType].add((sourceBallID, moduleID))
            sm.ScatterEvent('OnEwarStartFromTactical')

    def OnEwarEnd(self, sourceBallID, moduleID, targetBallID, jammingType):
        if not jammingType:
            self.LogError('Tactical::OnEwarEnd', sourceBallID, jammingType)
            return
        if not hasattr(self, 'jammers'):
            return
        if sourceBallID in self.jammers and jammingType in self.jammers[sourceBallID]:
            del self.jammers[sourceBallID][jammingType]
        if jammingType in self.jammersByJammingType and (sourceBallID, moduleID) in self.jammersByJammingType[jammingType]:
            self.jammersByJammingType[jammingType].remove((sourceBallID, moduleID))
        ewarId = (sourceBallID, moduleID, targetBallID)
        sm.ScatterEvent('OnEwarEndFromTactical', jammingType, ewarId)

    def OnEwarOnConnect(self, shipID, moduleID, moduleTypeID, targetID, guid, *args):
        if targetID != session.shipid:
            return
        if evetypes.GetCategoryID(moduleTypeID) == categoryEntity:
            ewarType = self.FindEwarTypeOnNpcFromGuid(moduleTypeID, guid)
        else:
            ewarType = self.FindEwarTypeFromModuleTypeID(moduleTypeID)
        if ewarType is not None:
            self.OnEwarStart(shipID, moduleID, targetID, ewarType)

    def FindEwarTypeFromModuleTypeID(self, moduleTypeID, *args):
        try:
            effectID = self.clientDogmaStaticSvc.GetDefaultEffect(moduleTypeID)
            return dogma.effects.GetEwarTypeByEffectID(effectID)
        except KeyError:
            pass

    def FindEwarTypeOnNpcFromGuid(self, entityTypeID, guid):
        effectID = None
        try:
            effects = self.godma.GetStateManager().GetEffectsByTypeID(entityTypeID)
            for effect in effects.itervalues():
                if effect.guid == guid:
                    if effectID is not None:
                        self.LogWarn('Entity=%s has multiple effects with same guid=%s - this will lead to dbuff icon conflict' % (entityTypeID, guid))
                    effectID = effect.effectID

            return dogma.effects.GetEwarTypeByEffectID(effectID)
        except KeyError:
            return effectID

    def GetEffectSourcesAndCountByJammingType(self, jammingType):
        effectSourcesSet = self.jammersByJammingType.get(jammingType, set())
        effectSources = defaultdict(int)
        for effectInfo in effectSourcesSet:
            sourceID, moduleID = effectInfo
            effectSources[sourceID] += 1

        return dict(effectSources)

    def ImportOverviewSettings(self, *args):
        ImportOverviewWindow.Open()

    def ExportOverviewSettings(self, *args):
        ExportOverviewWindow.Open()

    def OnEveGetsFocus(self, *args):
        pass

    def GetInBayDroneDamageTracker(self):
        dogmaLM = self.godma.GetDogmaLM()
        clientDogmaLM = sm.GetService('clientDogmaIM').GetDogmaLocation()
        if self.inBayDroneDamageTracker is None:
            self.inBayDroneDamageTracker = InBayDroneDamageTracker(dogmaLM, clientDogmaLM)
        else:
            self.inBayDroneDamageTracker.SetDogmaLM(dogmaLM)
        return self.inBayDroneDamageTracker
