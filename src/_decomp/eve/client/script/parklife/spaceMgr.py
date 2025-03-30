#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\spaceMgr.py
import logging
import math
import sys
import blue
import destiny
import eve.client.script.environment.spaceObject.repository as repository
import eve.client.script.environment.spaceObject.spaceObject as spaceObject
import eveaudio
import evegraphics.settings as gfxsettings
import evetypes
import fsdBuiltData.common.graphicIDs as fsdGraphicIDs
import geo2
import localization
import log
import telemetry
import trinity
import uthread
from carbon.common.script.sys.service import Service
from carbon.common.script.util import timerstuff
from carbon.common.script.util.commonutils import IsFullLogging
from carbon.common.script.util.exceptionEater import ExceptionEater
from carbon.common.script.util.format import FmtDate, FmtDist
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.uicore import uicore
from eve.client.script.parklife import states as state
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.util import uix
from eve.client.script.ui.view import hangarRegistry
from eve.client.script.ui.view.viewStateConst import ViewState
from eve.common.lib import appConst as const
from eve.common.script.sys import idCheckers
from eve.common.script.sys.eveCfg import IsControllingStructure
from eveservices.menu import GetMenuService
from spacecomponents.client.messages import MSG_ON_LOAD_OBJECT
from cosmetics.common.ships.skins.static_data.skin_type import ShipSkinType
stdlog = logging.getLogger(__name__)
DEGREES_15 = 0.26
SOLARSYSTEM_VISUALEFFECT_ENVIRONMENT_ID = {'SHATTEREDWORMHOLE_OVERLAY': 3}
BALL_CLOSE_DISTANCE = 0
BALL_APPROACH_DISTANCE = 1
BALL_ALIGN_DISTANCE = 2
BALL_ALIGN_DISTANCE_ALIGNED = 3
CAPTION_TOP = 14

