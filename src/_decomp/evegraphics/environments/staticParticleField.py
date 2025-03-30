#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\environments\staticParticleField.py
import evetypes
import trinity
import geo2
from fsdBuiltData.client.groupGraphics import GetColorFromTypeID
from evegraphics.environments import BaseEnvironmentObject
import evegraphics.settings as gfxsettings
import logging
log = logging.getLogger(__name__)

class AddObjectError(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


def AddClientBall(pos):
    from environmentManager import EnvironmentManager
    if EnvironmentManager.BALLPARK_MODE:
        from tacticalNavigation.ballparkFunctions import AddClientBall
        return AddClientBall(pos)


class StaticParticleField(BaseEnvironmentObject):

    def __init__(self, meshFile, maxParticleCount, particleMinSize, particleMaxSize, density, staticClusters):
        super(StaticParticleField, self).__init__()
        self.clusterBalls = []
        self.staticParticleField = None
        self.meshFile = meshFile
        self.maxParticleCount = maxParticleCount
        self.particleMinSize = particleMinSize
        self.particleMaxSize = particleMaxSize
        self.density = density
        self.staticClusters = staticClusters

    def Setup(self):
        log.debug("Setting up static particle field '%s'" % self.meshFile)
        self.staticParticleField = trinity.EveSceneStaticParticles()
        self.staticParticleField.mesh = self.Load(self.meshFile)
        self.staticParticleField.maxParticleCount = self.maxParticleCount
        self.staticParticleField.maxSize = self.particleMaxSize
        self.staticParticleField.minSize = self.particleMinSize
        self.staticParticleField.clusterParticleDensity = self.density
        for curve in self.environmentTranslationCurves:
            curvePosition = (curve.x, curve.y, curve.z)
            for i, cluster in self.staticClusters.iteritems():
                positions = []
                radius = cluster.radius
                if radius <= 0.0:
                    return
                if cluster.position is not None:
                    positions = [(cluster.position.x, cluster.position.y, cluster.position.z)]
                elif cluster.modelLocatorSetName:
                    if not hasattr(curve, 'GetModel'):
                        return
                    model = curve.GetModel()
                    if model is None:
                        return
                    locatorSet = model.locatorSets.FindByName(cluster.modelLocatorSetName)
                    if locatorSet is not None:
                        modelRotation = geo2.MatrixRotationQuaternion(getattr(model.rotationCurve, 'currentValue', (0, 0, 0, 1)))
                        for location in locatorSet.locators:
                            pos = geo2.Vec3Transform(location[0], modelRotation)
                            positions.append(pos)

                    else:
                        log.warning("Could not find locator with name '%s' on for environment", cluster.modelLocatorSetName)
                for position in positions:
                    pos = map(sum, zip(curvePosition, position))
                    ball = AddClientBall(pos)
                    self.AddCluster(pos, radius, cluster.color, cluster.baseColor, ball)

    def IsDisabled(self):
        return gfxsettings.Get(gfxsettings.UI_ASTEROID_ATMOSPHERICS) == 0

    def IsReady(self):
        return self.staticParticleField is not None

    def ApplyToScene(self):
        if self.IsDisabled():
            return
        self.RebuildParticleField()
        self.scene.staticParticles.append(self.staticParticleField)

    def AddObjects(self, environmentObjects):
        addedObject = False
        for environmentObject in environmentObjects:
            groupID = evetypes.GetGroupID(environmentObject.typeID)
            for _, staticCluster in self.staticClusters.iteritems():
                if groupID in staticCluster.groupIdFilter:
                    addedObject = True
                    color = getattr(staticCluster, 'color', None)
                    color = color or GetColorFromTypeID(environmentObject.typeID, (1.0, 1.0, 1.0, 1.0))
                    baseColor = tuple(staticCluster.baseColor)
                    ball = getattr(environmentObject, 'ball', None)
                    if ball:
                        ball = environmentObject.ball
                        if ball.GetModel() is not None:
                            radius = max(ball.radius, ball.GetModel().boundingSphereRadius)
                        else:
                            radius = ball.radius
                        self.clusterBalls.append(ball)
                    else:
                        radius = environmentObject.radius
                    self.AddCluster(environmentObject.position, radius, color, baseColor, ball)

        if addedObject:
            log.info('Added clusters to environment at position %s', self.environmentPosition)
            self.RebuildParticleField()

    def AddCluster(self, worldPosition, radius, color, baseColor, ball):
        if self.staticParticleField is None:
            return
        worldPos = worldPosition
        ballID = 0
        if ball is None:
            ballWorldPosition = [ x + y for x, y in zip(worldPosition, self.environmentPosition) ]
            ball = AddClientBall(ballWorldPosition)
            if ball is not None:
                worldPos = (ball.x, ball.y, ball.z)
                ballID = ball.id
            else:
                worldPos = ballWorldPosition
        seed = int(ballID % 123456)
        self.staticParticleField.AddCluster(worldPos, radius, color, baseColor, seed)

    def RebuildParticleField(self):
        log.debug('Rebuilding particle field')
        self.staticParticleField.Rebuild()

    def LinkToDistanceField(self, distanceFieldEnvironmentItem):
        for ball in self.clusterBalls:
            distanceFieldEnvironmentItem.AddBallToField(ball)

    def TearDown(self):
        log.debug('Tearing down static particle field')
        if self.staticParticleField is not None:
            self.staticParticleField.ClearClusters()
            self.staticParticleField.mesh = None
            if self.scene and self.staticParticleField in self.scene.staticParticles:
                self.scene.staticParticles.fremove(self.staticParticleField)
            del self.staticParticleField
            self.staticParticleField = None
        self.clusterBalls = []
        self.scene = None
