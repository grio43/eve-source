#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\lib\TextureCompositor\TextureCompositor.py
from contextlib import contextmanager
import trinity
import blue
import log
RUN_RENDER_JOB, RETURN_RENDER_JOB = range(2)
DIFFUSE_MAP, SPECULAR_MAP, NORMAL_MAP, MASK_MAP = range(4)
MAPS = (DIFFUSE_MAP,
 SPECULAR_MAP,
 NORMAL_MAP,
 MASK_MAP)
MAPNAMES = ('DiffuseMap', 'SpecularMap', 'NormalMap', 'CutMaskMap')
EFFECT_LOCATION = 'res:/Graphics/Effect/Utility/Compositing'
COMPOSITE_SHADER_PATHS = ['AlphaFill.fx',
 'BlitIntoAlpha1.fx',
 'BlitIntoAlpha2.fx',
 'BlitIntoAlphaWithZones.fx',
 'BlitUVOffset.fx',
 'ColorCopyblit.fx',
 'ColorCopyblitToGamma.fx',
 'ColorFill.fx',
 'ColorizedBlit.fx',
 'ColorizedBlit_AlphaTest.fx',
 'ColorizedCopyBlit.fx',
 'Copyblit.fx',
 'ExpandOpaque.fx',
 'ExpandOpaqueNoMask.fx',
 'MaskedNormalBlit.fx',
 'PatternBlit.fx',
 'SimpleBlit.fx',
 'SphericalCircleBlit.fx',
 'TwistNormalBlit.fx']
COMPRESS_DXT1 = trinity.TR2DXT_COMPRESS_SQUISH_DXT1
COMPRESS_DXT5 = trinity.TR2DXT_COMPRESS_SQUISH_DXT5
COMPRESS_DXT5n = trinity.TR2DXT_COMPRESS_RT_DXT5N

class TextureLoadingError(Exception):
    pass


def _GetEffectsToCache():
    effects = []
    for each in COMPOSITE_SHADER_PATHS:
        effect = trinity.Tr2Effect()
        effect.effectFilePath = EFFECT_LOCATION + '/' + each
        effects.append(effect)

    return effects


def _CreateParameter(paramType, paramName, paramValue):
    param = paramType
    param.name = paramName
    if isinstance(paramValue, list):
        paramValue = tuple(paramValue)
    param.value = paramValue
    return param


def _AppendParameter(effect, paramName, paramValue):
    try:
        value = tuple(paramValue)
    except TypeError:
        value = (paramValue,)

    value += (0.0,) * (4 - len(value))
    effect.constParameters.append((paramName, value))


@contextmanager
def _UpdateEffect(effect):
    effect.StartUpdate()
    try:
        yield
    finally:
        effect.EndUpdate()


