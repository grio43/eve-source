#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\validators\particleSystemValidation.py
import blue
import trinity
from trinity import effects, particlesystemelements
from evegraphics.validation.commonUtilities import Validate, DeleteAction
from effectValidation import effectCache

@Validate('Tr2DynamicEmitter')
def RateIsValid(context, emitter):
    if not context.IsBoundAsDestination(emitter, 'rate') and emitter.rate <= 0:
        context.Error(emitter, 'rate needs to be positive')


@Validate('Tr2DynamicEmitter')
def MaxParticlesIsValid(context, emitter):
    if not context.IsBoundAsDestination(emitter, 'maxParticles') and emitter.maxParticles == 0:
        context.Error(emitter, 'maxParticles is zero - emitter will not emit')


@Validate('Tr2DynamicEmitter')
def HasParticleSystem(context, emitter):
    if not emitter.particleSystem:
        context.Error(emitter, 'emitter is not attached to a particle system')


@Validate('Tr2DynamicEmitter')
def DynamicEmitterIsValid(context, emitter):
    if not emitter.isValid:
        context.Error(emitter, 'emitter reports as being invalid')


@Validate('EveChildParticleSphere')
def ParticleSphereIsValid(context, sphere):
    if not sphere.isValid:
        context.Error(sphere, 'particle sphere reports as being invalid')


@Validate('Tr2DynamicEmitter')
def ConstantParticleSystemBoundToDynamicEmitter(context, emitter):
    if emitter.particleSystem:
        if not emitter.particleSystem.updateSimulation:
            context.Error(emitter, 'dynamic emitter emits into a constant particle system (particle system updateSimulation flag is off)')


@Validate('Tr2ParticleSystem')
def ParticleSystemIsValid(context, particleSystem):
    if not particleSystem.isValid:
        context.Error(particleSystem, 'particle system reports as being invalid')


@Validate('Tr2ParticleSystem')
def ConstantParticleSystemBoundToDynamicEmitter(context, particleSystem):
    if particleSystem.forces and not particleSystem.applyForce:
        context.Error(particleSystem, 'particle system has forces yet applyForce flag is off')


@Validate('/*')
def ParticleSystemsUsed(context, root):
    systems = set(blue.FindInterface(root, 'Tr2ParticleSystem'))
    for each in list(systems):
        if each.emitParticleOnDeathEmitter:
            try:
                systems.remove(each)
            except KeyError:
                pass

        if each.emitParticleDuringLifeEmitter:
            try:
                systems.remove(each)
            except KeyError:
                pass

    for each in blue.FindInterface(root, 'Tr2InstancedMesh'):
        if each.instanceGeometryResource in systems:
            systems.remove(each.instanceGeometryResource)

    for each in systems:
        context.Error(each, 'system is not used', actions=[DeleteAction(context.GetStack()[0], each, True)])


@Validate('/*')
def ParticleSystemsHaveEmitters(context, root):
    systems = set(blue.FindInterface(root, 'Tr2ParticleSystem'))
    emitters = blue.FindInterface(root, 'Tr2DynamicEmitter') + blue.FindInterface(root, 'Tr2StaticEmitter') + blue.FindInterface(root, 'EveChildParticleSphere')
    for each in list(systems):
        if each.emitParticleOnDeathEmitter in systems:
            systems.remove(each.emitParticleOnDeathEmitter)
        if each.emitParticleDuringLifeEmitter in systems:
            systems.remove(each.emitParticleDuringLifeEmitter)

    for each in emitters:
        if each.particleSystem in systems:
            systems.remove(each.particleSystem)

    for each in systems:
        context.Error(each, 'there are no emitters emitting into this particle system', actions=[DeleteAction(context.GetStack()[0], each, True)])


def _UnsetUsedByGpu(element, particleSystem, root, default):

    def inner():
        element.usedByGPU = False
        particleSystem.UpdateElementDeclaration()
        emitters = blue.FindInterface(root, 'Tr2DynamicEmitter')
        for each in emitters:
            if each.particleSystem == particleSystem:
                each.Rebind()

        for each in blue.FindInterface(root, 'Tr2InstancedMesh'):
            if each.instanceGeometryResource == particleSystem:
                each.instanceGeometryResource = None
                each.instanceGeometryResource = particleSystem

        return True

    return ('Unset usedByGPU flag', inner, default)


def _DeleteElement(element, particleSystem, root, default):

    def inner():
        particleSystem.elements.remove(element)
        particleSystem.UpdateElementDeclaration()
        particleSystem.RebindConstraints()
        emitters = blue.FindInterface(root, 'Tr2DynamicEmitter') + blue.FindInterface(root, 'EveChildParticleSphere')
        for each in emitters:
            if each.particleSystem == particleSystem:
                for generator in each.generators:
                    if isinstance(generator, trinity.Tr2SphereShapeAttributeGenerator):
                        if element.elementType == trinity.PARTICLE_ELEMENT_TYPE.POSITION:
                            generator.controlPosition = False
                            break
                        elif element.elementType == trinity.PARTICLE_ELEMENT_TYPE.VELOCITY:
                            generator.controlVelocity = False
                            break
                    elif generator.elementType == element.elementType:
                        if element.elementType != trinity.PARTICLE_ELEMENT_TYPE.CUSTOM or generator.customName == element.customName:
                            each.generators.remove(generator)
                            break

                if hasattr(each, 'Rebind'):
                    each.Rebind()
                else:
                    each.Refresh()

        for each in blue.FindInterface(root, 'Tr2InstancedMesh'):
            if each.instanceGeometryResource == particleSystem:
                each.instanceGeometryResource = None
                each.instanceGeometryResource = particleSystem

        return True

    return ('Delete element', inner, default)


