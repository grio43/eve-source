#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\effects\shipEjector.py
import trinity
import blue
import uthread
from eve.client.script.environment.effects.GenericEffect import GenericEffect, STOP_REASON_DEFAULT, STOP_REASON_BALL_REMOVED
import inventorycommon.const as invC
from fsdBuiltData.common.graphicIDs import GetGraphicFile
SHIP_SIZE_CLASS_LOOKUP_DICTIONARY = {}

class ShipEjector(GenericEffect):
    __guid__ = 'effects.ShipEjector'

    def __init__(self, trigger, effect = None, graphicFile = None):
        super(ShipEjector, self).__init__(trigger, effect, graphicFile)
        shipBall = self.fxSequencer.GetBall(trigger.targetID)
        carrierBall = self.fxSequencer.GetBall(trigger.shipID)
        self.ship = self.effRoot = self.effRoot = gIDOverride = None
        self.lingerOnDeathTime = 10
        if shipBall is not None:
            self.ship = shipBall.GetModel()
        if carrierBall is not None:
            self.carrier = carrierBall.GetModel()
        if trigger.graphicInfo is not None:
            self.lingerOnDeathTime = trigger.graphicInfo.get('deathTimer', 10)
            gIDOverride = trigger.graphicInfo.get('graphicIDOverride', None)
        self.multiEffectPath = graphicFile
        self.sizeClass = self._AssignSizeClass(shipBall)
        self.isReversed = False
        if trigger.graphicInfo is not None:
            rev = trigger.graphicInfo.get('reversed')
            if rev is not None:
                self.isReversed = rev
        if gIDOverride is not None:
            graphicFilePath = GetGraphicFile(gIDOverride)
            if graphicFilePath is not None:
                self.multiEffectPath = graphicFilePath

    def Prepare(self):
        self.gfx = self.RecycleOrLoad(self.multiEffectPath)
        if self.gfx is None:
            raise RuntimeError('shipEjector: no effect defined: %s' % getattr(self, 'graphicFile', 'None'))
        if self.carrier is None:
            raise RuntimeError('shipEjector: the SuperCarrier no longer exists')
        if self.ship is None:
            raise RuntimeError('shipEjector: ship being built no longer exists')
        self.AddToScene(self.gfx)
        if self.ship.modelTranslationCurve is None:
            self.ship.modelTranslationCurve = trinity.Tr2CurveVector3()
        self.gfx.SetParameter('sourceShip', self.carrier)
        self.gfx.SetParameter('objectBeingBuilt', self.ship)
        self.gfx.SetControllerVariable('Build', 1)
        self.gfx.SetControllerVariable('shipSize', self.sizeClass)
        self.carrier.SetControllerVariable('isSpawning', 1)
        if self.isReversed:
            self.gfx.SetControllerVariable('Reversed', 1)
        effLoad = trinity.EveEffectRoot2()
        effLoad.name = 'carrierLink_' + self.ship.name
        effLoad.translation = self.carrier.worldPosition
        self.AddToScene(effLoad)
        if effLoad is not None:
            self.effRoot = effLoad
            self.gfx.SetParameter('buildLink', self.effRoot)
        self._SetupLineSet()

    def Start(self, duration):
        if self.gfx is None:
            raise RuntimeError('shipEjector: no effect defined: %s' % getattr(self, 'graphicFile', 'None'))
        self.gfx.StartControllers()

    def Stop(self, reason = STOP_REASON_DEFAULT):
        if self.gfx is None:
            raise RuntimeError('shipEjector: no effect defined: ' + str(getattr(self, 'graphicFile', 'None')))
        self.RemoveFromScene(self.effRoot)
        self.effRoot = None
        scene = self.fxSequencer.GetScene()
        if reason == STOP_REASON_BALL_REMOVED:
            if self.lingerOnDeathTime is not None:
                uthread.new(ShipEjector._DelayedCleanUp, self.lingerOnDeathTime, self.gfx, scene)
        else:
            self._CleanUp(self.gfx, scene)

    @staticmethod
    def _DelayedCleanUp(timeInSec, model, scene):
        blue.synchro.SleepSim(timeInSec * 1000)
        ShipEjector._CleanUp(model, scene)

    @staticmethod
    def _CleanUp(model, scene):
        if scene is not None and model is not None:
            scene.objects.fremove(model)

    def _GetPoseID(self):
        defaultPosID = 0
        if not isinstance(self.graphicInfo, dict):
            return defaultPosID
        return self.graphicInfo.get('poseID', defaultPosID)

    def _SetupLineSet(self):
        locatorSetName = 'spawn'
        bestIndex = self.carrier.GetCloseLocatorIndex(self.ship.modelWorldPosition, locatorSetName)
        emitLocation = self.carrier.GetLocatorPositionFromSet(bestIndex, True, locatorSetName)
        if emitLocation == (0.0, 0.0, 0.0):
            locatorSetName = 'damage'
            bestIndex = self.carrier.GetCloseLocatorIndex(self.ship.modelWorldPosition, locatorSetName)
            emitLocation = self.carrier.GetLocatorPositionFromSet(bestIndex, True, locatorSetName)
        emitLocation = tuple([emitLocation[0] - self.carrier.worldPosition[0], emitLocation[1] - self.carrier.worldPosition[1], emitLocation[2] - self.carrier.worldPosition[2]])
        direction = self.carrier.GetLocatorRotationFromSet(bestIndex, True, locatorSetName)
        cs = self.gfx.curveSets.FindByName('builder')
        if cs is not None:
            c1 = cs.curves.FindByName('BuildLink_Point1_Offset')
            if c1 is not None:
                c1.input1 = emitLocation[0]
                c1.input2 = emitLocation[1]
                c1.input3 = emitLocation[2]
            c2 = cs.curves.FindByName('BuildLink_BezierPoint_Offset')
            if c2 is not None:
                c2.input1 = emitLocation[0] + self.carrier.boundingSphereRadius * direction[0]
                c2.input2 = emitLocation[1] + self.carrier.boundingSphereRadius * direction[1]
                c2.input3 = emitLocation[2] + self.carrier.boundingSphereRadius * direction[2]
            c3 = cs.curves.FindByName('TimeScale_ Multiplier')
            if c3 is not None:
                c3.input1 = 1.0 / blue.os.desiredSimDilation

    def _AssignSizeClass(self, shipBall):
        targetGID = shipBall.typeData.get('groupID')
        assignedGroup = SHIP_SIZE_CLASS_LOOKUP_DICTIONARY.get(targetGID)
        if assignedGroup is not None:
            return assignedGroup
        assignedGroup = 0
        rad = self.ship.boundingSphereRadius or 200
        for i in [70,
         115,
         170,
         215]:
            if rad > i:
                assignedGroup += 1

        return assignedGroup


