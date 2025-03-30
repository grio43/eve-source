#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\validators\gpuEmitterValidation.py
import blue
from evegraphics.validation.commonUtilities import Validate

@Validate('Tr2GpuUniqueEmitter')
@Validate('Tr2GpuSharedEmitter')
def RateNonZero(context, emitter):
    if not context.IsBoundAsDestination(emitter, 'rate') and emitter.rate <= 0 and not context.IsBoundAsDestination(emitter, 'emissionDensity') and emitter.emissionDensity <= 0:
        context.Error(emitter, 'rate is zero - emitter never emits')


@Validate('Tr2GpuUniqueEmitter')
@Validate('Tr2GpuSharedEmitter')
def AngleNonNegative(context, emitter):
    if emitter.angle < 0:
        context.Error(emitter, 'angle is negative, it should be zero or greater than zero')


@Validate('Tr2GpuUniqueEmitter')
@Validate('Tr2GpuSharedEmitter')
def InnerAngleNonNegative(context, emitter):
    if emitter.innerAngle < 0:
        context.Error(emitter, 'innerAngle is negative, it should be zero or greater than zero')


@Validate('Tr2GpuUniqueEmitter')
@Validate('Tr2GpuSharedEmitter')
def RadiusNonNegative(context, emitter):
    if emitter.radius < 0:
        context.Error(emitter, 'radius is negative, it should be zero or greater than zero')


def _SwapLifeTimes(emitter):

    def inner():
        tmp = emitter.minLifeTime
        emitter.minLifeTime = emitter.maxLifeTime
        emitter.maxLifeTime = tmp
        return True

    return ('Swap minLifeTime and maxLifeTime', inner, True)


@Validate('Tr2GpuUniqueEmitter')
@Validate('Tr2GpuSharedEmitter')
def LifeTimeInBounds(context, emitter):
    if emitter.minLifeTime < 0:
        context.Error(emitter, 'minLifeTime is negative, it should be zero or greater than zero')
    if emitter.maxLifeTime < 0:
        context.Error(emitter, 'maxLifeTime is negative, it should be zero or greater than zero')
    if emitter.minLifeTime > emitter.maxLifeTime:
        context.Error(emitter, 'minLifeTime is greater than maxLifeTime', actions=(_SwapLifeTimes(emitter),))


@Validate('Tr2GpuUniqueEmitter')
@Validate('Tr2GpuSharedEmitter')
def SizesInBounds(context, emitter):
    if any((x < 0 for x in emitter.sizes)):
        context.Error(emitter, 'one of the particle sizes is less than zero')
    if all((x == 0 for x in emitter.sizes)) and emitter.sizeVariance == 0:
        context.Error(emitter, 'particle sizes are all zero')


@Validate('Tr2GpuUniqueEmitter')
@Validate('Tr2GpuSharedEmitter')
def TextureIndexIsValid(context, emitter):
    ps = blue.resMan.LoadObject('res:/fisfx/gpuparticles/system.red')
    if ps and ps.render:
        size = ps.render.parameters.FindByName('AtlasMapSize')
        if size:
            count = int(size.value[1])
            if emitter.textureIndex >= count:
                context.Error(emitter, 'invalid texture index')
