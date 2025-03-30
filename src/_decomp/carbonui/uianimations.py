#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\uianimations.py
import math
import blue
import telemetry
import trinity
from carbon.common.lib.const import SEC
from carbonui import uiconst
from carbonui.util.color import Color
OVERSHOT_TIME = 0.4

class UIAnimations(object):
    CURVE_BLINK = 1

    def __init__(self):
        self.curveSetByObjectIDAttrName = {}
        self.curveByObjectIDAttrName = {}

    def CreateCurveSet(self, useRealTime = True):
        curveSet = trinity.TriCurveSet()
        curveSet.useRealTime = useRealTime
        trinity.device.curveSets.append(curveSet)
        return curveSet

    def Play(self, curve, obj, attrName, loops = 1, callback = None, sleep = False, curveSet = None):
        if loops is uiconst.ANIM_REPEAT or loops > 1:
            for each in curve.Find('trinity.Tr2CurveScalar'):
                each.extrapolationAfter = trinity.Tr2CurveExtrapolation.CLAMP
                each.extrapolationAfter = trinity.Tr2CurveExtrapolation.CYCLE

        curveSet = self._GetOrCreateCurveSet(curveSet, obj)
        curveSet.curves.append(curve)
        self.StopAnimation(obj, attrName)
        self.RegisterCurvesetForObject(obj, curveSet, attrName)
        self.RegisterCurveForObject(obj, curve, attrName)
        if hasattr(obj, '__iroot__'):
            binding = trinity.CreateBinding(curveSet, curve, 'currentValue', obj, attrName)
        else:
            try:
                obj.isAnimated = True
            except AttributeError:
                pass

            binding = trinity.CreatePythonBinding(curveSet, curve, 'currentValue', obj, attrName)
        binding.name = getattr(obj, 'name', str(id(obj))) + '_' + attrName
        if not curveSet.isPlaying:
            curveSet.Play()
        if loops == uiconst.ANIM_REPEAT:
            return curveSet
        duration = loops * curveSet.GetMaxCurveDuration()
        duration += self.GetMaxTimeOffset(curveSet)
        if callback:
            curveSet.StopAfterWithCallback(duration, callback)
        else:
            curveSet.StopAfter(duration)
        if sleep:
            blue.pyos.synchro.SleepWallclock(duration * 1000)
        return curveSet

    def _GetOrCreateCurveSet(self, curveSet, obj):
        if not curveSet:
            curveSet = self.CreateCurveSet(useRealTime=True)
            curveSet.name = getattr(obj, 'name', str(id(obj)))
        elif isinstance(curveSet, basestring):
            for cs in trinity.device.curveSets:
                if cs.name == curveSet:
                    curveSet = cs
                    break
            else:
                name = curveSet
                curveSet = self.CreateCurveSet(useRealTime=True)
                curveSet.name = name

        return curveSet

    def SyncPlayback(self, curveset):
        duration = 0.0
        for curve in curveset.curves[0].Find('trinity.Tr2CurveScalar'):
            duration = max(curve.keys[-1][0], duration)

        if duration == 0:
            return
        timeOffset = blue.os.GetWallclockTime() % (SEC * duration) / float(SEC)
        curveset.scaledTime += timeOffset

    def RegisterCurvesetForObject(self, obj, curveSet, attrName):
        key = self._GetKey(attrName, obj)
        self.curveSetByObjectIDAttrName[key] = blue.BluePythonWeakRef(curveSet)
        self.curveSetByObjectIDAttrName[key].callback = lambda : self.OnCurveSetWeakRefLost(key)

    def RegisterCurveForObject(self, obj, curve, attrName):
        key = self._GetKey(attrName, obj)
        self.curveByObjectIDAttrName[key] = blue.BluePythonWeakRef(curve)
        self.curveByObjectIDAttrName[key].callback = lambda : self.OnCurveWeakRefLost(key)

    def StopAnimation(self, obj, attrName):
        key = self._GetKey(attrName, obj)
        self._StopAndRemoveCurveSet(key)

    def _GetKey(self, attrName, obj):
        return (id(obj), attrName)

    def _StopAndRemoveCurveSet(self, key):
        curveSet = self.curveSetByObjectIDAttrName.pop(key, None)
        if curveSet:
            curveSet.callback = None
            curveSet = curveSet.object
        curve = self.curveByObjectIDAttrName.pop(key, None)
        if curve:
            curve.callback = None
            curve = curve.object
        if curve and curveSet:
            curveSet.curves.remove(curve)
        if curveSet and not curveSet.curves:
            curveSet.Stop()

    @telemetry.ZONE_METHOD
    def StopAllAnimations(self, obj):
        objID = id(obj)
        for key in self._GetToRemoveKeys(objID):
            self._StopAndRemoveCurveSet(key)

    def _GetToRemoveKeys(self, objID):
        toRemove = set()
        for key, curveSet in self.curveSetByObjectIDAttrName.iteritems():
            _objID, attrName = key
            if _objID == objID:
                toRemove.add(key)

        for key, curveSet in self.curveByObjectIDAttrName.iteritems():
            _objID, attrName = key
            if _objID == objID:
                toRemove.add(key)

        return toRemove

    def GetAnimationCurveSet(self, obj, attrName):
        key = self._GetKey(attrName, obj)
        wr = self.curveSetByObjectIDAttrName.get(key, None)
        if wr:
            return wr.object

    def IsAnimating(self, obj, attrName):
        return bool(self.curveSetByObjectIDAttrName.get(self._GetKey(attrName, obj), False))

    def OnCurveSetWeakRefLost(self, key):
        self._StopAndRemoveCurveSet(key)

    def OnCurveWeakRefLost(self, key):
        self._StopAndRemoveCurveSet(key)

    def GetMaxTimeOffset(self, curveSet):
        curves = curveSet.curves.Find('trinity.Tr2CurveScalar')
        if not curves:
            return 0.0
        return max([ getattr(curve, 'timeOffset', 0.0) for curve in curves ])

    def MorphScalar(self, obj, attrName, startVal = 0.0, endVal = 1.0, duration = 0.75, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, curveSet = None, timeOffset = 0.0):
        curve = self.GetScalar(startVal, endVal, duration, curveType, timeOffset=timeOffset)
        return self.Play(curve, obj, attrName, loops, callback, sleep, curveSet)

    def MorphVector2(self, obj, attrName, startVal = (0.0, 0.0), endVal = (1.0, 1.0), duration = 0.75, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, timeOffset = 0.0, curveSet = None):
        curve = self.GetVector2(startVal, endVal, duration, curveType, timeOffset=timeOffset)
        return self.Play(curve, obj, attrName, loops, callback, sleep, curveSet)

    def MorphVector3(self, obj, attrName, startVal = (0.0, 0.0, 0.0), endVal = (1.0, 1.0, 1.0), duration = 0.75, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, timeOffset = 0.0, curveSet = None):
        curve = self.GetVector3(startVal, endVal, duration, curveType, timeOffset=timeOffset)
        return self.Play(curve, obj, attrName, loops, callback, sleep, curveSet)

    def MorphQuaternion(self, obj, attrName, startVal = (0.0, 0.0), endVal = (1.0, 1.0), duration = 0.75, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, timeOffset = 0.0, curveSet = None):
        curve = self.GetQuaternion(startVal, endVal, duration, curveType, timeOffset=timeOffset)
        return self.Play(curve, obj, attrName, loops, callback, sleep, curveSet)

    def FadeTo(self, obj, startVal = 0.0, endVal = 1.0, duration = 0.75, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, curveSet = None, timeOffset = 0.0):
        if hasattr(obj, 'opacity'):
            curve = self.GetScalar(startVal, endVal, duration, curveType, timeOffset=timeOffset)
            attrName = 'opacity'
        else:
            c = obj.color
            if isinstance(c, tuple):
                curve = self.GetColorCurve((c[0],
                 c[1],
                 c[2],
                 startVal), (c[0],
                 c[1],
                 c[2],
                 endVal), duration, curveType, timeOffset=timeOffset)
            else:
                curve = self.GetColorCurve((c.r,
                 c.g,
                 c.b,
                 startVal), (c.r,
                 c.g,
                 c.b,
                 endVal), duration, curveType, timeOffset=timeOffset)
            attrName = 'color'
        return self.Play(curve, obj, attrName, loops, callback, sleep, curveSet=curveSet)

    def FadeIn(self, obj, endVal = 1.0, duration = uiconst.TIME_ENTRY, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, curveSet = None, timeOffset = 0.0):
        startVal = getattr(obj, 'opacity', 0.0)
        return self.FadeTo(obj, startVal, endVal, duration, loops, curveType, callback, sleep, curveSet=curveSet, timeOffset=timeOffset)

    def FadeOut(self, obj, duration = uiconst.TIME_EXIT, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, curveSet = None, timeOffset = 0.0):
        startVal = getattr(obj, 'opacity', 0.0)
        return self.FadeTo(obj, startVal, 0.0, duration, loops, curveType, callback, sleep, curveSet=curveSet, timeOffset=timeOffset)

    def BlinkIn(self, obj, startVal = 0.0, endVal = 1.0, duration = 0.1, loops = 3, curveType = uiconst.ANIM_LINEAR, callback = None, sleep = False, timeOffset = 0.0):
        return self.FadeTo(obj, startVal, endVal, duration, loops, curveType, callback, sleep, timeOffset=timeOffset)

    def BlinkOut(self, obj, startVal = 1.0, endVal = 0.0, duration = 0.1, loops = 3, curveType = uiconst.ANIM_LINEAR, callback = None, sleep = False, timeOffset = 0.0):
        return self.FadeTo(obj, startVal, endVal, duration, loops, curveType, callback, sleep, timeOffset=timeOffset)

    def MoveTo(self, obj, startPos = None, endPos = None, duration = 0.5, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, timeOffset = 0.0, curveSet = None):
        if not startPos:
            startPos = (obj.displayX, obj.displayY)
        if not endPos:
            endPos = (obj.displayX, obj.displayY)
        curve = self.GetScalar(startPos[0], endPos[0], duration, curveType, timeOffset=timeOffset)
        curveSet = self.Play(curve, obj, 'left', loops, callback, curveSet=curveSet)
        curve = self.GetScalar(startPos[1], endPos[1], duration, curveType, timeOffset=timeOffset)
        return self.Play(curve, obj, 'top', loops, callback, sleep, curveSet=curveSet)

    def MoveInFromLeft(self, obj, amount = 30, duration = 0.5, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, curveSet = None, timeOffset = 0.0):
        curve = self.GetScalar(obj.left - amount, obj.left, duration, curveType, timeOffset=timeOffset)
        return self.Play(curve, obj, 'left', loops, callback, sleep, curveSet=curveSet)

    def MoveInFromRight(self, obj, amount = 30, duration = 0.5, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, curveSet = None, timeOffset = 0.0):
        curve = self.GetScalar(obj.left + amount, obj.left, duration, curveType, timeOffset=timeOffset)
        return self.Play(curve, obj, 'left', loops, callback, sleep, curveSet=curveSet)

    def MoveInFromTop(self, obj, amount = 30, duration = 0.5, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, timeOffset = 0.0):
        curve = self.GetScalar(obj.top - amount, obj.top, duration, curveType, timeOffset=timeOffset)
        return self.Play(curve, obj, 'top', loops, callback, sleep)

    def MoveInFromBottom(self, obj, amount = 30, duration = 0.5, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, timeOffset = 0.0):
        curve = self.GetScalar(obj.top + amount, obj.top, duration, curveType, timeOffset=timeOffset)
        return self.Play(curve, obj, 'top', loops, callback, sleep)

    def MoveOutLeft(self, obj, amount = 30, duration = 0.5, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, timeOffset = 0.0):
        curve = self.GetScalar(obj.left, obj.left - amount, duration, curveType, timeOffset=timeOffset)
        return self.Play(curve, obj, 'left', loops, callback, sleep)

    def MoveOutRight(self, obj, amount = 30, duration = 0.5, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, timeOffset = 0.0):
        curve = self.GetScalar(obj.left, obj.left + amount, duration, curveType, timeOffset=timeOffset)
        return self.Play(curve, obj, 'left', loops, callback, sleep)

    def MoveOutTop(self, obj, amount = 30, duration = 0.5, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, timeOffset = 0.0):
        curve = self.GetScalar(obj.top, obj.top - amount, duration, curveType, timeOffset=timeOffset)
        return self.Play(curve, obj, 'top', loops, callback, sleep)

    def MoveOutBottom(self, obj, amount = 30, duration = 0.5, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, timeOffset = 0.0):
        curve = self.GetScalar(obj.top, obj.top + amount, duration, curveType, timeOffset=timeOffset)
        return self.Play(curve, obj, 'top', loops, callback, sleep)

    def Tr2DScaleTo(self, obj, startScale = (0.0, 0.0), endScale = (1.0, 1.0), duration = 0.5, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, timeOffset = 0.0, curveSet = None):
        curve = self.GetVector2(startScale, endScale, duration, curveType, timeOffset=timeOffset)
        return self.Play(curve, obj, 'scale', loops, callback, sleep, curveSet=curveSet)

    def Tr2DScaleIn(self, obj, scaleCenter = (0.0, 0.0), duration = 0.5, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, timeOffset = 0.0, curveSet = None):
        return self.Tr2DScaleTo(obj, (0.0, 0.0), (1.0, 1.0), duration, loops, curveType, callback, sleep, timeOffset, curveSet=curveSet)

    def Tr2DScaleOut(self, obj, startScale = (0.0, 0.0), endScale = (1.0, 1.0), duration = 0.5, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, timeOffset = 0.0, curveSet = None):
        return self.Tr2DScaleTo(obj, obj.scale, (0.0, 0.0), duration, loops, curveType, callback, sleep, timeOffset, curveSet=curveSet)

    def Tr2DFlipIn(self, obj, startScale = (0.0, 0.0), endScale = (1.0, 1.0), duration = 0.5, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, timeOffset = 0.0):
        self.Tr2DScaleTo(obj, (1.0, 0.0), (1.0, 1.0), duration, loops, curveType, callback, timeOffset)
        curve = self.GetScalar(0.0, 1.0, duration, curveType, timeOffset=timeOffset)
        return self.Play(curve, obj, 'scalingRotation', loops, callback, sleep)

    def Tr2DFlipOut(self, obj, startScale = (1.0, 1.0), endScale = (0.0, 0.0), duration = 0.5, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, timeOffset = 0.0):
        self.Tr2DScaleTo(obj, startScale, endScale, duration, loops, curveType, callback, timeOffset)
        curve = self.GetScalar(1.0, 0.0, duration, curveType, timeOffset=timeOffset)
        return self.Play(curve, obj, 'scalingRotation', loops, callback, sleep)

    def Tr2DSquashOut(self, obj, duration = 0.5, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, timeOffset = 0.0):
        obj.scalingRotation = 0.5
        obj.scalingCenter = (0.5, 0.5)
        curve = self.GetVector2((1.0, 1.0), (0.0, 1.0), duration, curveType=uiconst.ANIM_SMOOTH, timeOffset=timeOffset)
        return self.Play(curve, obj, 'scale', loops, callback, sleep)

    def Tr2DSquashIn(self, obj, startRotation = (0.0, 1.0), duration = 0.5, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, timeOffset = 0.0):
        obj.scalingRotation = 0.5
        curve = self.GetVector2(startRotation, (1.0, 1.0), duration, curveType, timeOffset=timeOffset)
        return self.Play(curve, obj, 'scale', loops, callback, sleep)

    def Tr2DRotateTo(self, obj, startAngle = 0.0, endAngle = 2 * math.pi, duration = 0.5, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, timeOffset = 0.0, curveSet = None):
        curve = self.GetScalar(startAngle, endAngle, duration, curveType, timeOffset=timeOffset)
        return self.Play(curve, obj, 'rotation', loops, callback, sleep, curveSet=curveSet)

    def SpColorMorphTo(self, obj, startColor = None, endColor = Color.BLUE, duration = 0.5, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, timeOffset = 0.0, attrName = 'color', curveSet = None):
        if startColor is None:
            startColor = obj.GetRGBA()
        excludeAlpha = len(endColor) == 3
        if excludeAlpha:
            startColor = startColor[:3]
            endColor = endColor[:3]
            curve = self.GetColorCurveNoAlpha(startColor, endColor, duration, curveType, timeOffset=timeOffset)
        else:
            curve = self.GetColorCurve(startColor, endColor, duration, curveType, timeOffset=timeOffset)
        return self.Play(curve, obj, attrName, loops, callback, sleep, curveSet=curveSet)

    def SpColorMorphToBlack(self, obj, duration = 0.5, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, timeOffset = 0.0):
        return self.SpColorMorphTo(obj, obj.GetRGBA(), Color.BLACK, duration, loops, curveType, callback, sleep, timeOffset)

    def SpColorMorphToWhite(self, obj, duration = 0.5, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, timeOffset = 0.0):
        return self.SpColorMorphTo(obj, obj.GetRGBA(), Color.WHITE, duration, loops, curveType, callback, sleep, timeOffset)

    def SpGlowFadeTo(self, obj, startColor = (0.8, 0.8, 1.0, 0.3), endColor = (0, 0, 0, 0), glowFactor = 0.8, glowExpand = 3.0, duration = 0.5, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, curveSet = None, timeOffset = 0.0):
        obj.glowFactor = glowFactor
        obj.glowExpand = glowExpand
        curve = self.GetColorCurve(startColor, endColor, duration, curveType, timeOffset=timeOffset)
        return self.Play(curve, obj, 'glowColor', loops, callback, sleep, curveSet=curveSet)

    def SpGlowFadeIn(self, obj, glowColor = (0.8, 0.8, 1.0, 0.3), glowFactor = 0.8, glowExpand = 3.0, duration = 0.5, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, curveSet = None, timeOffset = 0.0):
        return self.SpGlowFadeTo(obj, (0, 0, 0, 0), glowColor, glowFactor, glowExpand, duration, loops, curveType, callback, sleep, curveSet=curveSet, timeOffset=timeOffset)

    def SpGlowFadeOut(self, obj, glowColor = (0.8, 0.8, 1.0, 0.3), glowFactor = 0.8, glowExpand = 3.0, duration = 0.5, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, curveSet = None, timeOffset = 0.0):
        return self.SpGlowFadeTo(obj, glowColor, (0, 0, 0, 0), glowFactor, glowExpand, duration, loops, curveType, callback, sleep, curveSet=curveSet, timeOffset=timeOffset)

    def SpShadowMoveTo(self, obj, startPos = (0.0, 0.0), endPos = (10.0, 10.0), color = None, duration = 0.5, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, timeOffset = 0.0):
        obj.shadowColor = color or (0.0, 0.0, 0.0, 0.5)
        curve = self.GetVector2(startPos, endPos, duration, curveType, timeOffset=timeOffset)
        return self.Play(curve, obj, 'shadowOffset', loops, callback, sleep)

    def SpShadowAppear(self, obj, offset = (10.0, 10.0), color = None, duration = 0.5, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, timeOffset = 0.0):
        color = color or (0.0, 0.0, 0.0, 0.5)
        return self.SpShadowMoveTo(obj, (0.0, 0.0), offset, color, duration, loops, curveType, callback, sleep, timeOffset)

    def SpShadowDisappear(self, obj, duration = 0.5, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, timeOffset = 0.0):
        return self.SpShadowMoveTo(obj, obj.shadowOffset, (0.0, 0.0), None, duration, loops, curveType, callback, sleep, timeOffset)

    def SpSecondaryTextureRotate(self, obj, startVal = 0.0, endVal = 2 * math.pi, duration = 2.0, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, timeOffset = 0.0):
        curve = self.GetScalar(startVal, endVal, duration, curveType, timeOffset=timeOffset)
        return self.Play(curve, obj, 'rotationSecondary', loops, callback, sleep)

    def SpSecondaryTextureScale(self, obj, startVal = (1.0, 1.0), endVal = (0.0, 0.0), duration = 1.0, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, timeOffset = 0.0):
        curve = self.GetVector2(startVal, endVal, duration, curveType, timeOffset=timeOffset)
        return self.Play(curve, obj, 'scaleSecondary', loops, callback, sleep)

    def SpTunnelTo(self, obj, startVal = (1.0, 1.0), endVal = (0.0, 0.0), texturePath = None, duration = 0.5, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, timeOffset = 0.0):
        if not texturePath:
            texturePath = 'res:/UI/Texture/Classes/Animations/radialGradient.png'
        obj.SetSecondaryTexturePath(texturePath)
        obj.spriteEffect = trinity.TR2_SFX_MODULATE
        return self.SpSecondaryTextureScale(obj, startVal, endVal, duration=duration, loops=loops, curveType=curveType, callback=callback, sleep=sleep, timeOffset=timeOffset)

    def SpTunnelIn(self, obj, duration = 1.0, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, timeOffset = 0.0):
        self.SpTunnelTo(obj, (3.0, 3.0), (0.0, 0.0), duration=duration, loops=loops, curveType=curveType, callback=callback, sleep=sleep, timeOffset=timeOffset)

    def SpTunnelOut(self, obj, duration = 1.0, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, timeOffset = 0.0):
        self.SpTunnelTo(obj, (0.0, 0.0), (3.0, 3.0), duration=duration, loops=loops, curveType=curveType, callback=callback, sleep=sleep, timeOffset=timeOffset)

    def SpSecondaryTextureMove(self, obj, startVal = (-1.0, -1.0), endVal = (0, 0), duration = 1.0, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, timeOffset = 0.0):
        curve = self.GetVector2(startVal, endVal, duration, curveType, timeOffset=timeOffset)
        return self.Play(curve, obj, 'translationSecondary', loops, callback, sleep)

    def SpMaskTo(self, obj, startVal = (-1.0, 0.0), endVal = (2.0, 0.0), texturePath = None, rotation = 0.0, duration = 0.5, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, timeOffset = 0.0):
        if not texturePath:
            texturePath = 'res:/UI/Texture/Classes/Animations/maskToGradient.png'
        obj.SetSecondaryTexturePath(texturePath)
        obj.translationSecondary = startVal
        obj.spriteEffect = trinity.TR2_SFX_MODULATE
        obj.rotationSecondary = rotation
        return self.SpSecondaryTextureMove(obj, startVal, endVal, duration=duration, loops=loops, curveType=curveType, callback=callback, sleep=sleep, timeOffset=timeOffset)

    def SpMaskIn(self, obj, rotation = math.pi * 0.75, duration = 0.5, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, timeOffset = 0.0):
        return self.SpMaskTo(obj, startVal=(-1.0, 0.0), endVal=(1.0, 0.0), rotation=rotation, duration=duration, loops=loops, curveType=curveType, callback=callback, sleep=sleep, timeOffset=timeOffset)

    def SpMaskOut(self, obj, rotation = -math.pi * 0.25, duration = 0.5, loops = 1, curveType = uiconst.ANIM_SMOOTH, callback = None, sleep = False, timeOffset = 0.0):
        return self.SpMaskTo(obj, startVal=(1.0, 0.0), endVal=(-1.0, 0.0), rotation=rotation, duration=duration, loops=loops, curveType=curveType, callback=callback, sleep=sleep, timeOffset=timeOffset)

    def SpSwoopBlink(self, obj, startVal = (-1.0, 0.0), endVal = (2.0, 0.0), texturePath = None, rotation = 0.75 * math.pi, duration = 0.5, loops = 1, curveType = uiconst.ANIM_LINEAR, callback = None, sleep = False, timeOffset = 0.0):
        if not texturePath:
            texturePath = 'res:/UI/Texture/Classes/Animations/swoopGradient.png'
        obj.SetSecondaryTexturePath(texturePath)
        obj.spriteEffect = trinity.TR2_SFX_MODULATE
        obj.rotationSecondary = rotation
        return self.SpSecondaryTextureMove(obj, startVal, endVal, duration=duration, loops=loops, curveType=curveType, callback=callback, sleep=sleep, timeOffset=timeOffset)

    def GetScalar(self, startValue, endValue, duration, curveType = uiconst.ANIM_SMOOTH, timeOffset = 0.0):
        if curveType is uiconst.ANIM_RANDOM:
            subCurve = trinity.Tr2CurveScalar()
            v = startValue + (endValue - startValue) / 2
            subCurve.AddKey(0, v, trinity.Tr2CurveInterpolation.LINEAR)
            subCurve.AddKey(25, endValue, trinity.Tr2CurveInterpolation.LINEAR)
            subCurve.AddKey(50, v, trinity.Tr2CurveInterpolation.LINEAR)
            subCurve.SetTimeOffset(timeOffset)
            curve = trinity.Tr2CurveScalarExpression()
            curve.expression = 'input1 + input2 * fractal(input(0), %s, 3.0, 4)' % duration
            curve.input1 = startValue
            curve.input2 = endValue
            curve.inputs.append(subCurve)
            return curve
        curve = trinity.Tr2CurveScalar()
        curve.SetTimeOffset(timeOffset)
        if curveType not in (uiconst.ANIM_LINEAR, uiconst.ANIM_RANDOM) and not isinstance(curveType, (list, tuple)):
            interpolation = trinity.Tr2CurveInterpolation.HERMITE
        else:
            interpolation = trinity.Tr2CurveInterpolation.LINEAR
        if isinstance(curveType, (list, tuple)):
            points = curveType
            for keyTime, keyValue in points:
                key = keyTime * duration
                curve.AddKey(key, keyValue, interpolation, 0, 0, trinity.Tr2CurveTangentType.FREE_SPLIT)

        else:
            curve.AddKey(0, startValue, interpolation, 0, 0, trinity.Tr2CurveTangentType.FREE_SPLIT)
            if curveType in uiconst.ANIM_OVERSHOT_TYPES:
                amount = self.GetOvershotAmount(curveType)
                keyTime = OVERSHOT_TIME * duration
                keyVal = endValue + amount * (endValue - startValue)
                curve.AddKey(keyTime, keyVal, interpolation, 0, 0, trinity.Tr2CurveTangentType.FREE_SPLIT)
            elif curveType is uiconst.ANIM_WAVE:
                curve.AddKey(0.5 * duration, endValue, interpolation, 0, 0, trinity.Tr2CurveTangentType.FREE_SPLIT)
                endValue = startValue
            elif curveType is uiconst.ANIM_BOUNCE:
                curve.AddKey(0.5 * duration, endValue, interpolation, 0, 0, trinity.Tr2CurveTangentType.FREE_SPLIT)
                endValue = startValue
            curve.AddKey(duration, endValue, interpolation, 0, 0, trinity.Tr2CurveTangentType.FREE_SPLIT)
        return curve

    def GetVector2(self, startValue, endValue, duration, curveType = uiconst.ANIM_SMOOTH, timeOffset = 0.0):
        curve = trinity.Tr2CurveVector2()
        curve.x.SetTimeOffset(timeOffset)
        curve.y.SetTimeOffset(timeOffset)
        return self._GetVector(curve, startValue, endValue, duration, curveType)

    def GetVector3(self, startValue, endValue, duration, curveType = uiconst.ANIM_SMOOTH, timeOffset = 0.0):
        curve = trinity.Tr2CurveVector3()
        curve.x.SetTimeOffset(timeOffset)
        curve.y.SetTimeOffset(timeOffset)
        curve.z.SetTimeOffset(timeOffset)
        if isinstance(curveType, (list, tuple)):
            numPoints = float(len(curveType))
            for i, point in enumerate(curveType):
                curve.AddKey(i / numPoints * duration, point)

            return curve
        else:
            return self._GetVector(curve, startValue, endValue, duration, curveType)

    def _GetVector(self, curve, startValue, endValue, duration, curveType = uiconst.ANIM_SMOOTH):
        if curveType is not uiconst.ANIM_LINEAR:
            interpolation = trinity.Tr2CurveInterpolation.HERMITE
        else:
            interpolation = trinity.Tr2CurveInterpolation.LINEAR
        tail = ((0,) * len(startValue), (0,) * len(startValue), trinity.Tr2CurveTangentType.FREE_SPLIT)
        if isinstance(curveType, (list, tuple)):
            points = curveType
            for keyTime, keyValue in points:
                key = keyTime * duration
                curve.AddKey(key, keyValue, interpolation, *tail)

        else:
            curve.AddKey(0, startValue, interpolation, *tail)
            if curveType in uiconst.ANIM_OVERSHOT_TYPES:
                amount = self.GetOvershotAmount(curveType)
                keyTime = OVERSHOT_TIME * duration
                overshotValue = []
                for i, startV in enumerate(startValue):
                    endV = endValue[i]
                    keyVal = endV + amount * (endV - startV)
                    overshotValue.append(keyVal)

                curve.AddKey(keyTime, tuple(overshotValue), interpolation, *tail)
            elif curveType is uiconst.ANIM_WAVE:
                curve.AddKey((0.5 * duration), endValue, interpolation, *tail)
                endValue = startValue
            curve.AddKey(duration, endValue, interpolation, *tail)
        return curve

    def GetOvershotAmount(self, curveType):
        return uiconst.ANIM_OVERSHOT_TYPES.index(curveType) * 0.2 + 0.1

    def GetQuaternion(self, startValue, endValue, duration, curveType = uiconst.ANIM_SMOOTH, timeOffset = 0.0):
        curve = trinity.Tr2CurveQuaternion()
        if isinstance(curveType, (list, tuple)):
            points = curveType
            for keyTime, keyValue in points:
                key = keyTime * duration
                curve.AddKey(key, keyValue)

        else:
            curve.AddKey(0, startValue)
            if curveType in uiconst.ANIM_OVERSHOT_TYPES:
                amount = self.GetOvershotAmount(curveType)
                keyTime = OVERSHOT_TIME * duration
                keyValX = endValue[0] + amount * (endValue[0] - startValue[0])
                keyValY = endValue[1] + amount * (endValue[1] - startValue[1])
                curve.AddKey(keyTime, (keyValX, keyValY))
            elif curveType is uiconst.ANIM_WAVE:
                curve.AddKey(0.5 * duration, endValue)
                endValue = startValue
            curve.AddKey(duration, endValue)
        return curve

    def GetColorCurve(self, startValue, endValue, duration, curveType = uiconst.ANIM_LINEAR, timeOffset = 0.0):
        if len(startValue) == 3:
            startValue = startValue + (1,)
        if len(endValue) == 3:
            endValue = endValue + (1,)
        curve = trinity.Tr2CurveColor()
        curve.r.SetTimeOffset(timeOffset)
        curve.g.SetTimeOffset(timeOffset)
        curve.b.SetTimeOffset(timeOffset)
        curve.a.SetTimeOffset(timeOffset)
        if isinstance(curveType, (list, tuple)):
            points = curveType
            for keyTime, keyValue in points:
                key = keyTime * duration
                curve.AddKey(key, keyValue, trinity.Tr2CurveInterpolation.LINEAR)

            curve.AddKey(duration, (0, 0, 0, 1))
        else:
            curve.AddKey(0, startValue, trinity.Tr2CurveInterpolation.LINEAR)
        if curveType is uiconst.ANIM_WAVE:
            curve.AddKey(0.5 * duration, endValue, trinity.Tr2CurveInterpolation.LINEAR)
            curve.AddKey(duration, startValue, trinity.Tr2CurveInterpolation.LINEAR)
        else:
            curve.AddKey(duration, endValue, trinity.Tr2CurveInterpolation.LINEAR)
        return curve

    def GetColorCurveNoAlpha(self, startValue, endValue, duration, curveType = uiconst.ANIM_LINEAR, timeOffset = 0.0):
        curve = trinity.Tr2CurveVector3()
        curve.x.SetTimeOffset(timeOffset)
        curve.y.SetTimeOffset(timeOffset)
        curve.z.SetTimeOffset(timeOffset)
        if isinstance(curveType, (list, tuple)):
            points = curveType
            for keyTime, keyValue in points:
                key = keyTime * duration
                curve.AddKey(key, keyValue, trinity.Tr2CurveInterpolation.LINEAR)

            curve.AddKey(duration, (0, 0, 0))
        else:
            curve.AddKey(0, startValue, trinity.Tr2CurveInterpolation.LINEAR)
        if curveType is uiconst.ANIM_WAVE:
            curve.AddKey(0.5 * duration, endValue, trinity.Tr2CurveInterpolation.LINEAR)
            curve.AddKey(duration, startValue, trinity.Tr2CurveInterpolation.LINEAR)
        else:
            curve.AddKey(duration, endValue, trinity.Tr2CurveInterpolation.LINEAR)
        return curve


animations = UIAnimations()