class CapsuleFlare(GenericEffect):
    __guid__ = 'effects.CapsuleFlare'

    def __init__(self, trigger, effect = None, graphicFile = None):
        super(CapsuleFlare, self).__init__(trigger, effect, graphicFile)
        self.gfxPath = graphicFile
        self.gfx = self.ship = None
        shipBall = self.fxSequencer.GetBall(trigger.shipID)
        if shipBall is not None:
            self.ship = shipBall.GetModel()

    def Prepare(self):
        self.gfx = self.RecycleOrLoad(self.gfxPath)
        if self.gfx is None:
            raise RuntimeError('CapsuleFlare: no effect defined: %s' % getattr(self, 'graphicFile', 'None'))
        if self.gfx.translation is not None and self.ship is not None:
            self.gfx.translation = self.ship.worldPosition
        self.AddToScene(self.gfx)
        self.gfx.StartControllers()

    def Start(self, duration):
        if self.gfx is None:
            raise RuntimeError('CapsuleFlare: no effect defined: %s' % getattr(self, 'graphicFile', 'None'))

    def Stop(self, reason = STOP_REASON_DEFAULT):
        if self.gfx is None:
            raise RuntimeError('CapsuleFlare: no effect defined: ' + str(getattr(self, 'graphicFile', 'None')))
        self.RemoveFromScene(self.gfx)
        self.gfx = None

    def _GetPoseID(self):
        defaultPosID = 0
        if not isinstance(self.graphicInfo, dict):
            return defaultPosID
        return self.graphicInfo.get('poseID', defaultPosID)


def _CreateShipSizeClassLookUpTable():
    sizeMapping = [[invC.groupCorvette,
      invC.groupShuttle,
      invC.groupFrigate,
      invC.groupAssaultFrigate],
     [invC.groupInterceptor,
      invC.groupCommandDestroyer,
      invC.groupTacticalDestroyer,
      invC.groupDestroyer],
     [invC.groupCruiser,
      invC.groupBlockadeRunner,
      invC.groupStealthBomber,
      invC.groupLogisticsFrigate,
      invC.groupCombatReconShip,
      invC.groupCommandShip,
      invC.groupElectronicAttackShips],
     [invC.groupBattlecruiser,
      invC.groupAttackBattlecruiser,
      invC.groupInterdictor,
      invC.groupHeavyAssaultCruiser,
      invC.groupHeavyInterdictors,
      invC.groupStrategicCruiser,
      invC.groupBlackOps,
      invC.groupMarauders],
     [invC.groupBattleship,
      invC.groupJumpFreighter,
      invC.groupLogistics,
      invC.groupDreadnought,
      invC.groupTitan,
      invC.groupCarrier,
      invC.groupSupercarrier,
      invC.groupForceAux,
      invC.groupLancerDreadnought]]
    classMapping = []
    for i in range(0, len(sizeMapping)):
        classMapping = classMapping + [i] * len(sizeMapping[i])

    return dict(zip(sum(sizeMapping, []), classMapping))


SHIP_SIZE_CLASS_LOOKUP_DICTIONARY = _CreateShipSizeClassLookUpTable()
