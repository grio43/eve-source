#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\autopilot.py
import itertools
import sys
from collections import defaultdict
import utillib
from carbon.common.script.sys.service import Service
from carbon.common.script.util.timerstuff import AutoTimer
from eve.common.lib import appConst as const
from eve.client.script.ui.services.menuSvcExtras import movementFunctions
import destiny
import uthread
import blue
import log
import localization
import geo2
from carbonui import uiconst
from eve.client.script.ui.services.menuSvcExtras.movementFunctions import WarpToItem
from carbonui.uicore import uicore
from eve.common.script.sys import eveCfg, idCheckers
from eve.common.script.sys.idCheckers import IsTriglavianSystem
from eveexceptions import ExceptionEater, UserError
from eveservices.menu import GetMenuService
from structures import SERVICE_JUMP_BRIDGE
from stargate.client.jump_checks import check_cancel_stargate_jump
AUTO_NAVIGATION_LOOP_INTERVAL_MS = 2000

class AutoPilot(Service):
    __guid__ = 'svc.autoPilot'
    __exportedcalls__ = {'SetOn': [],
     'SetOff': [],
     'GetState': []}
    __notifyevents__ = ['OnBallparkCall',
     'OnSessionChanged',
     'OnRemoteMessage',
     'OnPlayerPodRespawn',
     'OnCharacterSessionChanged',
     'OnSessionReset',
     'OnMapShowsJumpGatesChanged']
    __dependencies__ = ['michelle',
     'starmap',
     'clientPathfinderService',
     'structureDirectory']

    def __init__(self):
        Service.__init__(self)
        self.updateTimer = None
        self.updateJumpGatesTimer = None
        self.autopilot = 0
        self.ignoreTimerCycles = 0
        self.isOptimizing = False
        self.__navigateSystemDestinationItemID = None
        self.__navigateSystemThread = None
        self.enabledTimestamp = 0
        uthread.new(self.UpdateWaypointsThread).context = 'autoPilot::UpdateWaypointsThread'

    def UpdateWaypointsThread(self):
        blue.pyos.synchro.SleepWallclock(2000)
        starmapSvc = sm.GetService('starmap')
        waypoints = starmapSvc.GetWaypoints()
        if len(waypoints):
            loopCounter = 0
            while loopCounter < 5 and (not sm.IsServiceRunning('clientPathfinderService') or not sm.GetService('clientPathfinderService').initialized):
                loopCounter += 1
                blue.pyos.synchro.SleepWallclock(1000)

            starmapSvc.SetWaypoints(waypoints)

    def Run(self, memStream = None):
        Service.Run(self, memStream)
        self.StartTimer()

    def DoLogAutopilotEvent(self, columnNames, *args):
        if sm.GetService('machoNet').GetGlobalConfig().get('disableAutopilotLogging', 0):
            return
        try:
            sm.ProxySvc('eventLog').LogClientEvent('autopilot', columnNames, *args)
        except UserError:
            pass

    def SetOn(self):
        if self.autopilot == 1:
            return
        if not eveCfg.InShip():
            return
        self.autopilot = 1
        self.CancelSystemNavigation()
        sm.ScatterEvent('OnAutoPilotOn')
        eve.Message('AutoPilotEnabled')
        self.KillTimer()
        self.StartTimer()
        self.LogNotice('Autopilot Enabled')
        self.enabledTimestamp = blue.os.GetWallclockTimeNow()
        with ExceptionEater('eventLog'):
            starmapSvc = sm.GetService('starmap')
            waypoints = starmapSvc.GetWaypoints()
            destinationID = waypoints[-1] if waypoints else None
            routeData = starmapSvc.GetAutopilotRoute()
            routeData = routeData or []
            solarSystemIDs = ','.join([ str(s) for s in routeData ])
            routeType = starmapSvc.GetRouteType()
            avoidPodKill = settings.char.ui.Get('pfAvoidPodKill', 0)
            avoidTriglavianTales = settings.char.ui.Get('pfAvoidTriglavianTales', 0)
            stopAtEachWaypoint = settings.user.ui.Get('autopilot_stop_at_each_waypoint', False)
            avoidSystems = settings.char.ui.Get('pfAvoidSystems', True)
            avoidanceItems = self.clientPathfinderService.GetAvoidanceItems()
            mandatoryAvoidanceItems = self.clientPathfinderService.GetMandatoryAvoidanceItems()
            securityPenalty = settings.char.ui.Get('pfPenalty', 50.0)
            uthread.new(self.DoLogAutopilotEvent, ['numWaypoints',
             'numJumps',
             'routeType',
             'avoidSystems',
             'avoidanceItems',
             'mandatoryAvoidanceItems',
             'securityPenalty',
             'avoidPodKill',
             'avoidTriglavianTales',
             'stopAtEachWaypoint',
             'destinationID',
             'celestialID...'], 'Enabled', len(waypoints), len(routeData), routeType, avoidSystems, ','.join([ str(i) for i in avoidanceItems ]), ','.join([ str(i) for i in mandatoryAvoidanceItems ]), securityPenalty, avoidPodKill, avoidTriglavianTales, stopAtEachWaypoint, destinationID, solarSystemIDs)

    def OnSessionChanged(self, isremote, session, change):
        self.KillTimer()
        self.ignoreTimerCycles = 3
        self.StartTimer()
        sm.GetService('starmap').UpdateRoute(fakeUpdate=True)

    def SetOff(self, reason = ''):
        if self.autopilot == 0:
            self.KillTimer()
            return
        sm.ScatterEvent('OnAutoPilotOff')
        self.autopilot = 0
        if reason == '  - waypoint reached':
            eve.Message('AutoPilotWaypointReached')
        elif reason == '  - no destination path set':
            eve.Message('AutoPilotDisabledNoPathSet')
        else:
            eve.Message('AutoPilotDisabled')
        self.LogNotice('Autopilot Disabled', reason)
        with ExceptionEater('eventLog'):
            starmapSvc = sm.GetService('starmap')
            numSeconds = (blue.os.GetWallclockTimeNow() - self.enabledTimestamp) / const.SEC
            uthread.new(self.DoLogAutopilotEvent, ['secondsEnabled', 'reason'], 'Disabled', numSeconds, reason)
        self.enabledTimestamp = 0

    def OnRemoteMessage(self, msgID, *args, **kwargs):
        if msgID == 'FleetWarp':
            self.LogInfo('Canceling auto navigation due to fleet warp detected')
            self.CancelSystemNavigation()

    def OnPlayerPodRespawn(self):
        self.CancelSystemNavigation()

    def OnBallparkCall(self, functionName, args):
        functions = ['GotoDirection', 'GotoPoint']
        if args[0] != eve.session.shipid:
            return
        cancelAutoNavigation = False
        if self.__navigateSystemDestinationItemID is None:
            pass
        elif functionName in {'GotoDirection', 'GotoPoint', 'Orbit'}:
            cancelAutoNavigation = True
        elif functionName == 'FollowBall' and self.__navigateSystemDestinationItemID != args[1]:
            cancelAutoNavigation = True
        elif functionName == 'WarpTo':
            bp = sm.GetService('michelle').GetBallpark()
            autoNavigationBall = bp.GetBall(self.__navigateSystemDestinationItemID)
            if autoNavigationBall:
                navDstVector = (autoNavigationBall.x, autoNavigationBall.y, autoNavigationBall.z)
                dstVector = args[1:-2]
                if navDstVector and dstVector and geo2.Vec3DistanceD(navDstVector, dstVector) - autoNavigationBall.radius > const.minWarpDistance:
                    cancelAutoNavigation = True
        if cancelAutoNavigation:
            self.LogInfo('Canceling auto navigation to', self.__navigateSystemDestinationItemID, 'as a respons to OnBallparkCall:', functionName, args)
            self.CancelSystemNavigation()
        if functionName in functions:
            if functionName == 'GotoDirection' and self.gotoCount > 0:
                self.gotoCount = 0
                self.LogInfo('Autopilot gotocount set to 0')
                return
            if self.gotoCount == 0:
                waypoints = sm.GetService('starmap').GetWaypoints()
                if waypoints and self.IsStationOrStructure(waypoints[-1]):
                    return
            self.SetOff(functionName + str(args))
            self.LogInfo('Autopilot stopped gotocount is ', self.gotoCount)

    def GetState(self):
        return self.autopilot

    def Stop(self, stream):
        self.KillTimer()
        Service.Stop(self)

    def KillTimer(self):
        self.updateTimer = None

    def StartTimer(self):
        self.gotoCount = 0
        self.updateTimer = AutoTimer(2000, self.Update)
        self.updateJumpGatesTimer = AutoTimer(const.HOUR / const.MSEC, self.UpdateJumpGatesTimerThread)

    def IsStationOrStructure(self, itemID):
        if idCheckers.IsSolarSystem(itemID):
            return False
        return idCheckers.IsStation(itemID) or self.structureDirectory.GetStructureInfo(itemID) is not None

    def GetGateOrStationID(self, bp, destinationID):
        if idCheckers.IsSolarSystem(destinationID):
            gateID = self._GetGateIDToSolarsystem(destinationID)
            if gateID:
                return gateID
        if idCheckers.IsStation(destinationID):
            return destinationID
        slimItem = bp.GetInvItem(destinationID)
        if slimItem and slimItem.categoryID == const.categoryStructure:
            return destinationID
        return self.GetGateOrStation(bp, destinationID)[0]

    def _GetGateIDToSolarsystem(self, destinationID):
        fromLocationID = session.solarsystemid2
        return self.GetGateIDToSolarsystemFromLocationID(destinationID, fromLocationID)

    def GetGateIDToSolarsystemFromLocationID(self, destinationID, fromLocationID, addWarning = True):
        try:
            destGateIds = cfg.mapSolarSystemContentCache[destinationID].stargates.keys()
            for sgid, sg in cfg.mapSolarSystemContentCache[fromLocationID].stargates.iteritems():
                if sg.destination in destGateIds:
                    return sgid

            if addWarning:
                self.LogWarn('Autopilot: _GetGateIDToSolarsystem, did not find gate for destination', destinationID, fromLocationID)
        except StandardError:
            self.LogException()

    def GetGateOrStation(self, bp, destinationID, addWarning = True):
        for solarsystemItem in sm.GetService('map').GetSolarsystemItems(session.solarsystemid2, False):
            ballID = solarsystemItem.itemID
            slimItem = bp.GetInvItem(ballID)
            if slimItem is None:
                continue
            if slimItem.groupID == const.groupStargate and destinationID in map(lambda x: x.locationID, slimItem.jumps):
                return (ballID, slimItem)
            if slimItem.groupID == const.groupUpwellJumpGate:
                if destinationID == getattr(slimItem, 'targetSolarsystemID', None):
                    return (ballID, slimItem)
            elif destinationID == slimItem.itemID:
                return (ballID, slimItem)

        if addWarning:
            self.LogWarn('Autopilot: GetGateOrStation, did not find destination', destinationID, session.solarsystemid2)
        return (None, None)

    def GetDestinationItemID(self):
        destinationPath = sm.GetService('starmap').GetDestinationPath()
        if len(destinationPath) > 0:
            nextItemInRoute = destinationPath[0]
            ballpark = sm.GetService('michelle').GetBallpark()
            if ballpark and session.solarsystemid and ballpark.solarsystemID == session.solarsystemid:
                destinationID, _ = self.GetGateOrStation(ballpark, nextItemInRoute, addWarning=False)
                return destinationID

    def Update(self):
        if self.autopilot == 0:
            self.KillTimer()
            return
        if self.ignoreTimerCycles > 0:
            self.ignoreTimerCycles -= 1
            return
        if not session.IsItSafe():
            self.LogInfo('returning as it is not safe')
            return
        if not session.rwlock.IsCool():
            self.LogInfo("returning as the session rwlock isn't cool")
            return
        if not eveCfg.InShip():
            return
        starmapSvc = sm.GetService('starmap')
        destinationPath = starmapSvc.GetDestinationPath()
        if len(destinationPath) == 0:
            self.SetOff('  - no destination path set')
            return
        if destinationPath[0] is None:
            if not starmapSvc.GetWaypoints():
                self.SetOff('  - no destination path set')
            else:
                self.SetOff('  - destination not in expected system.')
            return
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return
        if sm.GetService('jumpQueue').IsJumpQueued():
            return
        ship = bp.GetBall(session.shipid)
        if ship is None:
            return
        if ship.mode == destiny.DSTBALL_WARP:
            return
        if bp.solarsystemID != session.solarsystemid:
            self.LogError('autopilot - waiting a bit as we have not updated the ballpark', session.solarsystemid, bp.solarsystemID)
            return
        destID, destItem = self.GetGateOrStation(bp, destinationPath[0])
        if destID is None:
            if len(destinationPath) == 1:
                self.SetOff('  - destination not in expected system.')
            return
        jumpingToCelestial = not idCheckers.IsSolarSystem(destinationPath[0])
        theJump = None
        if not jumpingToCelestial:
            for jump in destItem.jumps:
                if destinationPath[0] == jump.locationID:
                    theJump = jump
                    break

            if destinationPath[0] and destinationPath[0] == getattr(destItem, 'targetSolarsystemID', None):
                theJump = utillib.KeyVal(locationID=destItem.targetSolarsystemID, toCelestialID='-1')
        if theJump is None and not jumpingToCelestial:
            return
        approachObject = bp.GetBall(destID)
        if approachObject is None:
            return
        if jumpingToCelestial:
            jumpToLocationName = cfg.evelocations.Get(destinationPath[0]).name
        else:
            jumpToLocationName = cfg.evelocations.Get(theJump.locationID).name
        shipDestDistance = bp.GetSurfaceDist(ship.id, destID)
        if shipDestDistance < const.maxStargateJumpingDistance and not jumpingToCelestial:
            if not self._IsSessionAndBpSafeToJump(bp, ship):
                return
            try:
                self.LogNotice('Autopilot jumping from', destID, 'to', theJump.toCelestialID, '(', jumpToLocationName, ')')
                if not jumpingToCelestial:
                    if check_cancel_stargate_jump(destID, theJump.locationID, exclude_checks=['illicit_goods']):
                        self.SetOff()
                        return
                if destItem.groupID == const.groupUpwellJumpGate:
                    didJumpThrough = sm.GetService('sessionMgr').PerformSessionChange('autopilot', sm.RemoteSvc('structureJumpBridgeMgr').CmdJumpThroughStructureStargate, destID)
                    if not didJumpThrough:
                        self.SetOff()
                        return
                else:
                    gateRestricted = sm.GetService('gatejump').CheckForGateRestriction(session.solarsystemid, destID)
                    if gateRestricted:
                        self.SetOff('  - Gate Restricted')
                        return
                    sm.GetService('sessionMgr').PerformSessionChange('autopilot', sm.GetService('michelle').GetRemotePark().CmdStargateJump, destID, theJump.toCelestialID, session.shipid)
                eve.Message('AutoPilotJumping', {'what': jumpToLocationName})
                sm.ScatterEvent('OnAutoPilotJump')
                if IsTriglavianSystem(theJump.locationID):
                    self.ignoreTimerCycles = 13
                else:
                    self.ignoreTimerCycles = 5
            except UserError as e:
                self._HandleJumpUserErrors(e, destID, jumpToLocationName)
            except:
                sys.exc_clear()
                self.LogError('Autopilot: jumping to ' + jumpToLocationName + ' failed. Will try again')
                self.ignoreTimerCycles = 5

            return
        if shipDestDistance < const.maxStargateJumpingDistance and destItem.groupID == const.groupUpwellJumpGate:
            if not self._IsSessionAndBpSafeToJump(bp, ship):
                return
            try:
                didJumpThrough = sm.GetService('menu').ReallyJumpThroughStructureJumpBridge(destID)
                self.ignoreTimerCycles = 5
                if didJumpThrough:
                    eve.Message('AutoPilotJumping', {'what': jumpToLocationName})
                    sm.ScatterEvent('OnAutoPilotJump')
                else:
                    self.SetOff()
            except UserError as e:
                self._HandleJumpUserErrors(e, destID, jumpToLocationName)
            except:
                sys.exc_clear()
                self.LogError('Autopilot: jumping to ' + jumpToLocationName + ' failed. Will try again')
                self.ignoreTimerCycles = 5

            return
        if jumpingToCelestial and shipDestDistance < const.maxDockingDistance and self.IsStationOrStructure(destID):
            if self.__navigateSystemDestinationItemID != destID:
                if shipDestDistance > 2500:
                    sm.GetService('audio').AudioMessage('msg_AutoPilotApproachingStation_play')
                GetMenuService().Dock(destID)
                self.ignoreTimerCycles = 5
        elif shipDestDistance < const.minWarpDistance:
            if ship.mode == destiny.DSTBALL_FOLLOW and ship.followId == destID:
                return
            self.AP_ApproachDestID(destID, jumpingToCelestial)
        else:
            self.AP_WarpToDestID(destID, jumpToLocationName, jumpingToCelestial)

    def _IsSessionAndBpSafeToJump(self, bp, ship):
        if ship.isCloaked:
            return False
        if session.mutating:
            self.LogInfo('session is mutating')
            return False
        if session.changing:
            self.LogInfo('session is changing')
            return False
        if bp.solarsystemID != session.solarsystemid:
            self.LogInfo('bp.solarsystemid is not solarsystemid')
            return False
        if sm.GetService('michelle').GetRemotePark()._Moniker__bindParams != session.solarsystemid:
            self.LogInfo('remote park moniker bindparams is not solarsystemid')
            return False
        return True

    def _HandleJumpUserErrors(self, e, destID, jumpToLocationName):
        if e.msg in ('SystemCheck_JumpFailed_Stuck', 'CantJumpEmanationLockedToAnotherGate'):
            self.SetOff()
            raise
        elif e.msg.startswith('SystemCheck_JumpFailed_'):
            eve.Message(e.msg, e.dict)
            if e.msg == 'SystemCheck_JumpFailed_StandingsTooLow':
                self.SetOff()
                raise
        elif e.msg == 'NotCloseEnoughToJump':
            park = sm.GetService('michelle').GetRemotePark()
            park.CmdSetSpeedFraction(1.0)
            if uicore.layer.shipui.isopen:
                uicore.layer.shipui.SetSpeed(1.0)
            park.CmdFollowBall(destID, 0.0)
            self.LogWarn("Autopilot: I thought I was close enough to jump, but I wasn't.")
        elif e.msg in ('JumpNotEnoughCharge3', 'StructureServiceUnavailable', 'CannotUseJumpGateShipTooHeavy', 'NoLinkToDestination'):
            self.SetOff()
            raise
        sys.exc_clear()
        self.LogError('Autopilot: jumping to ' + jumpToLocationName + ' failed. Will try again')
        self.ignoreTimerCycles = 5

    def AP_ApproachDestID(self, destinationID, isFinal):
        self.CancelSystemNavigation()
        park = sm.GetService('michelle').GetRemotePark()
        park.CmdSetSpeedFraction(1.0)
        if uicore.layer.shipui.isopen:
            uicore.layer.shipui.SetSpeed(1.0)
        park.CmdFollowBall(destinationID, 0.0)
        eve.Message('AutoPilotApproaching')
        if not (isFinal and self.IsStationOrStructure(destinationID)):
            sm.GetService('audio').AudioMessage('msg_AutoPilotApproaching_play')
        self.LogInfo('Autopilot: approaching')
        self.ignoreTimerCycles = 2

    def AP_WarpToDestID(self, destinationID, name, isFinal):
        try:
            sm.GetService('space').WarpDestination(celestialID=destinationID)
            sm.GetService('michelle').GetRemotePark().CmdWarpToStuffAutopilot(destinationID)
            eve.Message('AutoPilotWarpingTo', {'what': name})
            if isFinal:
                if self.IsStationOrStructure(destinationID):
                    sm.GetService('audio').AudioMessage('msg_AutoPilotWarpingToStation_play')
                self.LogInfo('Autopilot: warping to celestial object', destinationID)
            else:
                sm.GetService('audio').AudioMessage('msg_AutoPilotWarpingTo_play')
                self.LogInfo('Autopilot: warping to gate')
            sm.ScatterEvent('OnAutoPilotWarp')
            self.ignoreTimerCycles = 2
        except UserError as e:
            sys.exc_clear()
            item = sm.GetService('godma').GetItem(session.shipid)
            if item.warpScrambleStatus > 0:
                self.SetOff('Autopilot cannot warp while warp scrambled.')
            if 'WarpDisrupted' in e.msg:
                self.SetOff('Autopilot cannot warp while warp scrambled by bubble.')
        except StandardError:
            self.SetOff('Unknown error')

    def NavigateSystemTo(self, itemID, interactionRange, commandFunc, *args, **kwargs):
        self.LogInfo('Navigate to item', itemID, 'range', interactionRange, 'and execute', commandFunc)
        self.__navigateSystemDestinationItemID = itemID
        self.__navigateSystemThread = AutoTimer(50, self.__NavigateSystemTo, itemID, interactionRange, commandFunc, *args, **kwargs)

    def CancelSystemNavigation(self):
        self.LogInfo('Cancel system navigation')
        self.__navigateSystemDestinationItemID = None
        self.__navigateSystemThread = None

    def IsSystemNavigationComplete(self, itemID, interactionRange):
        return not self.InWarp() and self.InInteractionRange(itemID, interactionRange) and not self.IsCloaked()

    def __NavigateSystemTo(self, itemID, interactionRange, commandFunc, *args, **kwargs):
        try:
            if self.InWarp():
                pass
            elif self.InInteractionRange(itemID, interactionRange) and not self.IsCloaked():
                self.LogInfo('System navigation: at target location. Triggering action')
                try:
                    commandFunc(*args, **kwargs)
                except UserError:
                    raise
                finally:
                    self.CancelSystemNavigation()

            elif self.InWarpRange(itemID):
                self.LogInfo('System navigation: warping to target', itemID, interactionRange)
                WarpToItem(itemID, warpRange=const.minWarpEndDistance, cancelAutoNavigation=False)
            elif self.IsApproachable(itemID):
                movementFunctions.ShipApproach(itemID, cancelAutoNavigation=False)
            else:
                self.LogInfo('Unable to resolve the proper navigation action. Aborting.', itemID, interactionRange, commandFunc)
                self.CancelSystemNavigation()
            if self.__navigateSystemThread:
                self.__navigateSystemThread.interval = AUTO_NAVIGATION_LOOP_INTERVAL_MS
        except UserError as e:
            self.LogInfo('User error detected', e.msg, itemID, interactionRange, commandFunc)
            raise
        except Exception as e:
            if isinstance(e, RuntimeError) and e.args[0] in ('MonikerSessionCheckFailure', 'Ship reattaching while in process of departing', 'Missing shipid', 'User not in any solar system'):
                self.LogInfo('Exception ignored due to session changing while still trying to navigate.', itemID, interactionRange, commandFunc)
            else:
                self.LogError('Problem while navigating system', itemID, interactionRange, commandFunc)
                log.LogException(channel=self.__guid__)
            self.CancelSystemNavigation()

    def IsApproachable(self, itemID):
        destBall = self.michelle.GetBall(itemID)
        if destBall is not None and destBall.surfaceDist < const.minWarpDistance:
            return True
        return False

    def InInteractionRange(self, itemID, interactionRange):
        destBall = self.michelle.GetBall(itemID)
        if destBall is not None and destBall.surfaceDist < interactionRange:
            return True
        return False

    def InWarp(self):
        shipBall = self.michelle.GetBall(session.shipid)
        if shipBall is not None and shipBall.mode == destiny.DSTBALL_WARP:
            return True
        return False

    def InWarpRange(self, itemID):
        destBall = self.michelle.GetBall(itemID)
        if destBall is not None and destBall.surfaceDist > const.minWarpDistance:
            return True
        return False

    def IsCloaked(self):
        shipBall = self.michelle.GetBall(session.shipid)
        if shipBall is not None:
            return bool(shipBall.isCloaked)
        return False

    def OnCharacterSessionChanged(self, _oldCharacterID, newCharacterID):
        if newCharacterID is not None:
            self.updateJumpGatesTimer = AutoTimer(const.HOUR / const.MSEC, self.UpdateJumpGatesTimerThread)

    def OnSessionReset(self):
        if self.updateJumpGatesTimer:
            self.updateJumpGatesTimer.KillTimer()
        self.updateJumpGatesTimer = None

    def UpdateJumpGatesTimerThread(self):
        if not settings.char.ui.Get('pathFinder_includeJumpGates', False):
            return
        with ExceptionEater('UpdateJumpGatesTimerThread'):
            self.VerifyJumpGatesInRoute()

    def FindJumpGatesInRoute(self):
        starmapSvc = sm.GetService('starmap')
        path = starmapSvc.GetRouteFromWaypoints(starmapSvc.GetWaypoints())
        if len(path) < 2:
            return []
        lastKnownJumpGates = self.clientPathfinderService.GetLastKnownJumpGates()
        potentialJumpGatePairs = []
        for fromLocationID, toLocationID in itertools.izip(path, path[1:]):
            if (fromLocationID, toLocationID) in lastKnownJumpGates:
                potentialJumpGatePairs.append((fromLocationID, toLocationID))

        jumpGatesInRoute = []
        for fromLocationID, toLocationID in potentialJumpGatePairs:
            if not self.GetGateIDToSolarsystemFromLocationID(toLocationID, fromLocationID):
                jGate = lastKnownJumpGates.get((fromLocationID, toLocationID), None)
                if jGate:
                    jumpGatesInRoute.append(jGate)

        return jumpGatesInRoute

    def VerifyJumpGatesInRoute(self):
        with ExceptionEater('VerifyJumpGatesInRoute'):
            if not settings.char.ui.Get('pathFinder_includeJumpGates', False):
                return
            jumpGates = self.FindJumpGatesInRoute()
            structureServicesSvc = sm.GetService('structureServices')
            needsRefresh = False
            for jGate in jumpGates:
                availableServices = structureServicesSvc.CharacterGetServices(jGate)
                if SERVICE_JUMP_BRIDGE not in availableServices:
                    needsRefresh = True
                    break

            if needsRefresh:
                self.UpdateJumpGatesAndRoute()

    def UpdateJumpGatesAndRoute(self):
        self.clientPathfinderService.UpdateJumpGates()
        sm.GetService('autoPilot').OptimizeRoute()

    def OnMapShowsJumpGatesChanged(self):
        self.UpdateJumpGatesAndRoute()

    def OptimizeRoute(self, *args):
        if self.isOptimizing:
            return
        try:
            self.isOptimizing = True
            starmapSvc = sm.GetService('starmap')
            waypoints = list(starmapSvc.GetWaypoints())
            originalWaypointsLen = len(waypoints)
            isReturnTrip = False
            for idx in reversed(xrange(len(waypoints))):
                if waypoints[idx] == eve.session.solarsystemid2:
                    del waypoints[idx]
                    isReturnTrip = True
                    break

            solarSystemToStations = defaultdict(list)
            for i, waypoint in enumerate(waypoints):
                if self.IsStationOrStructure(waypoint):
                    if idCheckers.IsStation(waypoint):
                        solarSystemID = cfg.stations.Get(waypoint).solarSystemID
                    else:
                        solarSystemID = self.structureDirectory.GetStructureInfo(waypoint).solarSystemID
                    solarSystemToStations[solarSystemID].append(waypoint)
                    waypoints[i] = solarSystemID

            waypoints = list(set(waypoints))
            if session.solarsystemid2 in waypoints:
                waypoints.remove(session.solarsystemid2)
            numWaypoints = len(waypoints)
            if numWaypoints == 0:
                return
            msg = None
            if numWaypoints > 12:
                msg = 'UI/Map/MapPallet/msgOptimizeQuestion1'
            elif numWaypoints > 10:
                msg = 'UI/Map/MapPallet/msgOptimizeQuestion2'
            if msg:
                yesNo = eve.Message('AskAreYouSure', {'cons': localization.GetByLabel(msg, numWaypoints=originalWaypointsLen)}, uiconst.YESNO)
                if yesNo != uiconst.ID_YES:
                    return
            distance = {}
            waypoints.append(eve.session.solarsystemid2)
            for fromID in waypoints:
                distance[fromID] = {}
                for toID in waypoints:
                    if fromID == toID:
                        continue
                    distance[fromID][toID] = self.clientPathfinderService.GetAutopilotJumpCount(toID, fromID)

            waypoints.pop()
            startTime = blue.os.GetWallclockTimeNow()
            prefix = [None]
            _push = prefix.append
            _pop = prefix.pop

            def FindShortestRoute(prefix, distanceSoFar, toID):
                distanceTo = distance[toID]
                prefix[-1] = toID
                shortestDist = shortestRouteSoFar[0]
                if len(prefix) < numWaypoints:
                    _push(None)
                    for i in indexes:
                        toID = waypoints[i]
                        if not toID:
                            continue
                        candidateDist = distanceSoFar + distanceTo[toID]
                        if candidateDist >= shortestDist:
                            continue
                        waypoints[i] = None
                        FindShortestRoute(prefix, candidateDist, toID)
                        waypoints[i] = toID

                    _pop()
                else:
                    for i in indexes:
                        toID = waypoints[i]
                        if not toID:
                            continue
                        candidateDist = distanceSoFar + distanceTo[toID]
                        if candidateDist < shortestDist:
                            shortestRouteSoFar[:] = [candidateDist, prefix[:], toID]
                            shortestDist = candidateDist

            shortestRouteSoFar = [999999999, None, None]
            indexes = range(len(waypoints))
            FindShortestRoute(prefix, 0, eve.session.solarsystemid2)
            distance, waypoints, last = shortestRouteSoFar
            if waypoints is not None and waypoints[0] == eve.session.solarsystemid2:
                waypoints = waypoints[1:]
            blue.pyos.synchro.SleepWallclock(1)
            if waypoints is None:
                raise UserError('AutoPilotDisabledUnreachable')
            waypoints.append(last)
            waypointsWithStations = []
            for waypoint in waypoints:
                if waypoint in solarSystemToStations:
                    waypointsWithStations.extend(solarSystemToStations[waypoint])
                else:
                    waypointsWithStations.append(waypoint)

            if isReturnTrip == True:
                sm.GetService('starmap').SetWaypoints(waypointsWithStations + [session.solarsystemid2])
            else:
                sm.GetService('starmap').SetWaypoints(waypointsWithStations)
        finally:
            self.isOptimizing = False

    def _GetNextItemIDInRoute(self):
        destinationPath = sm.GetService('starmap').GetDestinationPath()
        if destinationPath:
            return destinationPath[0]

    def GetNextItemIDInRoute(self):
        itemID = self._GetNextItemIDInRoute()
        if not itemID:
            return
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return
        for slimItem in bp.slimItems.values():
            if slimItem.jumps and slimItem.jumps[0].locationID == itemID:
                return slimItem.itemID
            if slimItem.itemID == itemID:
                return itemID
