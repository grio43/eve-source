#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\validators\missileValidation.py
from evegraphics.validation.commonUtilities import Validate

@Validate('EveMissile')
def MissileMustHaveWarheads(context, missile):
    if not missile.warheads:
        context.Error(missile, 'missile must have at least one warhead')


@Validate('EveMissile')
def MissileMayNotHaveSpaceObjectAttributes(context, missile):
    if missile.mesh:
        context.Error(missile, 'missile may not have a mesh')
    if missile.attachments:
        context.Error(missile, 'missile may not have attachments')
    if missile.observers:
        context.Error(missile, 'missile may not have observers')
    if missile.impactOverlay:
        context.Error(missile, 'missile may not have an impact overlay')
    if missile.decals:
        context.Error(missile, 'missile may not have decals')
    if missile.customMasks:
        context.Error(missile, 'missile may not have customMasks')
    if missile.effectChildren:
        context.Error(missile, 'missile may not have effectChildren')
    if missile.children:
        context.Error(missile, 'missile may not have children')
    if missile.overlayEffects:
        context.Error(missile, 'missile may not have overlayEffects')
    if missile.lights:
        context.Error(missile, 'missile may not have lights')
    if missile.locators:
        context.Error(missile, 'missile may not have locators')
    if missile.locatorSets:
        context.Error(missile, 'missile may not have locator sets')


@Validate('EveMissileWarhead')
def WarheadEjectVelocityPositive(context, warhead):
    if warhead.startEjectVelocity <= 0:
        context.Error(warhead, 'warhead startEjectVelocity needs to be a positive number')


@Validate('EveMissileWarhead')
def WarheadAccelerationPositive(context, warhead):
    if warhead.acceleration <= 0:
        context.Error(warhead, 'warhead acceleration needs to be a positive number')


@Validate('EveMissileWarhead')
def WarheadMaxExplosionDistancePositive(context, warhead):
    if warhead.maxExplosionDistance < 0:
        context.Error(warhead, 'warhead maxExplosionDistance needs to be a positive number')


@Validate('EveMissileWarhead')
def WarheadImpactSizePositive(context, warhead):
    if warhead.impactSize < 0:
        context.Error(warhead, 'warhead impactSize needs to be a positive number')


@Validate('EveMissileWarhead')
def WarheadImpactDurationPositive(context, warhead):
    if warhead.impactDuration < 0:
        context.Error(warhead, 'warhead impactDuration needs to be a positive number')


@Validate('EveMissileWarhead')
def WarheadSpriteSetLimit(context, warhead):
    if warhead.spriteSet and len(warhead.spriteSet.sprites) > 2:
        context.Error(warhead.spriteSet, 'warhead can contain no more than 2 sprites in a sprite set')


@Validate('EveMissileWarhead')
def WarheadMustHaveAMesh(context, warhead):
    if not warhead.mesh:
        context.Error(warhead, 'warhead needs to have a mesh')


@Validate('EveMissileWarhead')
def WarheadMustNotHaveObsoleteAttributes(context, warhead):
    if warhead.children:
        context.Error(warhead, 'warhead may not contain children')
    if warhead.particleSystems:
        context.Error(warhead, 'warhead may not contain particle systems')
    if warhead.observers:
        context.Error(warhead, 'warhead may not contain observers')
    if warhead.curveSets:
        context.Error(warhead, 'warhead may not contain curve sets')
