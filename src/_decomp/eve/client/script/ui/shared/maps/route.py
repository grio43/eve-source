#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\maps\route.py
import blue
import trinity
import geo2
from eve.client.script.ui.shared.maps.mapcommon import STARMAP_SCALE
LINESET_EFFECT = 'res:/Graphics/Effect/Managed/Space/SpecialFX/LinesAdditive.fx'
TIME_BASE = 0.25
BALL_SCALE = 30.0

class MapRoute(object):
    __persistvars__ = ['sr']

    def __init__(self):
        self.destinations = None
        self.model = None
        self.scale = STARMAP_SCALE
        self.ballScale = BALL_SCALE
        self.timeBase = TIME_BASE
        self.lineColor = None
        self.resPath = 'res:/dx9/model/Sprite/MapRouteSprite.red'

    def DrawRoute(self, destinations, usePoints = False, drawLines = False, blinking = True, flattened = False, rotationQuaternion = None):
        if not len(destinations):
            self.destinations = []
            if self.model:
                self.model.diplay = False
            return
        if self.model:
            self.model.display = True
        else:
            self.model = trinity.Load(self.resPath)
            self.model.name = '__mapRoute'
            self.model.scaling = (self.ballScale, self.ballScale, self.ballScale)
            if not blinking:
                self.model.curveSets.removeAt(0)
            if drawLines:
                self.lineSet = trinity.EveLineSet()
                self.lineSet.effect = trinity.Tr2Effect()
                self.lineSet.effect.effectFilePath = LINESET_EFFECT
        transCurve = trinity.Tr2CurveVector3()
        transCurve.SetExtrapolation(trinity.Tr2CurveExtrapolation.CYCLE)
        if type(rotationQuaternion) != trinity.TriQuaternion and rotationQuaternion is not None:
            rotationQuaternion = trinity.TriQuaternion(*rotationQuaternion)
        emptyVector = (0.0, 0.0, 0.0)
        if usePoints:
            for index, point in enumerate(destinations):
                pos = trinity.TriVector(*point)
                if flattened:
                    pos.y = 0.0
                if rotationQuaternion is not None:
                    pos.TransformQuaternion(rotationQuaternion)
                pos.Scale(self.scale)
                pythonPos = (pos.x, pos.y, pos.z)
                transCurve.AddKey(index * self.timeBase, pythonPos, trinity.Tr2CurveInterpolation.LINEAR)

            if drawLines:
                numPoints = len(destinations)
                for index in xrange(numPoints):
                    index2 = (index + 1) % numPoints
                    p1 = geo2.Vector(*destinations[index]) * self.scale
                    p2 = geo2.Vector(*destinations[index2]) * self.scale
                    self.lineSet.AddLine(p1, self.lineColor, p2, self.lineColor)

                self.lineSet.SubmitChanges()
        else:
            map = sm.StartService('map')
            for index, destinationID in enumerate(destinations):
                destination = cfg.evelocations.Get(destinationID)
                pos = trinity.TriVector(destination.x, destination.y, destination.z)
                if flattened:
                    pos.y = 0.0
                if rotationQuaternion is not None:
                    pos.TransformQuaternion(rotationQuaternion)
                pos.Scale(self.scale)
                pythonPos = (pos.x, pos.y, pos.z)
                transCurve.AddKey(index * 2 * self.timeBase, pythonPos, trinity.Tr2CurveInterpolation.LINEAR)
                transCurve.AddKey((index * 2 + 1.0) * self.timeBase, pythonPos, trinity.Tr2CurveInterpolation.LINEAR)

        now = blue.os.GetSimTime()
        self.model.translationCurve = trinity.Tr2TranslationAdapter()
        self.model.translationCurve.curve = transCurve
        if blinking:
            self.model.curveSets[0].scale = 2.0
            self.model.curveSets[0].PlayFrom(float(now / const.SEC))
        self.destinations = destinations
