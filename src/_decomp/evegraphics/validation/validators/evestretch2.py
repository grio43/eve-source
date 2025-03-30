#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\validators\evestretch2.py
import blue
import trinity
from evegraphics.validation.commonUtilities import Validate
from evegraphics.validation.validationFunctions import ListIsNotEmpty, ListAttributesAreDistinct

@Validate('EveStretch2')
def EveStretch2NeedsEffect(context, stretch):
    if not stretch.effect:
        context.Error(stretch, 'has no effect')


@Validate('EveStretch2')
def EveStretch2HasQuads(context, stretch):
    if stretch.quadCount <= 0:
        context.Error(stretch, 'has no quads')


@Validate('EveStretch2')
def EveStretch2HasACurveSet(context, stretch):
    if not stretch.start and not stretch.loop and not stretch.end:
        context.Error(stretch, 'has no curve sets')


def _HasBinding(bindingLists, source):
    for bindings in bindingLists:
        for binding in bindings:
            if binding.sourceObject == source:
                return True

    return False


@Validate('EveTurretFiringFX(firingEffect)/*/EveStretch2(stretch)/Tr2Effect(effect)')
def EveStretch2EffectColorIsBoundToAmmo(context, firingEffect, stretch, effect):
    if not any((x.name == 'Ammo' for x in blue.FindInterface(stretch, 'Tr2CurveConstant'))):
        return
    for param in effect.parameters:
        if param.name == 'Color':
            bound = False
            for bindings in context.GetDestinationBindings().get(param, {}).values():
                for binding in bindings:
                    if not binding.IsDestination():
                        continue
                    boundObject = binding.GetSourceObject()
                    if isinstance(boundObject, trinity.Tr2CurveConstant) and boundObject.name == 'Ammo':
                        bound = True

            if not bound:
                context.Error(param, 'Color parameter is not bound to Ammo curve')


@Validate('EveTurretFiringFX(firingEffect)/*/EveStretch2(stretch)/Tr2PointLight(light)')
def EveStretch2LightColorIsBoundToAmmo(context, firingEffect, stretch, light):
    if not any((x.name == 'Ammo' for x in blue.FindInterface(stretch, 'Tr2CurveConstant'))):
        return
    bound = False
    for bindings in context.GetDestinationBindings().get(light, {}).values():
        for binding in bindings:
            if not binding.IsDestination():
                continue
            boundObject = binding.GetSourceObject()
            if isinstance(boundObject, trinity.Tr2CurveConstant) and boundObject.name == 'Ammo':
                bound = True

    if not bound:
        context.Error(light, 'is not bound to Ammo curve')
