#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\graphs\animations.py
import random
import trinity
import uthread2
from carbonui.graphs import axis
from carbonui.uicore import uicore

class AnimationType(object):
    FADE = 1
    GROW = 2


class AnimationDynamics(object):
    SIMULTANEOUS = 0
    ALONG_AXIS = 1
    OPPOSITE_AXIS = 2
    RANDOM = 3


def CreateAnimation(uiObject, categoryAxis, valueAxis, orientation, animationType, animationDynamics, duration, vertexPerDataPoint):
    if animationType == AnimationType.FADE:
        return CreateOpacityAnimation(uiObject, categoryAxis, orientation, animationDynamics, duration, vertexPerDataPoint)
    if animationType == AnimationType.GROW:
        return CreateVertexAnimation(uiObject, categoryAxis, valueAxis, orientation, animationDynamics, duration, vertexPerDataPoint)
    raise ValueError('unsupported animation type')


def CreateVertexAnimation(uiObject, categoryAxis, valueAxis, orientation, animationDynamics, duration, vertexPerDataPoint):
    startVertex = max(0, int(categoryAxis.GetVisibleRange()[0] - 1)) * vertexPerDataPoint
    endVertex = int(min(categoryAxis.GetVisibleRange()[1] + 1, len(categoryAxis.GetDataPoints()))) * vertexPerDataPoint
    if startVertex >= endVertex:
        return None
    axisZero = valueAxis.GetViewportRange()[0]
    source = (axisZero,) * (endVertex - startVertex)
    index = 0 if orientation == axis.AxisOrientation.HORIZONTAL else 1
    dest = [ uiObject.renderObject.vertices[i].position[index] for i in xrange(startVertex, endVertex) ]
    offsets = GetAnimationOffsets(animationDynamics, endVertex - startVertex, vertexPerDataPoint=vertexPerDataPoint)
    return VertexAnimation('position', duration, offsets, source, dest, uiObject.renderObject, startVertex, index)


def CreateOpacityAnimation(uiObject, categoryAxis, orientation, animationDynamics, duration, vertexPerDataPoint):
    if animationDynamics == AnimationDynamics.SIMULTANEOUS:
        uicore.animations.MorphScalar(uiObject, 'opacity', startVal=0.0, endVal=1.0, duration=duration)
        return None
    startVertex = max(0, int(categoryAxis.GetVisibleRange()[0] - 1)) * vertexPerDataPoint
    endVertex = int(min(categoryAxis.GetVisibleRange()[1] + 1, len(categoryAxis.GetDataPoints()))) * vertexPerDataPoint
    if startVertex >= endVertex:
        return None
    source = (0,) * (endVertex - startVertex)
    index = 0 if orientation == axis.AxisOrientation.HORIZONTAL else 1
    dest = (1,) * (endVertex - startVertex)
    offsets = GetAnimationOffsets(animationDynamics, endVertex - startVertex, vertexPerDataPoint=vertexPerDataPoint)
    return VertexAnimation('color', duration, offsets, source, dest, uiObject.renderObject, startVertex, index)


class VertexAnimation(object):

    def __init__(self, attribute, duration, timeOffsets, source, destination, polygon, vertexOffset, vertexAttribute):
        self._attibute = attribute
        self._source = source
        self._timeOffsets = timeOffsets
        self._destination = destination
        self._polygon = polygon
        self._offset = vertexOffset
        self._startTime = trinity.device.animationTime
        self._endTime = self._startTime + max(self._timeOffsets) + duration
        self._duration = duration
        self._vertexAttribute = vertexAttribute
        self._cancelled = False
        uthread2.StartTasklet(self._Thread)

    def Cancel(self, applyLastFrame = True):
        self._cancelled = True
        if applyLastFrame:
            self._Apply((self._endTime - self._startTime) / self._duration)

    def _Apply(self, time):
        if self._attibute == 'position':
            self._ApplyPositions(time)
        else:
            self._ApplyColors(time)

    def _ApplyPositions(self, time):
        vertices = self._polygon.vertices
        for i, (offset, source, dest) in enumerate(zip(self._timeOffsets, self._source, self._destination)):
            t = time - offset
            t = min(max(t, 0), 1)
            t = t ** 0.3
            v = source * (1 - t) + dest * t
            vtx = vertices[i + self._offset]
            if self._vertexAttribute == 0:
                vtx.position = (v, vtx.position[1])
            else:
                vtx.position = (vtx.position[0], v)

        self._polygon.SetDirty()

    def _ApplyColors(self, time):
        vertices = self._polygon.vertices
        for i, (offset, source, dest) in enumerate(zip(self._timeOffsets, self._source, self._destination)):
            t = time - offset
            t = min(max(t, 0), 1)
            t = t ** 0.3
            v = source * (1 - t) + dest * t
            vtx = vertices[i + self._offset]
            vtx.color = (vtx.color[0],
             vtx.color[1],
             vtx.color[2],
             v)

        self._polygon.SetDirty()

    def _Thread(self):
        while not self._cancelled:
            now = trinity.device.animationTime
            self._Apply((now - self._startTime) / self._duration)
            if now > self._endTime:
                break
            uthread2.Yield()


def GetAnimationOffsets(animationDynamics, vertexCount, vertexPerDataPoint = 1):
    if animationDynamics == AnimationDynamics.SIMULTANEOUS:
        offsets = (0,) * vertexCount
    elif animationDynamics == AnimationDynamics.ALONG_AXIS:
        relRange = vertexPerDataPoint / float(vertexCount)
        offsets = [ x / vertexPerDataPoint * relRange for x in xrange(vertexCount) ]
    elif animationDynamics == AnimationDynamics.OPPOSITE_AXIS:
        relRange = vertexPerDataPoint / float(vertexCount)
        offsets = [ 1 - x / vertexPerDataPoint * relRange for x in xrange(vertexCount) ]
    elif animationDynamics == AnimationDynamics.RANDOM:
        if vertexPerDataPoint == 1:
            offsets = [ random.random() for _ in xrange(vertexCount) ]
        else:
            offsets = []
            for each in xrange(vertexCount):
                offsets.extend((random.random(),) * vertexPerDataPoint)

    else:
        raise ValueError('unsupported animation dynamics')
    return offsets
