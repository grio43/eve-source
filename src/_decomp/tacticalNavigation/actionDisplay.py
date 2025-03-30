#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\tacticalNavigation\actionDisplay.py
import blue
import destiny
import math
import tacticalNavigation.ui.util as tacticalui
import uthread2
from ballparkFunctions import GetBall, GetBallpark
from destructionEffect import destructionType as destructionEffectType
from eve.client.script.ui.inflight.squadrons.shipFighterState import GetShipFighterState

class ActionDisplay:

    def __init__(self, navPointContainer):
        self.shipid = 'shipid'
        self.items = [self.shipid]
        self.targetConnectors = {}
        self.orbitConnectors = {}
        self.navPointContainer = navPointContainer
        self.itemKeyToNavPoint = {}
        self.abilityTargets = {}
        self.shipFighterState = None
        self._updateThreadRunning = False

    def Enable(self, enable):
        if enable:
            if self.shipid not in self.items:
                self.items.append(self.shipid)
            if not self._updateThreadRunning:
                self._updateThreadRunning = True
                uthread2.StartTasklet(self._UpdateThread)
        else:
            self.ClearAll()
            self._updateThreadRunning = False

    def SetMaxMoveRange(self, range):
        self.maxMoveDistance = range * 2.0

    def _SetNavigationPoint(self, itemKey, globalPosition):
        ballID = self._GetBallID(itemKey)
        if self._HasCorrectNavPoint(itemKey, globalPosition):
            return self.itemKeyToNavPoint[itemKey]
        self._RemoveNavPointForBall(itemKey)
        navPoint = self.navPointContainer.GetOrCreatePoint(globalPosition)
        self.navPointContainer.ConfirmNavPoint(ballID, navPoint)
        self.itemKeyToNavPoint[itemKey] = navPoint
        return navPoint

    def _RemoveNavPointForBall(self, itemKey):
        if itemKey in self.itemKeyToNavPoint:
            oldNavPoint = self.itemKeyToNavPoint[itemKey]
            self.navPointContainer.Dereference(oldNavPoint)
            del self.itemKeyToNavPoint[itemKey]

    def _HasCorrectNavPoint(self, itemKey, globalPosition):
        if itemKey in self.itemKeyToNavPoint:
            oldNavPoint = self.itemKeyToNavPoint[itemKey]
            if oldNavPoint.globalPosition == globalPosition:
                return True
        return False

    def _GetBallID(self, itemKey):
        if itemKey == self.shipid:
            return session.shipid
        return itemKey

    def _ClearUIForItem(self, itemKey):
        itemID = self._GetBallID(itemKey)
        if itemKey in self.itemKeyToNavPoint:
            self._RemoveNavPointForBall(itemKey)
        if itemKey in self.targetConnectors:
            self._RemoveMovementLine(itemKey)
        if itemKey in self.orbitConnectors:
            self._RemoveOrbit(itemKey)
        if itemID in self.abilityTargets:
            for targetID in self.abilityTargets[itemID]:
                connector = self.abilityTargets[itemID][targetID]
                connector.Destroy()

            del self.abilityTargets[itemID]

    def ClearAll(self):
        for itemKey in self.items:
            self._ClearUIForItem(itemKey)

        self.positionToNavPoint = {}
        self.itemKeyToNavPoint = {}
        self.abilityTargets = {}
        self.items = [self.shipid]

    def _AddMovementLine(self, itemKey, sourceBall, targetBall, maxDistance):
        if targetBall is None:
            return
        if itemKey in self.targetConnectors:
            self.targetConnectors[itemKey].SetDestinationCurve(targetBall)
            self.targetConnectors[itemKey].lineConnector.length = maxDistance
        else:
            connector = tacticalui.CreateMovementConnector(sourceBall, targetBall)
            self.targetConnectors[itemKey] = connector
            self.targetConnectors[itemKey].lineConnector.length = maxDistance

    def _RemoveMovementLine(self, itemKey):
        if itemKey in self.targetConnectors:
            connector = self.targetConnectors[itemKey]
            connector.Destroy()
            del self.targetConnectors[itemKey]

    def _SetOrbitLine(self, itemKey, sourceBall, targetBall):
        if itemKey in self.orbitConnectors:
            connector = self.orbitConnectors[itemKey]
            self.orbitConnectors[itemKey].SetDestinationCurve(targetBall)
            self.orbitConnectors[itemKey].SetSourceCurve(sourceBall)
        else:
            connector = tacticalui.CreateOrbitConenctor(sourceBall, targetBall)
            self.orbitConnectors[itemKey] = connector
        connector.lineConnector.length = targetBall.radius + sourceBall.followRange + sourceBall.radius
        precession = 0.001
        currentTime = GetBallpark().currentTime
        phi1 = currentTime * precession
        phi2 = (sourceBall.id & 65535) + currentTime * precession
        x = math.cos(phi1) * math.cos(phi2)
        y = math.sin(phi2)
        z = math.sin(phi1) * math.cos(phi2)
        connector.lineConnector.planeNormal = (x, y, z)

    def _RemoveOrbit(self, itemKey):
        if itemKey in self.orbitConnectors:
            connector = self.orbitConnectors[itemKey]
            connector.Destroy()
            del self.orbitConnectors[itemKey]

    def AddFighter(self, fighterID):
        if fighterID in self.items:
            return
        if self.shipFighterState is None:
            self.shipFighterState = GetShipFighterState()
            self.shipFighterState.ConnectFighterTargetUpdatedHandler(self._OnFighterTargetUpdate)
        self.items.append(fighterID)
        self._RebuildConnectorsForFighter(fighterID)

    def _OnFighterTargetUpdate(self, fighterID, abilitySlotID, targetID):
        self._RebuildConnectorsForFighter(fighterID)

    def _RebuildConnectorsForFighter(self, fighterID):
        if fighterID not in self.abilityTargets:
            self.abilityTargets[fighterID] = {}
        fighterBall = GetBall(fighterID)
        if fighterBall is None:
            return
        targets = self.shipFighterState.GetAbilityTargetsForFighter(fighterID)
        for targetID in self.abilityTargets[fighterID]:
            connector = self.abilityTargets[fighterID][targetID]
            connector.Destroy()

        self.abilityTargets[fighterID] = {}
        for targetID in targets:
            targetBall = GetBall(targetID)
            if targetBall is not None and not (getattr(targetBall, 'released', False) or getattr(targetBall, 'destructionEffectId', destructionEffectType.NONE) is not destructionEffectType.NONE):
                connector = tacticalui.CreateAgressionConnector(fighterBall, targetBall)
                self.abilityTargets[fighterID][targetID] = connector

        self._UpdateItem(fighterID)

    def RemoveFighter(self, fighterID):
        self.items.remove(fighterID)
        self._ClearUIForItem(fighterID)

    def RemoveBall(self, ballID):
        rebuildFighters = []
        for fighterID in self.abilityTargets:
            if ballID in self.abilityTargets[fighterID]:
                rebuildFighters.append(fighterID)

        for fighterID in rebuildFighters:
            self._RebuildConnectorsForFighter(fighterID)

    def _GetMode(self, ball):
        mode = None
        if ball.mode == destiny.DSTBALL_GOTO:
            mode = destiny.DSTBALL_GOTO
        elif ball.mode == destiny.DSTBALL_ORBIT:
            mode = ball.mode
        elif ball.followId != 0:
            mode = destiny.DSTBALL_FOLLOW
        return mode

    def _UpdateItem(self, itemKey):
        ballID = self._GetBallID(itemKey)
        ball = GetBall(ballID)
        if ball is None:
            self._ClearUIForItem(ballID)
            return
        maxMoveDistance = 0
        if itemKey == self.shipid:
            maxMoveDistance = self.maxMoveDistance
        followBall = None
        if ballID == session.structureid:
            mode = None
        else:
            mode = self._GetMode(ball)
        if mode == destiny.DSTBALL_FOLLOW or mode == destiny.DSTBALL_ORBIT:
            followBall = GetBall(ball.followId)
            self._RemoveNavPointForBall(itemKey)
        elif mode == destiny.DSTBALL_GOTO:
            globalPosition = (ball.gotoX, ball.gotoY, ball.gotoZ)
            followBall = self._SetNavigationPoint(itemKey, globalPosition).GetNavBall()
            if followBall is None:
                self._RemoveNavPointForBall(itemKey)
        else:
            self._RemoveNavPointForBall(itemKey)
        if followBall is None:
            self._RemoveMovementLine(itemKey)
        elif ballID in self.abilityTargets and followBall.id in self.abilityTargets[ballID]:
            self._RemoveMovementLine(itemKey)
        elif mode == destiny.DSTBALL_ORBIT:
            self._RemoveMovementLine(itemKey)
        else:
            self._AddMovementLine(itemKey, ball, followBall, maxMoveDistance)
        if mode == destiny.DSTBALL_ORBIT and followBall:
            self._SetOrbitLine(itemKey, ball, followBall)
        else:
            self._RemoveOrbit(itemKey)

    def _UpdateThread(self):
        while self._updateThreadRunning:
            for each in self.items:
                self._UpdateItem(each)

            blue.synchro.SleepSim(500)