def _CheckShaderInputs(context, inputs, particleSystem, elementNames):
    psToVs = {trinity.PARTICLE_ELEMENT_TYPE.LIFETIME: 3,
     trinity.PARTICLE_ELEMENT_TYPE.POSITION: 0,
     trinity.PARTICLE_ELEMENT_TYPE.VELOCITY: 2,
     trinity.PARTICLE_ELEMENT_TYPE.MASS: 4,
     trinity.PARTICLE_ELEMENT_TYPE.CUSTOM: 5}
    vsToPs = {v:k for k, v in psToVs.items()}
    for each in particleSystem.elements:
        usage = psToVs[each.elementType]
        usageIndex = 8 if each.elementType == 1 else each.usageIndex + 8
        if (usage, usageIndex) in inputs:
            inputs.remove((usage, usageIndex))
        elif each.usedByGPU:
            isCustom = each.elementType == trinity.PARTICLE_ELEMENT_TYPE.CUSTOM
            actions = [_UnsetUsedByGpu(each, particleSystem, context.GetStack()[0], not isCustom)]
            if each.elementType not in [trinity.PARTICLE_ELEMENT_TYPE.POSITION, trinity.PARTICLE_ELEMENT_TYPE.VELOCITY, trinity.PARTICLE_ELEMENT_TYPE.LIFETIME]:
                actions.append(_DeleteElement(each, particleSystem, context.GetStack()[0], isCustom))
            context.Error(each, 'element has usedByGPU set, but the shader does not use it', actions=actions)

    for usage, usageIndex in inputs:
        if usageIndex < 8:
            continue
        if usage in vsToPs:
            try:
                name = elementNames[vsToPs[usage], usageIndex - 8]
            except KeyError:
                name = trinity.PARTICLE_ELEMENT_TYPE.GetNameFromValue(vsToPs[usage])
                if vsToPs[usage] == trinity.PARTICLE_ELEMENT_TYPE.CUSTOM:
                    name += '/%s' % (usageIndex - 8)

        else:
            name = '(%s, %s)' % (usage, usageIndex - 8)
        context.Error(particleSystem, 'the shader expects an %s element that is not present in the particle system' % name)


@Validate('/*')
def CheckShaderInputs(context, root):
    ps = {}
    elementNames = {}
    for mesh in blue.FindInterface(root, 'Tr2InstancedMesh'):
        if isinstance(mesh.instanceGeometryResource, trinity.Tr2ParticleSystem):
            areas = []
            if mesh.opaqueAreas:
                areas.extend(mesh.opaqueAreas)
            if mesh.decalAreas:
                areas.extend(mesh.decalAreas)
            if mesh.depthAreas:
                areas.extend(mesh.depthAreas)
            if mesh.transparentAreas:
                areas.extend(mesh.transparentAreas)
            if mesh.additiveAreas:
                areas.extend(mesh.additiveAreas)
            if mesh.pickableAreas:
                areas.extend(mesh.pickableAreas)
            if mesh.mirrorAreas:
                areas.extend(mesh.mirrorAreas)
            if mesh.decalNormalAreas:
                areas.extend(mesh.decalNormalAreas)
            if mesh.depthNormalAreas:
                areas.extend(mesh.depthNormalAreas)
            if mesh.opaquePrepassAreas:
                areas.extend(mesh.opaquePrepassAreas)
            if mesh.decalPrepassAreas:
                areas.extend(mesh.decalPrepassAreas)
            if mesh.geometryEraserAreas:
                areas.extend(mesh.geometryEraserAreas)
            if mesh.distortionAreas:
                areas.extend(mesh.distortionAreas)
            inputs = set()
            for each in areas:
                if each.effect:
                    inputs.update(effects.GetVertexShaderInputs(each.effect, effectCache))
                    for k, v in particlesystemelements.GetParticleElementAnnotations(each.effect, effectCache).items():
                        if v.name:
                            elementNames[k] = v.name

            ps.setdefault(mesh.instanceGeometryResource, set()).update(inputs)

    for k, v in ps.items():
        _CheckShaderInputs(context, v, k, elementNames)


@Validate('Tr2InstancedMesh')
def NoCopyPasteBounds(context, mesh):
    if mesh.boundsMethod != trinity.Tr2InstanceMeshBoundsMethod.STATIC:
        return
    if mesh.minBounds == (-10000000000.0, -10000000000.0, -10000000000.0) or mesh.maxBounds == (10000000000.0, 10000000000.0, 10000000000.0):
        context.Error(mesh, 'invalid mesh bounds (copy-paste error?)')
