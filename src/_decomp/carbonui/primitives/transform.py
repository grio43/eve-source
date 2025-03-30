#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\primitives\transform.py
import math
import blue
import log
import trinity
from carbonui import uiconst
from carbonui.primitives.container import Container

class Transform(Container):
    __guid__ = 'uiprimitives.Transform'
    __renderObject__ = trinity.Tr2Sprite2dTransform
    default_align = uiconst.RELATIVE
    default_state = uiconst.UI_PICKCHILDREN
    default_rotation = 0.0
    default_rotationCenter = (0.5, 0.5)
    default_scale = (1, 1)
    default_scalingCenter = (0, 0)
    default_scalingRotation = 0.0
    isTransformed = True

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.rotation = attributes.get('rotation', self.default_rotation)
        self.rotationCenter = attributes.get('rotationCenter', self.default_rotationCenter)
        self.scale = attributes.get('scale', self.default_scale)
        self.scalingCenter = attributes.get('scalingCenter', self.default_scalingCenter)
        self.scalingRotation = attributes.get('scalingRotation', self.default_scalingRotation)

    def SetRotation(self, rotation = 0):
        self.rotation = rotation

    def GetRotation(self):
        return self.rotation

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        self._scale = value
        ro = self.renderObject
        if ro:
            ro.scale = value

    @property
    def scalingCenter(self):
        return self._scalingCenter

    @scalingCenter.setter
    def scalingCenter(self, value):
        self._scalingCenter = value
        ro = self.renderObject
        if ro:
            ro.scalingCenter = value

    @property
    def scalingRotation(self):
        return self._scalingRotation

    @scalingRotation.setter
    def scalingRotation(self, value):
        self._scalingRotation = value
        ro = self.renderObject
        if ro:
            ro.scalingRotation = value

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        self._rotation = value
        ro = self.renderObject
        if ro:
            ro.rotation = -value

    @property
    def rotationCenter(self):
        return self._rotationCenter

    @rotationCenter.setter
    def rotationCenter(self, value):
        self._rotationCenter = value
        ro = self.renderObject
        if ro:
            ro.rotationCenter = self._rotationCenter

    def StartRotationCycle(self, direction = 1, cycleTime = 1000.0, cycles = None):
        if getattr(self, '_rotateCycle', False):
            self._rotateCycle = False
            blue.pyos.synchro.Yield()
        self._rotateCycle = True
        fullRotation = math.pi * 2
        start = blue.os.GetWallclockTime()
        ndt = 0.0
        current = self.GetRotation()
        while getattr(self, '_rotateCycle', False):
            try:
                ndt = max(ndt, blue.os.TimeDiffInMs(start, blue.os.GetWallclockTime()) / cycleTime)
            except:
                log.LogWarn('StartRotationCycle::Failed getting time diff. Diff should not exceed %s but is %s' % (cycleTime, start - blue.os.GetWallclockTimeNow()))
                ndt = 1.0

            self.SetRotation(current - fullRotation * ndt * direction)
            blue.pyos.synchro.Yield()
            if self.destroyed:
                return
            if cycles is not None and cycles <= int(ndt):
                return

    def Rotate(self, delta):
        newRotation = self.ClampRotation(self.rotation + delta)
        self.rotation = newRotation

    def ClampRotation(self, rotation):
        if rotation > math.pi * 2:
            rotation -= math.pi * 2
        elif rotation < 0:
            rotation += math.pi * 2
        return rotation

    def StopRotationCycle(self):
        self._rotateCycle = False

    def TransformPoint(self, x, y):
        return self.renderObject.TransformPoint(x, y)

    def _GetScale(self):
        return self.scale

    def _GetAbsolutePosition(self, childLeft, childTop):
        parent = self.GetParent()
        left, top = self._GetRelativePosition()
        childLeft, childTop = self.TransformPoint(childLeft, childTop)
        left += childLeft
        top += childTop
        if parent and self.align not in (uiconst.ABSOLUTE, uiconst.NOALIGN):
            left, top = parent._GetAbsolutePosition(left, top)
        return (left, top)