class TextureCompositor(object):
    cachedEffects = None

    def __init__(self, renderTarget = None, resData = None, targetWidth = 0):
        self.renderJob = None
        self.renderTarget = renderTarget
        self.targetWidth = targetWidth
        self.resData = resData
        self._texturesWithCutouts = []
        self._texturesByResourceID = {}
        self._resourcesToLoad = []
        if not TextureCompositor.cachedEffects:
            TextureCompositor.cachedEffects = _GetEffectsToCache()

    def _CreateResource(self, effect, paramName, resPath, cutoutName = None, mapType = ''):
        if not resPath:
            raise Exception('Invalid resource passed to texture compositor!')
        elif isinstance(resPath, basestring):
            resPath = str(resPath)
            if self.targetWidth > 0 and self.resData:
                resDataEntry = self.resData.GetEntryByFullResPath(resPath)
                if resDataEntry:
                    resPath = resDataEntry.GetMapResolutonMatch(resPath, self.targetWidth)
            paramRes = blue.resMan.GetResource(resPath)
        elif isinstance(resPath, trinity.TriTextureRes):
            paramRes = resPath
        elif hasattr(resPath, 'resource'):
            paramRes = resPath.resource
        else:
            raise Exception('Invalid resource passed to texture compositor!')
        if paramRes is None:
            raise Exception('Invalid resource passed to texture compositor!')
        param = trinity.TriTextureParameter()
        param.name = paramName
        param.SetResource(paramRes)
        item = (paramRes,
         effect,
         cutoutName,
         mapType)
        if cutoutName:
            self._texturesWithCutouts.append(item)
        self._texturesByResourceID[id(paramRes)] = item
        if paramRes not in self._resourcesToLoad:
            self._resourcesToLoad.append(paramRes)
        return param

    def _AppendResource(self, effect, paramName, resPath, cutoutName = None, mapType = ''):
        effect.resources.append(self._CreateResource(effect, paramName, resPath, cutoutName, mapType))

    def _MakeEffect(self, effectName):
        effect = trinity.Tr2Effect()
        effect.effectFilePath = '{0}/{1}.fx'.format(EFFECT_LOCATION, effectName)
        self._resourcesToLoad.append(effect.effectResource)
        return effect

    def Start(self, clear = True):
        self.renderJob = trinity.CreateRenderJob('Texture Compositing')
        self.renderJob.PushRenderTarget(self.renderTarget)
        self.renderJob.PushDepthStencil(None)
        if clear:
            cl = self.renderJob.Clear((0.0, 1.0, 0.0, 0.0), 1.0)
            cl.isDepthCleared = False
        self.renderJob.SetStdRndStates(trinity.RM_FULLSCREEN)

    def _WaitForLoads(self):
        while any((not x.isPrepared for x in self._resourcesToLoad)):
            blue.synchro.Yield()

        not_good = [ not x.isGood for x in self._resourcesToLoad ]
        if any(not_good):
            for idx, state in enumerate(not_good):
                if state:
                    x = self._resourcesToLoad[idx]
                    errpath = '(Effect Resource)'
                    if hasattr(x, 'path'):
                        errpath = x.path
                    log.LogError('TextureCompositor:: Texture load failed %s' % errpath)
                    raise TextureLoadingError('TextureCompositor:: Texture load failed %s' % errpath)

    def _AddCutoutParameters(self):
        lastFx = None
        for resource, effect, name, _ in self._texturesWithCutouts:
            cutout = (resource.cutoutX,
             resource.cutoutY,
             resource.cutoutWidth,
             resource.cutoutHeight)
            if lastFx != effect:
                if lastFx:
                    lastFx.EndUpdate()
                lastFx = effect
                lastFx.StartUpdate()
            _AppendParameter(lastFx, name, cutout)

        if lastFx:
            lastFx.EndUpdate()

    def _AddTextureTypeParameters(self):
        for step in self.renderJob.steps:
            if isinstance(step, trinity.TriStepRenderEffect):
                step.effect.StartUpdate()
                for res in step.effect.resources:
                    mapFormat = res.resource.format
                    if mapFormat == trinity.PIXEL_FORMAT.R8_UNORM:
                        _AppendParameter(step.effect, res.name.lower() + '_L8', 1.0)
                    elif mapFormat == trinity.PIXEL_FORMAT.R8G8_UNORM:
                        _AppendParameter(step.effect, res.name.lower() + '_L8A8', 1.0)
                    r = self._texturesByResourceID.get(id(res.resource))
                    if r:
                        mapName = r[3]
                        if mapName == 'N' and mapFormat == trinity.PIXEL_FORMAT.R8G8_UNORM:
                            _AppendParameter(step.effect, res.name.lower() + '_blitAsNormal', 1.0)

                step.effect.EndUpdate()

    def Finalize(self, textureToCopyTo = None, compressionSettings = None, mapType = None):
        self._WaitForLoads()
        doCompression = compressionSettings and compressionSettings.compressTextures and compressionSettings.AllowCompress(mapType)
        if doCompression:
            textureToCopyTo = None
        self._AddCutoutParameters()
        self._AddTextureTypeParameters()
        self.renderJob.PopDepthStencil()
        self.renderJob.PopRenderTarget()
        self.renderJob.GenerateMipMaps(self.renderTarget)
        if textureToCopyTo is not None:
            self.renderJob.CopyRenderTarget(textureToCopyTo, self.renderTarget)
        self.renderJob.ScheduleChained()
        try:
            self.renderJob.WaitForFinish()
        except Exception:
            self.renderJob.CancelChained()
            raise

        self._texturesWithCutouts = []
        self._texturesByResourceID.clear()
        if self.renderJob.status != trinity.RJ_DONE:
            return
        if not doCompression:
            if textureToCopyTo is not None:
                while not textureToCopyTo.isPrepared:
                    blue.synchro.Yield()

                if not textureToCopyTo.isGood:
                    log.LogError('TextureCompositor:: Texture %s failed to load properly' % textureToCopyTo.name)
                    raise TextureLoadingError('TextureCompositor:: Texture %s failed to load properly' % textureToCopyTo.name)
                return textureToCopyTo
            tex = trinity.TriTextureRes()
            tex.CreateAndCopyFromRenderTarget(self.renderTarget)
            while not tex.isPrepared:
                blue.synchro.Yield()

            if not tex.isGood:
                log.LogError('TextureCompositor:: Texture %s failed to load properly' % tex.name)
                raise TextureLoadingError('TextureCompositor:: Texture %s failed to load properly' % tex.name)
            return tex
        hostBitmap = trinity.Tr2HostBitmap(self.renderTarget)
        tex = trinity.TriTextureRes()
        compressionFormat = COMPRESS_DXT5n if mapType is NORMAL_MAP else COMPRESS_DXT5
        hostBitmap.Compress(compressionFormat, compressionSettings.qualityLevel, tex)
        while not tex.isPrepared:
            blue.synchro.Yield()

        if not tex.isGood:
            log.LogError('TextureCompositor:: Texture %s failed to load properly' % tex.name)
            raise TextureLoadingError('TextureCompositor:: Texture %s failed to load properly' % tex.name)
        return tex

    def _CompositeTexture(self, effect, subrect = None):
        vp = trinity.TriViewport()
        if subrect:
            vp.x = subrect[0]
            vp.y = subrect[1]
            vp.width = subrect[2] - subrect[0]
            vp.height = subrect[3] - subrect[1]
        else:
            vp.x = 0
            vp.y = 0
            vp.width = self.renderTarget.width
            vp.height = self.renderTarget.height
        self.renderJob.SetViewport(vp)
        self.renderJob.RenderEffect(effect)

    def CopyBlitTexture(self, path, subrect = None, srcRect = None, isNormalMap = False, alphaMultiplier = 1.0):
        effect = self._MakeEffect('Copyblit')
        with _UpdateEffect(effect):
            self._AppendResource(effect, 'Texture', path, 'TextureReverseUV', mapType='N' if isNormalMap else '')
            if srcRect:
                _AppendParameter(effect, 'SourceUVs', srcRect)
            _AppendParameter(effect, 'AlphaMultiplier', alphaMultiplier)
        self.renderJob.SetRenderState(trinity.D3DRS_BLENDOPALPHA, trinity.TRIBLENDOP_ADD)
        self._CompositeTexture(effect, subrect)

    def MaskedNormalBlitTexture(self, path, strength, subrect = None, srcRect = None):
        effect = self._MakeEffect('MaskedNormalBlit')
        with _UpdateEffect(effect):
            self._AppendResource(effect, 'Texture', path, 'TextureReverseUV')
            _AppendParameter(effect, 'Strength', strength)
            if srcRect:
                _AppendParameter(effect, 'SourceUVs', srcRect)
        self.renderJob.SetRenderState(trinity.D3DRS_BLENDOPALPHA, trinity.TRIBLENDOP_ADD)
        self._CompositeTexture(effect, subrect)

    def TwistNormalBlitTexture(self, path, strength, subrect = None, srcRect = None):
        effect = self._MakeEffect('TwistNormalBlit')
        with _UpdateEffect(effect):
            self._AppendResource(effect, 'Texture', path, 'TextureReverseUV')
            _AppendParameter(effect, 'Strength', strength)
            if srcRect:
                _AppendParameter(effect, 'SourceUVs', srcRect)
        self.renderJob.SetRenderState(trinity.D3DRS_BLENDOPALPHA, trinity.TRIBLENDOP_ADD)
        self._CompositeTexture(effect, subrect)

    def SubtractAlphaFromAlpha(self, path, subrect = None, srcRect = None):
        effect = self._MakeEffect('BlitIntoAlpha1')
        with _UpdateEffect(effect):
            self._AppendResource(effect, 'Texture', path, 'TextureReverseUV')
            if srcRect:
                _AppendParameter(effect, 'SourceUVs', srcRect)
        self.renderJob.SetRenderState(trinity.D3DRS_BLENDOPALPHA, trinity.TRIBLENDOP_REVSUBTRACT)
        self._CompositeTexture(effect, subrect)

    def BlitTextureIntoAlphaWithMask(self, path, mask, subrect = None, srcRect = None):
        effect = self._MakeEffect('BlitIntoAlpha1')
        with _UpdateEffect(effect):
            self._AppendResource(effect, 'Texture', path, 'TextureReverseUV')
            if srcRect:
                _AppendParameter(effect, 'SourceUVs', srcRect)
        effect2 = self._MakeEffect('BlitIntoAlpha2')
        with _UpdateEffect(effect2):
            self._AppendResource(effect2, 'Texture', path, 'TextureReverseUV')
            self._AppendResource(effect2, 'MaskMap', mask, 'MaskReverseUV')
            if srcRect:
                _AppendParameter(effect2, 'SourceUVs', srcRect)
        self.renderJob.SetRenderState(trinity.D3DRS_BLENDOPALPHA, trinity.TRIBLENDOP_REVSUBTRACT)
        self._CompositeTexture(effect, subrect)
        self.renderJob.SetRenderState(trinity.D3DRS_BLENDOPALPHA, trinity.TRIBLENDOP_ADD)
        self._CompositeTexture(effect2, subrect)

    def BlitAlphaIntoAlphaWithMask(self, path, mask, subrect = None, srcRect = None):
        effect = self._MakeEffect('BlitIntoAlpha1')
        with _UpdateEffect(effect):
            self._AppendResource(effect, 'Texture', mask, 'TextureReverseUV')
            if srcRect:
                _AppendParameter(effect, 'SourceUVs', srcRect)
        effect2 = self._MakeEffect('BlitIntoAlpha2')
        with _UpdateEffect(effect2):
            self._AppendResource(effect2, 'Texture', path, 'TextureReverseUV')
            self._AppendResource(effect2, 'MaskMap', mask, 'MaskReverseUV')
            if srcRect:
                _AppendParameter(effect2, 'SourceUVs', srcRect)
        self.renderJob.SetRenderState(trinity.D3DRS_BLENDOPALPHA, trinity.TRIBLENDOP_REVSUBTRACT)
        self._CompositeTexture(effect, subrect)
        self.renderJob.SetRenderState(trinity.D3DRS_BLENDOPALPHA, trinity.TRIBLENDOP_ADD)
        self._CompositeTexture(effect2, subrect)

    def BlitAlphaIntoAlphaWithMaskAndZones(self, path, mask, zone, values, subrect = None, srcRect = None):
        effect = self._MakeEffect('BlitIntoAlpha1')
        with _UpdateEffect(effect):
            self._AppendResource(effect, 'Texture', mask, 'TextureReverseUV')
            if srcRect:
                _AppendParameter(effect, 'SourceUVs', srcRect)
        effect2 = self._MakeEffect('BlitIntoAlphaWithZones')
        with _UpdateEffect(effect2):
            self._AppendResource(effect2, 'Texture', path, 'TextureReverseUV')
            self._AppendResource(effect2, 'MaskMap', mask, 'MaskReverseUV')
            self._AppendResource(effect2, 'ZoneMap', zone, 'ZoneReverseUV')
            if srcRect:
                _AppendParameter(effect2, 'SourceUVs', srcRect)
            _AppendParameter(effect2, 'Color1', values)
        self.renderJob.SetRenderState(trinity.D3DRS_BLENDOPALPHA, trinity.TRIBLENDOP_REVSUBTRACT)
        self._CompositeTexture(effect, subrect)
        self.renderJob.SetRenderState(trinity.D3DRS_BLENDOPALPHA, trinity.TRIBLENDOP_ADD)
        self._CompositeTexture(effect2, subrect)

    def BlitTexture(self, path, maskPath, weight, subrect = None, addAlpha = False, skipAlpha = False, srcRect = None, multAlpha = False, isNormalMap = False):
        effect = self._MakeEffect('SimpleBlit')
        with _UpdateEffect(effect):
            self._AppendResource(effect, 'Texture', path, 'TextureReverseUV', mapType='N' if isNormalMap else '')
            self._AppendResource(effect, 'MaskMap', maskPath, 'MaskReverseUV')
            _AppendParameter(effect, 'Strength', weight)
            if multAlpha:
                _AppendParameter(effect, 'MultAlpha', 1.0)
            if srcRect:
                _AppendParameter(effect, 'SourceUVs', srcRect)
        if skipAlpha:
            self.renderJob.SetRenderState(trinity.D3DRS_SRCBLENDALPHA, trinity.TRIBLEND_ZERO)
        else:
            self.renderJob.SetRenderState(trinity.D3DRS_SRCBLENDALPHA, trinity.TRIBLEND_ONE)
        if addAlpha:
            self.renderJob.SetRenderState(trinity.D3DRS_DESTBLENDALPHA, trinity.TRIBLEND_ONE)
        else:
            self.renderJob.SetRenderState(trinity.D3DRS_DESTBLENDALPHA, trinity.TRIBLEND_ZERO)
        self.renderJob.SetRenderState(trinity.D3DRS_BLENDOPALPHA, trinity.TRIBLENDOP_ADD)
        self._CompositeTexture(effect, subrect)

    def ColorizedBlitTexture(self, detail, zone, overlay, color1, color2, color3, subrect = None, addAlpha = False, skipAlpha = False, useAlphaTest = False, srcRect = None, weight = 1.0, mask = None):
        if useAlphaTest:
            effect = self._MakeEffect('ColorizedBlit_AlphaTest')
        else:
            effect = self._MakeEffect('ColorizedBlit')
        with _UpdateEffect(effect):
            self._AppendResource(effect, 'DetailMap', detail, 'DetailReverseUV')
            self._AppendResource(effect, 'ZoneMap', zone, 'ZoneReverseUV')
            self._AppendResource(effect, 'OverlayMap', overlay, 'OverlayReverseUV')
            if mask:
                self._AppendResource(effect, 'MaskMap', mask, 'MaskReverseUV2')
            _AppendParameter(effect, 'Strength', weight)
            _AppendParameter(effect, 'Color1', color1)
            _AppendParameter(effect, 'Color2', color2)
            _AppendParameter(effect, 'Color3', color3)
            if srcRect:
                _AppendParameter(effect, 'SourceUVs', srcRect)
            if mask:
                _AppendParameter(effect, 'UseMask', 1.0)
        if skipAlpha:
            self.renderJob.SetRenderState(trinity.D3DRS_SRCBLENDALPHA, trinity.TRIBLEND_ZERO)
        else:
            self.renderJob.SetRenderState(trinity.D3DRS_SRCBLENDALPHA, trinity.TRIBLEND_ONE)
        if addAlpha:
            self.renderJob.SetRenderState(trinity.D3DRS_DESTBLENDALPHA, trinity.TRIBLEND_ONE)
        else:
            self.renderJob.SetRenderState(trinity.D3DRS_DESTBLENDALPHA, trinity.TRIBLEND_ZERO)
        self.renderJob.SetRenderState(trinity.D3DRS_BLENDOPALPHA, trinity.TRIBLENDOP_ADD)
        self._CompositeTexture(effect, subrect)

    def ColorizedCopyBlitTexture(self, detail, zone, overlay, color1, color2, color3, subrect = None, srcRect = None, weight = 1.0):
        effect = self._MakeEffect('ColorizedCopyBlit')
        with _UpdateEffect(effect):
            self._AppendResource(effect, 'DetailMap', detail, 'DetailReverseUV')
            self._AppendResource(effect, 'ZoneMap', zone, 'ZoneReverseUV')
            self._AppendResource(effect, 'OverlayMap', overlay, 'OverlayReverseUV')
            _AppendParameter(effect, 'Strength', weight)
            _AppendParameter(effect, 'Color1', color1)
            _AppendParameter(effect, 'Color2', color2)
            _AppendParameter(effect, 'Color3', color3)
            if srcRect:
                _AppendParameter(effect, 'SourceUVs', srcRect)
        self.renderJob.SetRenderState(trinity.D3DRS_BLENDOPALPHA, trinity.TRIBLENDOP_ADD)
        self._CompositeTexture(effect, subrect)

    def PatternBlitTexture(self, pattern, detail, zone, overlay, patterncolor1, patterncolor2, patterncolor3, color2, color3, subrect = None, patternTransform = (0, 0, 8, 8), patternRotation = 0.0, addAlpha = False, skipAlpha = False, srcRect = None):
        effect = self._MakeEffect('PatternBlit')
        with _UpdateEffect(effect):
            self._AppendResource(effect, 'PatternMap', pattern, 'PatternReverseUV')
            self._AppendResource(effect, 'DetailMap', detail, 'DetailReverseUV')
            self._AppendResource(effect, 'ZoneMap', zone, 'ZoneReverseUV')
            self._AppendResource(effect, 'OverlayMap', overlay, 'OverlayReverseUV')
            _AppendParameter(effect, 'PatternColor1', patterncolor1)
            _AppendParameter(effect, 'PatternColor2', patterncolor2)
            _AppendParameter(effect, 'PatternColor3', patterncolor3)
            _AppendParameter(effect, 'PatternTransform', patternTransform)
            _AppendParameter(effect, 'PatternRotation', patternRotation)
            _AppendParameter(effect, 'Color2', color2)
            _AppendParameter(effect, 'Color3', color3)
            if srcRect:
                _AppendParameter(effect, 'SourceUVs', srcRect)
        if skipAlpha:
            self.renderJob.SetRenderState(trinity.D3DRS_SRCBLENDALPHA, trinity.TRIBLEND_ZERO)
        else:
            self.renderJob.SetRenderState(trinity.D3DRS_SRCBLENDALPHA, trinity.TRIBLEND_ONE)
        if addAlpha:
            self.renderJob.SetRenderState(trinity.D3DRS_DESTBLENDALPHA, trinity.TRIBLEND_ONE)
        else:
            self.renderJob.SetRenderState(trinity.D3DRS_DESTBLENDALPHA, trinity.TRIBLEND_ZERO)
        self.renderJob.SetRenderState(trinity.D3DRS_BLENDOPALPHA, trinity.TRIBLENDOP_ADD)
        self._CompositeTexture(effect, subrect)