class SpaceMgr(Service):
    __guid__ = 'svc.space'
    __update_on_reload__ = 0
    __exportedcalls__ = {'StartPartitionDisplayTimer': [],
     'StopPartitionDisplayTimer': [],
     'WarpDestination': [],
     'IndicateWarp': [],
     'StartWarpIndication': [],
     'StopWarpIndication': []}
    __notifyevents__ = ['DoBallsAdded',
     'DoBallRemove',
     'OnDamageStateChange',
     'OnSpecialFX',
     'OnDockingAccepted',
     'ProcessSessionChange',
     'OnBallparkCall',
     'OnWormholeJumpCancel',
     'DoBallsRemove',
     'OnRemoteMessage']
    __dependencies__ = ['michelle',
     'FxSequencer',
     'transmission',
     'settings',
     'stateSvc',
     'sceneManager',
     'audio',
     'cosmeticsSvc']

    def __init__(self):
        super(SpaceMgr, self).__init__()
        self.warpDestinationCache = [None,
         None,
         None,
         None,
         None]
        self.lazyLoadQueueCount = 0
        self.maxTimeInDoBallsAdded = 10 * const.MSEC
        self.prioritizedIDs = set()
        self.planetManager = PlanetManager()
        self.environments = {}
        self.unloadables = set()
        self.npcStations = cfg.mapSolarSystemContentCache.npcStations
        self.environmentTemplateLoadingThread = None

    def Run(self, memStream = None):
        super(SpaceMgr, self).Run(memStream)
        sm.FavourMe(self.DoBallsAdded)
        for each in uicore.layer.shipui.children[:]:
            if each.name in ('caption', 'indicationtext'):
                each.Close()

        self.indicationtext = None
        self.setIndicationText = None
        self.caption = None
        self.captionProgressbar = None
        self.indicateTimer = timerstuff.AutoTimer(250, self.Indicate_thread)
        self.unloadableTimer = timerstuff.AutoTimer(1000, self.HandleUnloadables)
        self.shortcutText = None
        self.shortcutSubText = None
        self.shortcutClearThread = None

    def Stop(self, stream):
        self.ClearIndicateText()
        self.ClearShortcutText()
        self.indicateTimer.KillTimer()
        self.indicateTimer = None
        self.unloadableTimer.KillTimer()
        self.unloadableTimer = None
        super(SpaceMgr, self).Stop()

    def ProcessSessionChange(self, isRemote, session, change):
        self.ClearIndicateText()
        self.ClearShortcutText()

    def OnWormholeJumpCancel(self):
        self.ClearIndicateText()
        self.ClearShortcutText()
        eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Wormholes/EnterCollapsed')})

    def GetTypeData(self, slimItem):
        data = {}
        data['slimItem'] = slimItem
        data['typeID'] = slimItem.typeID
        data['groupID'] = slimItem.groupID
        data['typeName'] = evetypes.GetEnglishName(slimItem.typeID)
        skin = sm.GetService('cosmeticsSvc').GetCachedAppliedSkinState(licenseeID=slimItem.charID, itemID=slimItem.itemID)
        station = self.npcStations.get(slimItem.itemID, None)
        if station:
            data['graphicID'] = station.graphicID
        else:
            data['graphicID'] = evetypes.GetGraphicID(slimItem.typeID)
        graphicID = data['graphicID']
        graphicInfo = fsdGraphicIDs.GetGraphic(graphicID)
        data['graphicFile'] = fsdGraphicIDs.GetGraphicFile(graphicInfo)
        data['animationStateObjects'] = fsdGraphicIDs.GetAnimationStateObjects(graphicInfo, default={})
        data['sofRaceName'] = fsdGraphicIDs.GetSofRaceName(graphicInfo)
        data['sofFactionName'] = fsdGraphicIDs.GetSofFactionName(graphicInfo)
        dunRotation = getattr(slimItem, 'dunRotation', None)
        data['dunRotation'] = dunRotation
        dunDirection = getattr(slimItem, 'dunDirection', None)
        data['dunDirection'] = dunDirection
        return data

    @telemetry.ZONE_METHOD
    def LoadObject(self, ball, slimItem, ob):
        try:
            if slimItem is None:
                return
            if getattr(ob, 'released', 1):
                self.LogWarn(slimItem.itemID, 'has already been released')
                return
            if getattr(ob, '__unloadable__', False):
                self.unloadables.add(slimItem.itemID)
                return
            ob.Prepare()
        except StandardError:
            log.LogException('Error adding SpaceObject (%s, %s, %s) of type %s to scene' % (str(ball),
             str(slimItem),
             str(ob),
             str(getattr(ob, '__klass__', ''))))
            sys.exc_clear()
        finally:
            ob.UnblockModelEvent()

        self._NotifyComponents(ball)

    def _NotifyComponents(self, ball):
        bp = self.michelle.GetBallpark()
        if bp:
            bp.GetComponentRegistry().SendMessageToItem(ball.id, MSG_ON_LOAD_OBJECT, ball)

    def HandleUnloadables(self):
        with ExceptionEater('HandleUnloadables'):
            if not self.unloadables:
                return
            ballpark = self.michelle.GetBallpark()
            if not ballpark or not ballpark.ego:
                return
            for ballID in list(self.unloadables):
                ball = ballpark.GetBall(ballID)
                if not ball:
                    self.unloadables.discard(ballID)
                    continue
                with ExceptionEater('HandleUnloadable'):
                    visible = ballpark.IsBallVisible(ballID)
                    unloaded = getattr(ball, 'unloaded', True)
                    if visible and unloaded:
                        if getattr(ball, 'released', False):
                            ball.released = False
                        ball.unloaded = False
                        ball.Prepare()
                        self._NotifyComponents(ball)
                    elif not visible and not unloaded:
                        ball.unloaded = True
                        ball.Release()
                blue.pyos.BeNice()

    @telemetry.ZONE_METHOD
    def DoBallsAdded(self, *args, **kw):
        lst = []
        ballsToAdd = args[0]
        for ball, slimItem in ballsToAdd:
            try:
                groupID = slimItem.groupID
                categoryID = slimItem.categoryID
                klass = repository.GetClass(groupID, categoryID)
                if klass is None:
                    self.LogError('SpaceObject class not specified for group: ', groupID, '- defaulting to basic SpaceObject')
                    klass = spaceObject.SpaceObject
                typeData = self.GetTypeData(slimItem)
                ob = klass(ball, initDict={'typeData': typeData})
                ob.SetServices(self, sm)
                if groupID == const.groupPlanet or groupID == const.groupMoon:
                    self.planetManager.RegisterPlanetBall(ob)
                elif groupID == const.groupSun:
                    self.planetManager.RegisterSunBall(ob)
                lst.append((ball, slimItem, ob))
                if ball.id == session.shipid and ball.mode == destiny.DSTBALL_WARP:
                    self.OnBallparkCall('WarpTo', (ball.id,
                     ball.gotoX,
                     ball.gotoY,
                     ball.gotoZ))
                    self.FxSequencer.OnSpecialFX(ball.id, None, None, None, None, 'effects.Warping', 0, 1, 0)
            except Exception:
                self.LogError('DoBallsAdded - failed to add ball', (ball, slimItem))
                log.LogException()
                sys.exc_clear()

        if settings.public.generic.Get('lazyLoading', 1):
            uthread.new(self.DoBallsAdded_, lst)
        else:
            self.DoBallsAdded_(lst)

    @telemetry.ZONE_METHOD
    def SplitListByThreat(self, bp, ballsToAdd):
        threatening = []
        nonThreatening = []
        numLostBalls = 0
        for each in ballsToAdd:
            ball, slimItem, ob = each
            itemID = slimItem.itemID
            slimItem = bp.GetInvItem(slimItem.itemID)
            if slimItem is None:
                self.LogInfo('Lost ball', itemID)
                numLostBalls += 1
                continue
            itemID = slimItem.itemID
            if slimItem.categoryID == const.categoryShip and getattr(slimItem, 'charID', None) or slimItem.categoryID == const.categoryEntity:
                attacking, hostile = self.stateSvc.GetStates(itemID, [state.threatAttackingMe, state.threatTargetsMe])
                if attacking or hostile:
                    threatening.append(each)
                else:
                    nonThreatening.append(each)
            else:
                nonThreatening.append(each)

        return (nonThreatening, threatening, numLostBalls)

    def PrioritizeLoadingForIDs(self, ids):
        self.prioritizedIDs.update(ids)

    def _LoadObjects(self, objects, info = 'Loading'):
        numBallsAdded = 0
        numLostBalls = 0
        michelle = sm.GetService('michelle')
        for each in objects:
            ball, slimItem, ob = each
            bp = michelle.GetBallpark()
            if bp is None:
                return (numBallsAdded, numLostBalls)
            itemID = slimItem.itemID
            slimItem = bp.GetInvItem(slimItem.itemID)
            if slimItem is None:
                self.LogInfo('Lost ball', itemID)
                numLostBalls += 1
                continue
            itemID = slimItem.itemID
            self.LogInfo(info, itemID)
            self.LoadObject(ball, slimItem, ob)
            numBallsAdded += 1

        return (numBallsAdded, numLostBalls)

    def GetScene(self):
        return sm.GetService('sceneManager').GetRegisteredScene('default')

    def GetRenderJob(self):
        return sm.GetService('sceneManager').GetFisRenderJob()

    def GetCamera(self):
        return sm.GetService('sceneManager').GetActiveCamera()

    @telemetry.ZONE_METHOD
    def DoBallsAdded_(self, ballsToAdd):
        bp = sm.GetService('michelle').GetBallpark()
        if bp is None:
            return
        self.LogInfo('DoBallsAdded_ - Starting to add', len(ballsToAdd), ' balls. lazy = ', settings.public.generic.Get('lazyLoading', 1))
        numBallsToAdd = len(ballsToAdd)
        numLostBalls = 0
        numBallsAdded = 0
        self.lazyLoadQueueCount = len(ballsToAdd)
        timeStarted = blue.os.GetWallclockTimeNow()
        nonPrioritized = []
        prioritized = []
        for each in ballsToAdd:
            ball, slimItem, ob = each
            itemID = slimItem.itemID
            slimItem = bp.GetInvItem(slimItem.itemID)
            if slimItem is None:
                self.LogInfo('Lost ball', itemID)
                numLostBalls += 1
                continue
            itemID = slimItem.itemID
            if slimItem.groupID in (const.groupSun, const.groupMassiveEnvironments):
                prioritized.append(each)
            elif itemID == session.shipid:
                prioritized.append(each)
            elif itemID in self.prioritizedIDs:
                prioritized.append(each)
                self.prioritizedIDs.remove(itemID)
            elif slimItem.groupID in (const.groupPlanet, const.groupMoon):
                egoball = bp.GetBall(bp.ego)
                distance = bp.DistanceBetween(egoball.id, itemID)
                if distance < const.AU / 2:
                    prioritized.append(each)
                else:
                    nonPrioritized.append(each)
            else:
                nonPrioritized.append(each)

        ballsToAdd = nonPrioritized
        added, lost = self._LoadObjects(prioritized, 'Preemtively loading prioritized')
        numBallsAdded += added
        numLostBalls += lost
        startOfTimeSlice = blue.os.GetWallclockTimeNow()
        nextThreatCheck = startOfTimeSlice + 500 * const.MSEC
        while len(ballsToAdd):
            try:
                ball, slimItem, ob = ballsToAdd.pop(0)
                self.LogInfo('Handling ball', slimItem.itemID)
                self.lazyLoadQueueCount = len(ballsToAdd)
                bp = sm.GetService('michelle').GetBallpark()
                if bp is None:
                    return
                itemID = slimItem.itemID
                slimItem = bp.GetInvItem(slimItem.itemID)
                if slimItem is None:
                    self.LogInfo('Lost ball', itemID)
                    numLostBalls += 1
                    continue
                itemID = slimItem.itemID
                self.LogInfo('Loading', itemID)
                self.LoadObject(ball, slimItem, ob)
                numBallsAdded += 1
                if blue.os.GetWallclockTimeNow() > nextThreatCheck:
                    ballsToAdd, threatening, lost = self.SplitListByThreat(bp, ballsToAdd)
                    numLostBalls += lost
                    added, lost = self._LoadObjects(threatening, 'Preemptively loading threat')
                    numBallsAdded += added
                    numLostBalls += lost
                    nextThreatCheck = blue.os.GetWallclockTimeNow() + 500 * const.MSEC
                self.lazyLoadQueueCount = len(ballsToAdd)
                if settings.public.generic.Get('lazyLoading', 1):
                    if blue.os.GetWallclockTimeNow() > startOfTimeSlice + self.maxTimeInDoBallsAdded:
                        blue.synchro.Yield()
                        startOfTimeSlice = blue.os.GetWallclockTimeNow()
            except:
                stdlog.warning('DoBallsAdded - failed to add ball', exc_info=1, extra={'ball': ball,
                 'slimItem': slimItem})
                sys.exc_clear()

        self.LogInfo('DoBallsAdded_ - Done adding', numBallsToAdd, ' balls in', FmtDate(blue.os.GetWallclockTimeNow() - timeStarted, 'nl'), '.', numLostBalls, 'balls were lost. lazy = ', settings.public.generic.Get('lazyLoading', 1))
        if numBallsAdded + numLostBalls != numBallsToAdd:
            self.LogError("DoBallsAdded - balls don't add up! numBallsAdded:", numBallsAdded, 'numLostBalls:', numLostBalls, 'numBallsToAdd:', numBallsToAdd)

    @telemetry.ZONE_METHOD
    def DoBallsRemove(self, pythonBalls, isRelease):
        if isRelease:
            for ball, slimItem, terminal in pythonBalls:
                self.unloadables.discard(ball.id)
                if hasattr(ball, 'Release'):
                    uthread.new(ball.Release)

            self.planetManager.Release()
            return
        for ball, slimItem, terminal in pythonBalls:
            self.DoBallRemove(ball, slimItem, terminal)

    @telemetry.ZONE_METHOD
    def DoBallRemove(self, ball, slimItem, terminal):
        if ball is None:
            return
        self.LogInfo('DoBallRemove::spaceMgr', ball.id)
        self.unloadables.discard(ball.id)
        if hasattr(ball, 'Release'):
            uthread.new(ball.Release)
        if slimItem.groupID == const.groupPlanet or slimItem.groupID == const.groupMoon:
            self.planetManager.UnRegisterPlanetBall(ball)
        elif slimItem.groupID == const.groupSun:
            self.planetManager.UnRegisterSunBall(ball)

    @telemetry.ZONE_METHOD
    def OnBallparkCall(self, functionName, args):
        if functionName == 'WarpTo' and args[0] == session.shipid:
            x = args[1]
            y = args[2]
            z = args[3]
            if not self.warpDestinationCache:
                self.warpDestinationCache = [None,
                 None,
                 None,
                 (x, y, z)]
            else:
                self.warpDestinationCache[3] = (x, y, z)
        elif functionName == 'SetBallRadius':
            ballID = args[0]
            newRadius = args[1]
            ball = sm.GetService('michelle').GetBall(ballID)
            if hasattr(ball, 'SetRadius'):
                ball.SetRadius(newRadius)

    def OnDamageStateChange(self, shipID, damageState):
        ball = sm.GetService('michelle').GetBall(shipID)
        if ball:
            if hasattr(ball, 'OnDamageState'):
                ball.OnDamageState(damageState)

    def OnRemoteMessage(self, msgID, *args, **kwargs):
        if msgID == 'FleetWarp':
            warpInfoDict = args[0]
            self.LogInfo('Setting local warp destination for fleet warp')
            celestialID = warpInfoDict.get('celestialID', None)
            self.WarpDestination(celestialID=celestialID)

    def WarpDestination(self, celestialID = None, bookmarkID = None, fleetMemberID = None):
        self.warpDestinationCache[0] = celestialID
        self.warpDestinationCache[1] = bookmarkID
        self.warpDestinationCache[2] = fleetMemberID

    def GetWarpDestinationItemIDAndTypeID(self):
        itemID = None
        typeID = None
        if self.warpDestinationCache[0]:
            itemID = self.warpDestinationCache[0]
            item = uix.GetBallparkRecord(itemID)
            if item:
                typeID = item.typeID
        elif self.warpDestinationCache[1]:
            itemID = self.warpDestinationCache[1]
            typeID = const.typeBookmark
        elif self.warpDestinationCache[2]:
            itemID = self.warpDestinationCache[2]
            typeID = const.typeCharacter
        return (itemID, typeID)

    def IsWarping(self):
        for destination in self.warpDestinationCache:
            if destination is not None:
                return True

        return False

    def GetWarpDistance(self):
        _, _, _, destinationPosition, actualDestinationPosition = self.warpDestinationCache
        if not destinationPosition:
            return 0
        ballPark = sm.GetService('michelle').GetBallpark()
        if not ballPark:
            return 0
        egoball = ballPark.GetBall(ballPark.ego)
        destinationPosition = actualDestinationPosition or destinationPosition
        if actualDestinationPosition is not None:
            destinationPosition = actualDestinationPosition
        warpDirection = [destinationPosition[0] - egoball.x, destinationPosition[1] - egoball.y, destinationPosition[2] - egoball.z]
        return self.VectorLength(warpDirection)

    def StartWarpIndication(self):
        self.ConfirmWarpDestination()
        self.LogNotice('StartWarpIndication', self.warpDestText, 'autopilot =', sm.GetService('autoPilot').GetState())

    def OnSpecialFX(self, shipID, moduleID, moduleTypeID, targetID, otherTypeID, guid, isOffensive, start, active, duration = -1, repeat = None, startTime = None, timeFromStart = 0, graphicInfo = None):
        self.LogInfo('Space::OnSpecialFX - ', guid)
        if IsFullLogging():
            self.LogInfo(shipID, moduleID, moduleTypeID, targetID, otherTypeID, guid, isOffensive, start, active, duration, repeat)
        if shipID == eve.session.shipid:
            if guid == 'effects.JumpOut':
                bp = sm.StartService('michelle').GetBallpark()
                slimItem = bp.GetInvItem(targetID)
                if slimItem:
                    locations = [slimItem.jumps[0].locationID, slimItem.jumps[0].toCelestialID]
                    cfg.evelocations.Prime(locations)
                    solID = slimItem.jumps[0].locationID
                    destID = slimItem.jumps[0].toCelestialID
                    sm.GetService('logger').AddText(localization.GetByLabel('UI/Inflight/Messages/LoggerJumpingToGateInSystem', gate=destID, system=solID))
                    self.IndicateAction(localization.GetByLabel('UI/Inflight/Messages/Jumping'), localization.GetByLabel('UI/Inflight/Messages/DestinationInSystem', gate=destID, system=solID))
            elif guid == 'effects.JumpOutWormhole':
                if otherTypeID is None:
                    otherTypeID = 0
                wormholeClasses = {0: 'UI/Wormholes/Classes/Space',
                 1: 'UI/Wormholes/Classes/UnknownSpace',
                 2: 'UI/Wormholes/Classes/UnknownSpace',
                 3: 'UI/Wormholes/Classes/UnknownSpace',
                 4: 'UI/Wormholes/Classes/UnknownSpace',
                 5: 'UI/Wormholes/Classes/DeepUnknownSpace',
                 6: 'UI/Wormholes/Classes/DeepUnknownSpace',
                 7: 'UI/Wormholes/Classes/HighSecuritySpace',
                 8: 'UI/Wormholes/Classes/LowSecuritySpace',
                 9: 'UI/Wormholes/Classes/NullSecuritySpace',
                 12: 'UI/Wormholes/Classes/DeepUnknownSpace',
                 13: 'UI/Wormholes/Classes/UnknownSpace',
                 25: 'UI/Wormholes/Classes/TriglavianSpace'}
                wormholeClassLabelName = wormholeClasses.get(otherTypeID, 'UI/Wormholes/Classes/Space')
                wormholeClassName = localization.GetByLabel(wormholeClassLabelName)
                self.IndicateAction(localization.GetByLabel('UI/Inflight/Messages/JumpingThroughWormhole'), localization.GetByLabel('UI/Inflight/Messages/NotifyJumpingThroughWormhole', wormholeClass=wormholeClassName))
            elif guid in ('effects.JumpDriveOut', 'effects.JumpDriveOutBO'):
                self.IndicateAction(localization.GetByLabel('UI/Inflight/Messages/Jumping'), localization.GetByLabel('UI/Inflight/Messages/NotifyJumpingToBeacon'))

    def OnDockingAccepted(self, itemID):
        self.audio.AudioMessage('msg_DockingAccepted_play')
        if idCheckers.IsStation(itemID):
            name = localization.GetByLabel('UI/Inflight/Messages/DestinationStation', station=itemID)
        else:
            name = self.GetWarpDestinationName(itemID)
        self.IndicateAction(localization.GetByLabel('UI/Inflight/Messages/Docking'), name)

    def OnReleaseBallpark(self):
        self.flashTransform = None

    def CheckWarpDestination(self, warpPoint, destinationPoint, egoPoint, angularTolerance, distanceTolerance):
        destinationOffset = [destinationPoint[0] - warpPoint[0], destinationPoint[1] - warpPoint[1], destinationPoint[2] - warpPoint[2]]
        destinationDirection = [warpPoint[0] - egoPoint[0], warpPoint[1] - egoPoint[1], warpPoint[2] - egoPoint[2]]
        warpDirection = [destinationPoint[0] - egoPoint[0], destinationPoint[1] - egoPoint[1], destinationPoint[2] - egoPoint[2]]
        vlen = self.VectorLength(destinationDirection)
        destinationDirection = [ x / vlen for x in destinationDirection ]
        vlen = self.VectorLength(warpDirection)
        warpDirection = [ x / vlen for x in warpDirection ]
        angularDifference = warpDirection[0] * destinationDirection[0] + warpDirection[1] * destinationDirection[1] + warpDirection[2] * destinationDirection[2]
        angularDifference = min(max(-1.0, angularDifference), 1.0)
        angularDifference = math.acos(angularDifference)
        if abs(angularDifference) < angularTolerance or self.VectorLength(destinationOffset) < distanceTolerance:
            return True
        else:
            return False

    def VectorLength(self, vector):
        result = 0
        for i in vector:
            result += pow(i, 2)

        return pow(result, 0.5)

    def GetWarpDestinationName(self, id):
        name = None
        item = uix.GetBallparkRecord(id)
        if item is None or item.categoryID not in [const.categoryAsteroid]:
            name = cfg.evelocations.Get(id).name
        if not name and item:
            name = evetypes.GetName(item.typeID)
        return name

    def ConfirmWarpDestination(self):
        destinationItemID, destinationBookmarkID, destinationfleetMemberID, destinationPosition, actualDestinationPosition = self.warpDestinationCache
        self.warpDestText = ''
        self.warpDestinationCache[4] = None
        ballPark = sm.GetService('michelle').GetBallpark()
        if not ballPark:
            return
        egoball = ballPark.GetBall(ballPark.ego)
        if destinationItemID:
            if destinationItemID in ballPark.balls:
                b = ballPark.balls[destinationItemID]
                if self.CheckWarpDestination(destinationPosition, (b.x, b.y, b.z), (egoball.x, egoball.y, egoball.z), math.pi / 32, 20000000):
                    self.warpDestinationCache[4] = (b.x, b.y, b.z)
                    name = self.GetWarpDestinationName(destinationItemID)
                    self.warpDestText = localization.GetByLabel('UI/Inflight/Messages/WarpDestination', destinationName=name) + '<br>'
        elif destinationBookmarkID:
            bookmark = sm.GetService('addressbook').GetBookmark(destinationBookmarkID)
            if bookmark is not None:
                if bookmark.x is None:
                    if bookmark.memo:
                        titleEndPosition = bookmark.memo.find('\t')
                        if titleEndPosition > -1:
                            memoTitle = bookmark.memo[:titleEndPosition]
                        else:
                            memoTitle = bookmark.memo
                        self.warpDestText = localization.GetByLabel('UI/Inflight/Messages/WarpDestination', destinationName=memoTitle) + '<br>'
                        if bookmark.itemID is not None:
                            b = ballPark.balls[bookmark.itemID]
                            if self.CheckWarpDestination(destinationPosition, (b.x, b.y, b.z), (egoball.x, egoball.y, egoball.z), math.pi / 32, 20000000):
                                self.warpDestinationCache[4] = (b.x, b.y, b.z)
                elif self.CheckWarpDestination(destinationPosition, (bookmark.x, bookmark.y, bookmark.z), (egoball.x, egoball.y, egoball.z), math.pi / 32, 20000000):
                    if bookmark.memo:
                        titleEndPosition = bookmark.memo.find('\t')
                        if titleEndPosition > -1:
                            memoTitle = bookmark.memo[:titleEndPosition]
                        else:
                            memoTitle = bookmark.memo
                        self.warpDestText = localization.GetByLabel('UI/Inflight/Messages/WarpDestination', destinationName=memoTitle) + '<br>'
                        self.warpDestinationCache[4] = (bookmark.x, bookmark.y, bookmark.z)

    def IndicateWarp(self, ball):
        destinationItemID, destinationBookmarkID, destinationfleetMemberID, destinationPosition, actualDestinationPosition = self.warpDestinationCache
        if not destinationPosition:
            return (None, None)
        ballPark = sm.GetService('michelle').GetBallpark()
        if not ballPark:
            self.LogWarn('Space::IndicateWarp: Trying to indicate warp without a ballpark?')
            return (None, None)
        centeredDestText = '<center>' + getattr(self, 'warpDestText', '')
        text = centeredDestText
        egoball = ballPark.GetBall(ballPark.ego)
        if actualDestinationPosition is not None:
            warpDirection = [actualDestinationPosition[0] - egoball.x, actualDestinationPosition[1] - egoball.y, actualDestinationPosition[2] - egoball.z]
        else:
            warpDirection = [destinationPosition[0] - egoball.x, destinationPosition[1] - egoball.y, destinationPosition[2] - egoball.z]
        dist = self.VectorLength(warpDirection)
        if dist:
            distanceText = '<center>' + localization.GetByLabel('UI/Inflight/ActiveItem/SelectedItemDistance', distToItem=FmtDist(dist))
            if actualDestinationPosition is None:
                text = localization.GetByLabel('UI/Inflight/Messages/WarpIndicatorWithDistanceAndBubble', warpDestination=centeredDestText, distance=distanceText)
            else:
                text = localization.GetByLabel('UI/Inflight/Messages/WarpIndicatorWithDistance', warpDestination=centeredDestText, distance=distanceText)
        self.LogInfo('Space::IndicateWarp', text)
        if ball and ball.effectStamp < 0:
            overallProgress = self._GetWarpProgress(ball, warpDirection)
            headerText = localization.GetByLabel('UI/Inflight/Messages/WarpDrivePreparing')
            self.SetProgressbar(overallProgress)
            self.audio.SetUIRTPC('ship_warp_direction', overallProgress)
        else:
            self.audio.WarpPreparation('stop', ball.id)
            headerText = localization.GetByLabel('UI/Inflight/Messages/WarpDriveActive')
            self.KillProgressBarOnWarp()
        return (headerText, text)

    def _GetWarpProgress(self, ball, warpDirection):
        speedFraction = min(1.0, ball.GetVectorDotAt(blue.os.GetSimTime()).Length() / ball.maxVelocity)
        speedProgress = min(speedFraction / 0.75, 1.0)
        if speedFraction > 0.01:
            currentDirection = geo2.Vec3Normalize((ball.vx, ball.vy, ball.vz))
            dotProduct = geo2.Vec3DotD(currentDirection, geo2.Vec3Normalize(warpDirection))
        else:
            dotProduct = -1.0
        angleProgress = (dotProduct + 1.0) / 1.99
        MAX_ALIGN_TICKS = 180.0
        autoWarpProgress = min(-ball.effectStamp / MAX_ALIGN_TICKS, 1.0)
        overallProgress = max(min(speedProgress, angleProgress) ** 3, autoWarpProgress)
        return overallProgress

    def Indicate_thread(self, *args):
        indicateProperties = self.GetHUDActionIndicateProperties()
        oldIndicateProperties = getattr(self, 'indicateProperties', None)
        if oldIndicateProperties is None or indicateProperties != oldIndicateProperties:
            wasDisplayed = self.UpdateHUDActionIndicator(storeText=False)
            if wasDisplayed:
                self.indicateProperties = indicateProperties

    def GetHUDActionIndicateProperties(self, *args):
        ballpark = sm.GetService('michelle').GetBallpark()
        if not ballpark:
            return
        ball = ballpark.GetBall(ballpark.ego)
        if ball is None:
            return
        if ball.mode == destiny.DSTBALL_STOP:
            speed = ball.GetVectorDotAt(blue.os.GetSimTime()).Length()
        else:
            speed = None
        alignTargetID, aligningToBookmark = GetMenuService().GetLastAlignTarget()
        if ball.mode == destiny.DSTBALL_GOTO and alignTargetID is None and aligningToBookmark is None:
            approachType = self.GetBallApproachType(ball)
        else:
            approachType = None
        return (ball.followId,
         ball.mode,
         ball.followRange,
         alignTargetID or aligningToBookmark,
         speed,
         approachType)

    def UpdateHUDActionIndicator(self, storeText = False, *args):
        header, subText = self.GetHeaderAndSubtextFromBall()
        if header is not None and subText is not None:
            return self.IndicateAction(header, subText, storeText=storeText)
        if not self.setIndicationText:
            self.ClearIndicateText()

    def GetHeaderAndSubtextFromBall(self, *args):
        ballpark = sm.GetService('michelle').GetBallpark()
        if not ballpark:
            return (None, None)
        ball = ballpark.GetBall(ballpark.ego)
        if ball is None:
            return (None, None)
        return self.GetHeaderAndSubtextForActionIndication(ball.mode, ball.followId, ball.followRange, ball=ball)

    def GetHeaderAndSubtextForActionIndication(self, ballMode, followId, followRange, ball = None, *args):
        headerText = None
        subText = None
        if ballMode != destiny.DSTBALL_GOTO and ball is not None:
            if not self.caption or self.caption.text != localization.GetByLabel('UI/Inflight/Messages/AligningHeader'):
                GetMenuService().ClearAlignTargets()
        if followId != 0 and ballMode in (destiny.DSTBALL_ORBIT, destiny.DSTBALL_FOLLOW):
            name = sm.GetService('space').GetWarpDestinationName(followId)
            myRange = followRange
            rangeText = FmtDist(myRange, maxdemicals=0)
            if ballMode == destiny.DSTBALL_ORBIT:
                headerText = localization.GetByLabel('UI/Inflight/Messages/OrbitingHeader')
                subText = localization.GetByLabel('UI/Inflight/Messages/OrbitingSubText', targetName=name, rangeText=rangeText)
            elif ballMode == destiny.DSTBALL_FOLLOW:
                if myRange in (const.approachRange, 0):
                    headerText = localization.GetByLabel('UI/Inflight/Messages/ApproachingHeader')
                    subText = localization.GetByLabel('UI/Inflight/Messages/ApproachingSubText', targetName=name)
                else:
                    headerText = localization.GetByLabel('UI/Inflight/Messages/KeepingAtRangeHeader')
                    subText = localization.GetByLabel('UI/Inflight/Messages/KeepingAtRangeSubText', targetName=name, rangeText=rangeText)
        elif ballMode == destiny.DSTBALL_GOTO:
            alignTargetID, aligningToBookmark = GetMenuService().GetLastAlignTarget()
            if not alignTargetID and not aligningToBookmark:
                approachType = self.GetBallApproachType(ball)
                if approachType in (None, BALL_CLOSE_DISTANCE, BALL_ALIGN_DISTANCE_ALIGNED):
                    return (None, None)
                if approachType == BALL_APPROACH_DISTANCE:
                    headerText = localization.GetByLabel('UI/Inflight/Messages/ApproachingHeader')
                    subText = localization.GetByLabel('UI/Inflight/Messages/ApproachingPointSubText')
                else:
                    headerText = localization.GetByLabel('UI/Inflight/Messages/AligningHeader')
                    subText = localization.GetByLabel('UI/Inflight/Messages/AligningToPointSubText')
                return (headerText, subText)
            headerText = localization.GetByLabel('UI/Inflight/Messages/AligningHeader')
            if alignTargetID:
                if idCheckers.IsCharacter(alignTargetID):
                    subText = localization.GetByLabel('UI/Inflight/Messages/AligningToPlayerSubText', charID=alignTargetID)
                else:
                    try:
                        name = sm.GetService('space').GetWarpDestinationName(alignTargetID)
                        subText = localization.GetByLabel('UI/Inflight/Messages/AligningToLocationSubText', targetName=name)
                    except:
                        subText = localization.GetByLabel('UI/Inflight/Messages/AligningUnknownSubText')

            elif aligningToBookmark:
                subText = localization.GetByLabel('UI/Inflight/Messages/AligningToBookmarkSubText')
            else:
                subText = localization.GetByLabel('UI/Inflight/Messages/AligningUnknownSubText')
        elif ballMode == destiny.DSTBALL_WARP:
            return self.IndicateWarp(ball)
        return (headerText, subText)

    def GetBallApproachType(self, ball):
        if not ball or IsControllingStructure():
            return None
        currentBallLocation = (ball.x, ball.y, ball.z)
        destinationLocation = (ball.gotoX, ball.gotoY, ball.gotoZ)
        distance = geo2.Vec3Distance(currentBallLocation, destinationLocation)
        if distance < 1000:
            return BALL_CLOSE_DISTANCE
        if distance <= const.maxApproachDistance:
            return BALL_APPROACH_DISTANCE
        currentDirection = geo2.Vec3Normalize((ball.vx, ball.vy, ball.vz))
        directionToDestination = geo2.Vec3Direction(destinationLocation, currentBallLocation)
        dotProduct = geo2.Vec3DotD(currentDirection, directionToDestination)
        ang = math.acos(max(-1.0, min(1.0, dotProduct)))
        if ang < DEGREES_15:
            return BALL_ALIGN_DISTANCE_ALIGNED
        return BALL_ALIGN_DISTANCE

    def SetIndicationTextForcefully(self, ballMode, followId, followRange):
        header, subText = self.GetHeaderAndSubtextForActionIndication(ballMode, followId, followRange)
        self.DoSetIndicationTextForcefully(header, subText)

    def DoSetIndicationTextForcefully(self, headerText, subText, indicationTime = 2000):
        self.ClearShortcutText()
        self.ShowOrHideProgressbar(False)
        if headerText:
            self.CreateIndicationTextsIfNeeded()
            self.IndicateAction(headerText, subText, storeText=True)
            self.caption.SetRGBA(0.5, 0.5, 0.5, 1.0)
            uicore.animations.BlinkOut(self.caption, startVal=1.0, endVal=0.3, duration=0.8, loops=2, curveType=uiconst.ANIM_WAVE)
            uicore.animations.BlinkOut(self.indicationtext, startVal=1.0, endVal=0.3, duration=0.8, loops=2, curveType=uiconst.ANIM_WAVE)
        elif self.caption:
            self.ResetCaptionColor()
        uthread.new(self.ClearForcefullySetText_thread, headerText, subText, indicationTime)

    def ClearForcefullySetText_thread(self, header, subText, sleep_time):
        blue.pyos.synchro.SleepWallclock(sleep_time)
        if self.setIndicationText is None:
            return
        if self.setIndicationText == (header, subText):
            sm.GetService('space').ClearIndicateText()
            sm.GetService('space').UpdateHUDActionIndicator()
            uicore.animations.SpColorMorphToWhite(self.caption, duration=0.2)
            uicore.animations.SpColorMorphToWhite(self.indicationtext, duration=0.2)

    def ClearIndicateText(self, *args):
        self.indicateProperties = None
        if self.indicationtext is not None and not self.indicationtext.destroyed:
            self.indicationtext.display = False
            self.indicationtext.text = ''
        if self.caption is not None and not self.caption.destroyed:
            self.caption.display = False
            self.caption.text = ''
            self.ResetCaptionColor()
        if self.captionProgressbar:
            self.captionProgressbar.Close()
            self.captionProgressbar = None
        self.setIndicationText = None

    def ResetCaptionColor(self):
        if self.caption is not None and not self.caption.destroyed:
            self.caption.SetRGBA(1.0, 1.0, 1.0, 1.0)

    def IndicateAction(self, header = None, subText = None, storeText = True, *args):
        if not storeText and self.setIndicationText or getattr(self, 'displayingShortcut', False):
            self.ShowOrHideProgressbar(False)
            return False
        if storeText:
            self.setIndicationText = (header, subText)
            self.indicateProperties = None
        if header is None and subText is None:
            if self.indicationtext is not None and not self.indicationtext.destroyed:
                self.indicationtext.display = False
            if self.caption is not None and not self.caption.destroyed:
                self.caption.display = False
            return False
        if uicore.layer.shipui.sr.indicationContainer is None or uicore.layer.shipui.sr.indicationContainer.destroyed:
            self.indicateProperties = None
            return False
        if self.indicationtext is None or self.indicationtext.destroyed or self.indicationtext.parent is None:
            self.CreateIndicationTextsIfNeeded()
        else:
            self.indicationtext.display = True
            self.caption.display = True
        self.indicationtext.text = '<center>' + subText
        self.caption.text = header
        self.caption.top = CAPTION_TOP
        if uicore.layer.shipui.sr.indicationContainer is None:
            self.indicateProperties = None
            return False
        self.indicationtext.left = (uicore.layer.shipui.sr.indicationContainer.width - self.indicationtext.width) / 2
        self.indicationtext.top = self.caption.top + self.caption.height
        return True

    def CreateIndicationTextsIfNeeded(self, *args):
        if self.indicationtext is None or self.indicationtext.destroyed:
            self.indicationtext = eveLabel.EveLabelMedium(parent=uicore.layer.shipui.sr.indicationContainer, name='indicationtext2', text='', align=uiconst.TOPLEFT, width=400, state=uiconst.UI_DISABLED)
        if self.caption is None or self.caption.destroyed:
            self.caption = eveLabel.CaptionLabel(text='', parent=uicore.layer.shipui.sr.indicationContainer, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, top=CAPTION_TOP)

    def SetProgressbar(self, value = 0):
        if value == 0:
            self.ShowOrHideProgressbar(False)
            return
        width = min(1.0, max(0, value))
        if self.captionProgressbar is None or self.captionProgressbar.destroyed:
            self.captionProgressbar = Container(name='captionProgressbar', parent=uicore.layer.shipui.sr.indicationContainer, width=200, height=3, align=uiconst.CENTERTOP)
            self.captionProgressbar.normalDisplayState = True
            Fill(parent=self.captionProgressbar, opacity=0.2)
            self.captionProgressbar.fill = Fill(parent=self.captionProgressbar, align=uiconst.TOLEFT_PROP, width=width, opacity=0.5)
        self.ShowOrHideProgressbar(True)
        self.captionProgressbar.beingKilled = False
        fill = self.captionProgressbar.fill
        uicore.animations.MorphScalar(fill, 'width', startVal=fill.width, endVal=width, duration=1.0, curveType=uiconst.ANIM_LINEAR)

    def ShowOrHideProgressbar(self, doShow, recordState = True):
        if self.captionProgressbar:
            self.captionProgressbar.display = doShow
            if recordState:
                self.captionProgressbar.normalDisplayState = doShow

    def KillProgressBarOnWarp(self):
        if self.captionProgressbar and not self.captionProgressbar.beingKilled:
            self.captionProgressbar.beingKilled = True
            uthread.new(self._KillProgressBarOnWarpDelayed, self.captionProgressbar)

    def _KillProgressBarOnWarpDelayed(self, progressbar):
        if progressbar and not progressbar.destroyed:
            fill = progressbar.fill
            uicore.animations.MorphScalar(fill, 'width', startVal=fill.width, endVal=1.0, duration=0.25, curveType=uiconst.ANIM_LINEAR, sleep=True)
            uicore.animations.FadeTo(progressbar, startVal=0.5, endVal=1.0, duration=0.1, loops=2, curveType=uiconst.ANIM_BOUNCE, sleep=True)
            if progressbar:
                progressbar.Close()
            if self.captionProgressbar and self.captionProgressbar.destroyed:
                self.captionProgressbar = None

    def OnShipUIReset(self, *args):
        self.indicateProperties = None
        if self.indicationtext:
            self.indicationtext.Close()
        if self.caption:
            self.caption.Close()
        if self.captionProgressbar:
            self.captionProgressbar.Close()

    def ChangeHUDActionVisiblity(self, doDisplay = True):
        for each in (self.indicationtext, self.caption):
            if each:
                each.display = doDisplay

        if self.captionProgressbar:
            if doDisplay and self.captionProgressbar.normalDisplayState:
                doDisplayProgressBar = True
            else:
                doDisplayProgressBar = False
            self.ShowOrHideProgressbar(doDisplayProgressBar, recordState=False)

    def SetShortcutText(self, headerText, text, delayMs = 0, hideDelayMs = None, *args):
        if not sm.GetService('viewState').IsViewActive(ViewState.Space):
            return
        if uicore.layer.shipui.sr.indicationContainer is None or uicore.layer.shipui.sr.indicationContainer.destroyed:
            self.shortcutText = None
            self.shortcutSubText = None
            return
        if self.shortcutText is None or self.shortcutText.destroyed:
            self.shortcutText = eveLabel.CaptionLabel(text='', parent=uicore.layer.shipui.sr.indicationContainer, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, top=CAPTION_TOP)
        else:
            self.shortcutText.display = True
        if self.shortcutSubText is None or self.shortcutSubText.destroyed:
            self.shortcutSubText = eveLabel.EveLabelMedium(parent=uicore.layer.shipui.sr.indicationContainer, name='shortcutSubText', text='', align=uiconst.CENTERTOP, width=400, state=uiconst.UI_DISABLED, top=-34)
        else:
            self.shortcutSubText.display = True
            self.shortcutSubText.SetAlpha(1.0)
        self.shortcutText.text = headerText
        self.shortcutSubText.text = text
        self.shortcutSubText.left = (uicore.layer.shipui.sr.indicationContainer.width - self.shortcutSubText.width) / 2
        self.shortcutSubText.top = self.shortcutText.top + self.shortcutText.height
        self.displayingShortcut = True
        if delayMs:
            uthread.new(self._DelayShowShortcutMsg, delayMs)
        else:
            self.ChangeHUDActionVisiblity(doDisplay=False)
        if hideDelayMs:
            self.StartShortcutClearThread(hideDelayMs)

    def StartShortcutClearThread(self, delayMs):
        if self.shortcutClearThread is not None and self.shortcutClearThread.alive:
            self.shortcutClearThread.kill()
        self.shortcutClearThread = uthread.new(self._ClearShortcutText, delayMs)

    def _ClearShortcutText(self, delayMs):
        blue.pyos.synchro.SleepWallclock(delayMs)
        self.ClearShortcutText()

    def _DelayShowShortcutMsg(self, delayMs):
        if self.shortcutSubText is None or self.shortcutSubText.destroyed:
            return
        self.shortcutSubText.SetAlpha(0.0)
        self.shortcutText.SetAlpha(0.0)
        blue.pyos.synchro.SleepWallclock(delayMs)
        if self.displayingShortcut:
            self.ChangeHUDActionVisiblity(doDisplay=False)
        if self.shortcutSubText:
            self.shortcutSubText.SetAlpha(1.0)
        if self.shortcutText:
            self.shortcutText.SetAlpha(1.0)

    def ClearShortcutText(self, *args):
        self.displayingShortcut = False
        self.ChangeHUDActionVisiblity(doDisplay=True)
        if self.shortcutText and not self.shortcutText.destroyed:
            self.shortcutText.display = False
            self.shortcutText.text = ''
        if self.shortcutSubText and not self.shortcutSubText.destroyed:
            self.shortcutSubText.display = False
            self.shortcutSubText.text = ''

    def GetHeader(self):
        if self.caption is None or self.caption.destroyed:
            return
        return self.caption.text

    def StopWarpIndication(self):
        self.LogNotice('StopWarpIndication', getattr(self, 'warpDestText', '-'), 'autopilot =', sm.GetService('autoPilot').GetState())
        self.warpDestinationCache = [None,
         None,
         None,
         None,
         None]
        self.ClearIndicateText()
        self.transmission.StopWarpIndication()
        self.audio.SetShipState(eveaudio.const.ShipState.idle)

    def KillIndicationTimer(self, guid):
        self.warpDestinationCache = [None,
         None,
         None,
         None,
         None]
        if hasattr(self, guid):
            delattr(self, guid)
            self.ClearIndicateText()

    def StartPartitionDisplayTimer(self, boxsize = 7):
        self.StopPartitionDisplayTimer()
        settings.user.ui.Set('partition_box_size', boxsize)
        self.partitionDisplayTimer = timerstuff.AutoTimer(50, self.UpdatePartitionDisplay)

    def StopPartitionDisplayTimer(self):
        self.partitionDisplayTimer = None
        self.CleanPartitionDisplay()

    def UpdatePartitionDisplay(self):
        if getattr(self, 'partitionTF', None) is None:
            scene = sm.GetService('sceneManager').GetRegisteredScene('default')
            self.partitionTF = trinity.EveTransform()
            scene.objects.append(self.partitionTF)
        boxRange = settings.user.ui.Get('partition_box_size', 7)
        allboxes = settings.user.ui.Get('partition_box_showall', 1)
        ballpark = sm.GetService('michelle').GetBallpark()
        if not ballpark:
            self.StopPartitionDisplayTimer()
            return
        egoball = ballpark.GetBall(ballpark.ego)
        if allboxes == 1:
            boxRange = range(boxRange, 8)
        else:
            boxRange = [boxRange]
        numChildren = len(self.partitionTF.children)
        count = [0]

        def GetTransform():
            if count[0] >= numChildren:
                tf = blue.resMan.LoadObject('res:/model/global/partitionBox.red')
                self.partitionTF.children.append(tf)
                count[0] += 1
                return tf
            tf = self.partitionTF.children[count[0]]
            count[0] += 1
            return tf

        for boxSize in boxRange:
            boxes = ballpark.GetActiveBoxes(boxSize)
            width, coords = boxes
            if not boxes:
                continue
            for x, y, z in coords:
                tf = GetTransform()
                x = x - egoball.x + width / 2
                y = y - egoball.y + width / 2
                z = z - egoball.z + width / 2
                tf.scaling = (width, width, width)
                tf.translation = (x, y, z)

        while count[0] < numChildren:
            numChildren -= 1
            self.partitionTF.children.removeAt(numChildren)

    def CleanPartitionDisplay(self):
        if getattr(self, 'partitionTF', None) is None:
            return
        scene = sm.GetService('sceneManager').GetRegisteredScene('default')
        scene.objects.fremove(self.partitionTF)
        self.partitionTF = None

    def GetNebulaTextureForType(self, nebulaType):
        sceneManager = sm.GetService('sceneManager')
        return sceneManager.DeriveTextureFromSceneName(fsdGraphicIDs.GetGraphicFile(nebulaType))

    def OnClientControllerEvent(self, ballID, targetID, eventName, value = None, delay = None):
        ball = sm.GetService('michelle').GetBall(ballID)
        if ball and hasattr(ball, 'SetControllerVariableFromEvent'):
            if delay is not None:
                uthread.new(ball.SetControllerVariableFromEvent, eventName, value, delay)
            else:
                ball.SetControllerVariableFromEvent(eventName, value)


