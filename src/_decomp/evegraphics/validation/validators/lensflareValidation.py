#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\validators\lensflareValidation.py
from evegraphics.validation.commonUtilities import Validate

@Validate('EveLensflare')
def LensflareNeedsAName(context, lensflare):
    if not lensflare.name:
        context.Error(lensflare, 'name is empty')


def _IsEmptyLensflare(lensflare):
    return not lensflare.mesh and not lensflare.occluders and not lensflare.backgroundOccluders


@Validate('EveLensflare')
def LensflareNeedsAMesh(context, lensflare):
    if _IsEmptyLensflare(lensflare):
        return
    if not lensflare.mesh:
        context.Error(lensflare, 'mesh is empty')


@Validate('EveLensflare')
def LensflareNeedsOccluders(context, lensflare):
    if _IsEmptyLensflare(lensflare):
        return
    if not lensflare.occluders:
        context.Error(lensflare, 'lens flare contains no occluders')


@Validate('EveLensflare')
def LensflareNeedsBackgroundOccluders(context, lensflare):
    if _IsEmptyLensflare(lensflare):
        return
    if not lensflare.backgroundOccluders:
        context.Error(lensflare, 'lens flare contains no background occluders')


@Validate('EveLensflare')
def EmptyLensflareHasNoCurves(context, lensflare):
    if not _IsEmptyLensflare(lensflare):
        return
    if lensflare.distanceToCenterCurves:
        context.Error(lensflare.distanceToCenterCurves, 'empty lens flare should contain no curves')
    if lensflare.distanceToEdgeCurves:
        context.Error(lensflare.distanceToEdgeCurves, 'empty lens flare should contain no curves')
    if lensflare.distanceToEdgeCurves:
        context.Error(lensflare.radialAngleCurves, 'empty lens flare should contain no curves')
    if lensflare.xDistanceToCenter:
        context.Error(lensflare.xDistanceToCenter, 'empty lens flare should contain no curves')
    if lensflare.yDistanceToCenter:
        context.Error(lensflare.yDistanceToCenter, 'empty lens flare should contain no curves')
    if lensflare.bindings:
        context.Error(lensflare.bindings, 'empty lens flare should contain no bindings')
    if lensflare.curveSets:
        context.Error(lensflare.curveSets, 'empty lens flare should contain no curve sets')


@Validate('EveLensflare')
def LensflareFlaresIsDeprecated(context, lensflare):
    if lensflare.flares:
        context.Error(lensflare, 'flares list is deprecated')


@Validate('EveLensflare')
def LensflareDisplay(context, lensflare):
    if not lensflare.display and not context.IsBoundAsDestination(lensflare, 'display'):
        context.Error(lensflare, 'display is off - lens flare is invisible')


@Validate('EveLensflare')
def LensflareDoOcclusionQueries(context, lensflare):
    if not lensflare.doOcclusionQueries:
        context.Error(lensflare, 'doOcclusionQueries is off')


@Validate('EveOccluder')
def OccluderDisplay(context, occluder):
    if not occluder.display and not context.IsBoundAsDestination(occluder, 'display'):
        context.Error(occluder, 'display is off - occluder is disabled')


@Validate('EveOccluder')
def OccluderNeedsSprites(context, occluder):
    if not occluder.sprites:
        context.Error(occluder, 'contains no sprites')
