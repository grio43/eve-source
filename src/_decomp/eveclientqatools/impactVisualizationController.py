#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\impactVisualizationController.py
import threading
import trinity
import geo2
import math
import random

class ImpactVisualizationController(object):

    def __init__(self, shipId = None, impactVelocityScalar = 1000, impactObjectMass = 0.0, damageLocatorID = 0, randomize = False):
        self.shipId = shipId
        self.damageLocatorID = damageLocatorID
        self.impactArrow = None
        self.arrowModel = None
        self.impactArrowBoundingRadius = 0.0
        self.impactRotation = geo2.QuaternionRotationSetYawPitchRoll(0.0, math.pi, 0.0)
        self.damageLocatorPos = (0.0, 0.0, 0.0)
        self.arrowPositionUpdater = None
        self.impactVelocity = None
        self.randomize = randomize
        self.arrowModel = trinity.Load('res:/Model/global/impactDirection.red')
        self.impactObjectMass = impactObjectMass
        self.impactVelocityScalar = impactVelocityScalar
        self.SetupImpactArrow()
        self.AddImpactArrowToScene()
        self.damageLocatorsMaxValue = 0
        self.OnSetShipId(self.shipId)

    def Close(self):
        print 'attempting to remove the arrow ...'
        self.RemoveImpactArrowFromScene()
        self.arrowPositionUpdater.Stop()

    def OnSetImpactVelocityScalar(self, value):
        self.impactVelocityScalar = float(value)
        self._OnSetDamageLocator(self.damageLocatorID)

    def OnSetImpactMass(self, impactObjectMass):
        self.impactObjectMass = float(impactObjectMass)

    def SetupImpactArrow(self):
        self.impactArrow = trinity.EveRootTransform()
        self.impactArrow.name = 'DebugImpactArrow'
        self.impactArrow.children.append(self.arrowModel)
        self.arrowPositionUpdater = ArrowPositionUpdater(self.impactArrow)
        self.OnSetImpactMass(self.impactObjectMass)
        self.SetDamageLocator(self.damageLocatorID)

    def AddImpactArrowToScene(self):
        scene = sm.GetService('sceneManager').GetActiveScene()
        scene.objects.append(self.impactArrow)

    def OnSetShipId(self, shipId):
        try:
            shipId = long(shipId)
        except ValueError:
            print "Could not set shipId to '%s'" % shipId
            return False

        if sm.GetService('michelle').GetBall(shipId) is None:
            print "No ball with id '%d' found in ballpark" % shipId
            return False
        print 'Setting ship ID to %d' % shipId
        self.shipId = shipId
        self.arrowPositionUpdater.SetBall(self.GetBall())
        damageLocators = self.GetDamageLocators()
        self.damageLocatorsMaxValue = len(damageLocators) - 1
        self._OnSetDamageLocator(self.damageLocatorID)
        return True

    def GetBall(self, ballID = None):
        if ballID is None:
            ballID = self.shipId
        return sm.GetService('michelle').GetBall(ballID)

    def GetDamageLocators(self):
        return self.GetBall().model.locatorSets.FindByName('damage').locators

    def SetDamageLocator(self, damageLocatorIDString):
        self._OnSetDamageLocator(int(damageLocatorIDString))

    def _OnSetDamageLocator(self, damageLocatorID):
        self.damageLocatorID = damageLocatorID
        self.arrowPositionUpdater.SetDamageLocator(self.damageLocatorID)
        _, rotation, __ = self.GetDamageLocators()[self.damageLocatorID]
        self.impactVelocity = geo2.QuaternionTransformVector(rotation, (0.0, self.impactVelocityScalar, 0.0))
        self.impactVelocity = (-self.impactVelocity[0], -self.impactVelocity[1], -self.impactVelocity[2])
        self.arrowPositionUpdater.SetArrowDirection(self.impactVelocity)

    def RemoveImpactArrowFromScene(self):
        scene = sm.GetService('sceneManager').GetActiveScene()
        objectsToRemove = []
        for o in scene.objects:
            if o.name == 'DebugImpactArrow':
                objectsToRemove.append(o)

        for o in objectsToRemove:
            scene.objects.remove(o)

    def ApplyPhysicalImpact(self):
        if self.randomize:
            newDamageLocatorID = random.randint(0, len(self.GetDamageLocators()) - 1)
            while newDamageLocatorID == self.damageLocatorID:
                newDamageLocatorID = random.randint(0, len(self.GetDamageLocators()) - 1)

            self.damageLocatorID = newDamageLocatorID
            self._OnSetDamageLocator(self.damageLocatorID)
        sm.GetService('michelle').GetBall(self.shipId).ApplyTorqueAtDamageLocator(self.damageLocatorID, self.impactVelocity, self.impactObjectMass)


class ArrowPositionUpdater(object):

    def __init__(self, arrowObject):
        self.arrowObject = arrowObject
        self.stop = False
        self.damageLocator = 0
        self.ball = None
        self.arrowScale = 1.0
        self.arrowDirection = (0.0, 1.0, 0.0)
        self.arrowModel = self.arrowObject.children[0]
        arrowGeometry = self.arrowModel.mesh.geometry
        self.arrowPoint = (0.0, arrowGeometry.GetBoundingBox(0)[1][1], 0.0)
        self.arrowRotation = (0.0, 0.0, 0.0, 1.0)
        self.thread = threading.Thread(target=self.Update)
        self.thread.start()

    def SetDamageLocator(self, damageLocatorIndex):
        self.damageLocator = damageLocatorIndex

    def SetBall(self, ball):
        self.ball = ball
        self.arrowScale = ball.model.GetBoundingSphereRadius() * 0.1
        self.arrowModel.scaling = (self.arrowScale, self.arrowScale, self.arrowScale)

    def SetArrowDirection(self, direction):
        impactDir = geo2.Vec3Normalize(direction)
        self.arrowRotation = geo2.QuaternionRotationArc((0, 1, 0), impactDir)
        if impactDir == (0, -1, 0):
            self.arrowRotation = geo2.QuaternionRotationSetYawPitchRoll(0.0, math.pi, 0.0)

    def Stop(self):
        self.stop = True

    def Update(self):
        print 'starting update thread'
        while not self.stop:
            if self.ball:
                arrowCenter = geo2.QuaternionTransformVector(self.arrowRotation, (self.arrowPoint[0] * self.arrowScale, self.arrowPoint[1] * self.arrowScale, self.arrowPoint[2] * self.arrowScale))
                dl = self.ball.GetModel().GetTransformedDamageLocator(self.damageLocator)
                self.arrowObject.rotation = self.arrowRotation
                self.arrowObject.translation = (dl[0] - arrowCenter[0], dl[1] - arrowCenter[1], dl[2] - arrowCenter[2])

        print 'stopping update thread'
