#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\asteroid.py
import math
import random
import trinity
from eve.client.script.environment.spaceObject.scalableSpaceObject import ScalableSpaceObject

class Asteroid(ScalableSpaceObject):

    def Assemble(self):
        if self.model is None:
            self.logger.error('Cannot Assemble Asteroid, model failed to load')
            return
        super(Asteroid, self).Assemble()
        r = random.Random()
        r.seed(self.id)
        duration = 50.0 * math.log(self.radius)
        rdur = r.random() * 50.0 * math.log(self.radius)
        duration += rdur
        curve = trinity.Tr2CurveRandomAxisRotation()
        curve.seed = self.id % 4294967296L
        curve.period = duration
        self.model.modelRotationCurve = curve


class NonInteractableAsteroid(Asteroid):

    def Assemble(self):
        super(NonInteractableAsteroid, self).Assemble()
        if self.model is not None and hasattr(self.model, 'isPickable'):
            self.model.isPickable = False
