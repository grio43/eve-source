#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\bracketsAndTargets\blinkingSpriteOnSharedCurve.py
import trinity
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore

class BlinkingSpriteOnSharedCurve(Sprite):

    def ApplyAttributes(self, attributes):
        Sprite.ApplyAttributes(self, attributes)
        self.blinkBinding = None
        curveSetName = attributes.curveSetName
        self.curveSetName = curveSetName
        fromCurveValue = attributes.get('fromCurveValue', 0.3)
        toCurveValue = attributes.get('toCurveValue', 0.6)
        duration = attributes.get('duration', 0.5)
        self.SetupSharedBlinkingCurve(curveSetName, fromCurveValue, toCurveValue, duration)

    def SetupSharedBlinkingCurve(self, cuverSetName, fromCurveValue, toCurveValue, duration, *args):
        curveSet = getattr(uicore, cuverSetName, None)
        if curveSet:
            curve = curveSet.curves[0]
        else:
            curveSet = trinity.TriCurveSet()
            setattr(uicore, cuverSetName, curveSet)
            setattr(curveSet, 'name', cuverSetName)
            trinity.device.curveSets.append(curveSet)
            curveSet.Play()
            curve = trinity.Tr2CurveScalar()
            curve.name = 'blinking_curve'
            curve.AddKey(0, fromCurveValue, trinity.Tr2CurveInterpolation.LINEAR)
            curve.AddKey(duration / 2.0, toCurveValue, trinity.Tr2CurveInterpolation.LINEAR)
            curve.AddKey(duration, fromCurveValue, trinity.Tr2CurveInterpolation.LINEAR)
            curve.extrapolationAfter = trinity.Tr2CurveExtrapolation.CYCLE
            curveSet.curves.append(curve)
        if getattr(self, 'blinkBinding', None) is not None:
            curveSet.bindings.remove(self.blinkBinding)
        self.blinkBinding = trinity.CreatePythonBinding(curveSet, curve, 'currentValue', self, 'opacity')

    def Close(self):
        if getattr(self, 'blinkBinding', None) is not None:
            curveSet = getattr(uicore, self.curveSetName, None)
            if curveSet:
                curveSet.bindings.remove(self.blinkBinding)
            self.blinkBinding = None
        Sprite.Close(self)
