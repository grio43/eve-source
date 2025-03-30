#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveSpaceObject\moonDrillComponent.py
from eve.client.script.environment.model.turretSet import TurretSet
import blue
import inventorycommon.const as const
import geo2
import trinity
import tacticalNavigation.ballparkFunctions as ballparkFunctions
import decometaclass
import uthread2

class BallWrapper(decometaclass.WrapBlueClass('destiny.ClientBall')):
    __persistdeco__ = 0
    __update_on_reload__ = 1


class MoonDrillComponent:

    def __init__(self, michelle, ballid, moduleID, moduleTypeID):
        self.michelle = michelle
        self.ballID = ballid
        structure = michelle.GetBall(ballid)
        self.ball = structure
        self.model = structure.model
        self.faction = structure.typeData.get('sofFactionName', None)
        self.turretSet = None
        self.turretSetModel = None
        self.moon = None
        self.moonID = None
        self.chunkID = None
        self._chunkBall = None
        self.moonDirection = None
        self.targetBall = None
        self.targetModel = trinity.EveEffectRoot2()
        self.moduleID = moduleID
        self.moduleTypeID = moduleTypeID
        self._FitTurret()
        self._SetupMoonConnection()
        self._SetupTargetPoint()

    def FitHardpoints(self, michelle, moonID, structureID, itemID):
        self.moonID = moonID
        self.structureID = structureID
        targetMoonBall = michelle.GetBall(moonID)
        structureBall = michelle.GetBall(structureID)
        eveTurretSet = None
        ts = structureBall.modules.get(itemID, None)
        if ts is not None:
            if len(ts.turretSets) > 0:
                eveTurretSet = ts.turretSets[0]
        if eveTurretSet is not None:
            eveTurretSet.targetObject = targetMoonBall.model
            eveTurretSet.EnterStateTargeting()
        print 'MoonDrillComponent::FitHardpoints -> ' + str(targetMoonBall.model) + ' : ' + str(eveTurretSet.name)

    def Teardown(self):
        if self.targetBall is not None:
            ballparkFunctions.RemoveClientBall(self.targetBall)
            self.targetBall = None
        if self.targetModel is not None:
            self.targetModel.translationCurve = None
            scene = sm.GetService('space').GetScene()
            scene.objects.fremove(self.targetModel)

    def GetTarget(self, targetID):
        if self.moduleID is None:
            return
        if targetID != self.moonID:
            return
        return self.targetBall

    def _FitTurret(self):
        pass

    def _SetupMoonConnection(self):
        bp = self.michelle.GetBallpark()
        dist = 1e+100
        closestID = None
        for ballID, slimItem in bp.slimItems.iteritems():
            if slimItem.groupID == const.groupMoon:
                test = bp.DistanceBetween(self.ballID, ballID)
                if test < dist:
                    dist = test
                    closestID = ballID

        if closestID is None:
            return
        self.moonID = closestID
        self.moon = self.michelle.GetBall(closestID)
        self.moonDirection = geo2.Vec3NormalizeD(geo2.Vec3SubtractD((self.ball.x, self.ball.y, self.ball.z), (self.moon.x, self.moon.y, self.moon.z)))

    def _SetupTargetPoint(self):
        moonDirScaled = geo2.Vec3ScaleD(self.moonDirection, self.moon.radius)
        position = geo2.Vec3AddD((self.moon.x, self.moon.y, self.moon.z), moonDirScaled)
        self.targetBall = BallWrapper(ballparkFunctions.AddClientBall(position))
        self.targetModel.translationCurve = self.targetBall
        self.targetBall.model = self.targetModel
        scene = sm.GetService('space').GetScene()
        scene.objects.append(self.targetModel)
        if self.chunkID is None:
            self.SetMoonChunk(None)

    def PlaceSurfaceImpact(self):
        surfaceObject = trinity.Load('res:/fisfx/structure/moonmining/moonmining_surfaceeffect_01a.red')
        surfaceObject.translationCurve = self.moon
        surfaceObject.scaling = (self.moon.radius, self.moon.radius, self.moon.radius)
        surfaceObject.rotation = geo2.QuaternionRotationArc((0, 1, 0), self.moonDirection)
        scene = sm.GetService('space').GetScene()
        scene.objects.append(surfaceObject)

        def _delayed_remove():
            blue.synchro.SleepSim(40000.0)
            scene.objects.fremove(surfaceObject)

        uthread2.start_tasklet(_delayed_remove)

    def SetMoonChunk(self, chunk):
        pass