class PlanetManager():

    def __init__(self):
        self.processingList = []
        self.planets = []
        self.suns = []
        self.planetWarpingList = []
        self.worker = None
        self.format = trinity.PIXEL_FORMAT.B8G8R8A8_UNORM
        self.maxSize = 2048
        self.maxSizeLimit = 2048

    def Release(self):
        self.planets = []
        self.suns = []

    def RegisterPlanetBall(self, planet):
        self.planets.append(planet)

    def UnRegisterPlanetBall(self, planet):
        planet = self.GetPlanet(planet.id)
        if planet is not None:
            self.planets.remove(planet)

    def RegisterSunBall(self, sun):
        self.suns.append(sun)

    def UnRegisterSunBall(self, sun):
        for each in self.suns:
            if each.id == sun.id:
                self.suns.remove(each)
                return

    def DoPlanetPreprocessing(self, planet, size):
        self.processingList.append((planet, size))
        if self.worker is not None:
            if self.worker.alive:
                return
        self.worker = uthread.new(self.PreProcessAll)

    def CreateRenderTarget(self):
        textureQuality = gfxsettings.Get(gfxsettings.GFX_TEXTURE_QUALITY)
        self.maxSizeLimit = size = self.maxSize >> textureQuality
        rt = None
        while rt is None or not rt.isValid:
            rt = trinity.Tr2RenderTarget(2 * size, size, 0, self.format)
            if not rt.isValid:
                if size < 2:
                    return
                self.maxSizeLimit = size = size / 2
                rt = None

        return rt

    def GetPlanet(self, ballid):
        for planet in self.planets:
            if planet.id == ballid:
                return planet
