#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\graphs\animations.py
from carbonui.graphs.animations import AnimationType
from carbonui.graphs.animations import AnimationDynamics
from carbonui.graphs.animations import GetAnimationOffsets
from carbonui.graphs.animations import VertexAnimation
from carbonui.uicore import uicore
from carbonui.graphs import axis

def CreateAnimation(uiObject, categoryAxis, valueAxis, orientation, animationType, animationDynamics, duration, vertexPerDataPoint):
    if animationType == AnimationType.FADE:
        return CreateOpacityAnimation(uiObject, categoryAxis, orientation, animationDynamics, duration, vertexPerDataPoint)
    if animationType == AnimationType.GROW:
        return CreateVertexAnimation(uiObject, categoryAxis, valueAxis, orientation, animationDynamics, duration, vertexPerDataPoint)
    raise ValueError('unsupported animation type')


def CreateVertexAnimation(uiObject, categoryAxis, valueAxis, orientation, animationDynamics, duration, vertexPerDataPoint):
    startVertex = 0
    endVertex = int(len(categoryAxis.GetDataPoints())) * vertexPerDataPoint
    axisZero = valueAxis.MapToViewport(0) * uicore.desktop.dpiScaling
    source = (axisZero,) * (endVertex - startVertex)
    index = 0 if orientation == axis.AxisOrientation.HORIZONTAL else 1
    dest = [ uiObject.renderObject.vertices[i].position[index] for i in xrange(startVertex, endVertex) ]
    offsets = GetAnimationOffsets(animationDynamics, endVertex - startVertex, vertexPerDataPoint=vertexPerDataPoint)
    return VertexAnimation('position', duration, offsets, source, dest, uiObject.renderObject, startVertex, index)


def CreateOpacityAnimation(uiObject, categoryAxis, orientation, animationDynamics, duration, vertexPerDataPoint):
    if animationDynamics == AnimationDynamics.SIMULTANEOUS:
        uicore.animations.MorphScalar(uiObject, 'opacity', startVal=0.0, endVal=1.0, duration=duration)
        return None
    startVertex = 0
    endVertex = int(len(categoryAxis.GetDataPoints())) * vertexPerDataPoint
    source = (0,) * (endVertex - startVertex)
    index = 0 if orientation == axis.AxisOrientation.HORIZONTAL else 1
    dest = (1,) * (endVertex - startVertex)
    offsets = GetAnimationOffsets(animationDynamics, endVertex - startVertex, vertexPerDataPoint=vertexPerDataPoint)
    return VertexAnimation('color', duration, offsets, source, dest, uiObject.renderObject, startVertex, index)
