#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\paperDoll\renderDrivers.py
import trinity
import types
import uthread
from eve.common.script.paperDoll import paperDollCommonFunctions as pdCf
import commonClientFunctions as pdCcf
import eve.common.script.paperDoll.paperDollDefinitions as pdDef
import paperDollPortrait as pdPor

class RenderDriver:

    def __init__(self):
        self._chainedRenderDriver = None

    def SetChainedRenderDriver(self, chainedRenderDriver):
        if not isinstance(chainedRenderDriver, RenderDriver):
            return False
        if self._chainedRenderDriver:
            self._chainedRenderDriver = chainedRenderDriver
            return
        self._chainedRenderDriver = chainedRenderDriver
        imethods = [ (n, getattr(self, n), getattr(chainedRenderDriver, n)) for n in dir(self) if not n.startswith('_') and n != 'SetChainedRenderDriver' and type(getattr(self, n)) is types.MethodType and hasattr(chainedRenderDriver, n) ]
        for i in xrange(len(imethods)):
            imethodPair = imethods[i]
            imName = imethodPair[0]
            thisObjIM = imethodPair[1]
            nextObjIM = imethodPair[2]
            thisObjIM = setattr(self, imName, self._CallChainedDeco(thisObjIM.im_func, nextObjIM.im_func))

    def _CallChainedDeco(self, first, second):

        def wrapped(*args, **kwargs):
            extraArgs = kwargs
            newArgs = first(self, *args, **kwargs)
            if newArgs is not None:
                extraArgs.update(newArgs)
            second(self._chainedRenderDriver, *args, **extraArgs)

        return wrapped

    def OnBeginUpdate(self, doll):
        pass

    def OnModifierUVChanged(self, modifier):
        pass

    def OnModifierRedfileLoaded(self, modifier, redfilePath):
        pass

    def OnApplyMorphTargets(self, meshes, morphTargets):
        pass

    def ApplyShaders(self, doll, meshes):
        pass

    def OnFinalizeAvatar(self, visualModel, avatar, updateRuleBundle, doll, factory):
        pass

    def OnEndUpdate(self, avatar, visualModel, doll, factory, **kwargs):
        pass


class RenderDriverNCC(RenderDriver):

    def __init__(self):
        RenderDriver.__init__(self)
        self.wrinkleFx = None

    def OnBeginUpdate(self, doll):
        pass

    def OnModifierUVChanged(self, modifier):
        pass

    def OnModifierRedfileLoaded(self, modifier, redfilePath):
        pass

    def OnApplyMorphTargets(self, meshes, morphTargets):
        pass

    def ApplyShaders(self, doll, meshes):
        self.wrinkleFx = []
        if not meshes:
            return
        skinLightmapRendererActive = lambda : doll.skinLightmapRenderer is not None
        tasklets = []
        asyncMeshes = {}
        for mesh in iter(meshes):
            if skinLightmapRendererActive():
                asyncMeshes[mesh] = False
            if pdDef.DOLL_PARTS.HEAD in mesh.name:
                t = uthread.new(self.SetInteriorShader, *(asyncMeshes,
                 mesh,
                 self.wrinkleFx,
                 doll))
            else:
                t = uthread.new(self.SetInteriorShader, *(asyncMeshes,
                 mesh,
                 None,
                 doll))
            tasklets.append(t)
            uthread.schedule(t)

        pdCf.WaitForAll(tasklets, lambda x: x.alive)
        for mesh in asyncMeshes.iterkeys():
            if skinLightmapRendererActive() and asyncMeshes[mesh]:
                doll.skinLightmapRenderer.BindLightmapShader(mesh)

    def SetInteriorShader(self, asyncMeshes, mesh, wrinkleFx, doll):
        fx = pdCcf.GetEffectsFromMesh(mesh)
        tasklets = []
        for f in iter(fx):
            t = uthread.new(self.SetInteriorShaderForFx_t, *(f,
             asyncMeshes,
             mesh,
             wrinkleFx,
             doll))
            tasklets.append(t)

        pdCf.WaitForAll(tasklets, lambda x: x.alive)
        t = uthread.new(self.SetDecalClip, mesh)
        pdCf.WaitForAll([t], lambda x: x.alive)

    def SetDecalClip(self, mesh):
        effects = []
        if type(mesh) is trinity.Tr2Mesh:
            for area in mesh.decalAreas:
                effects += pdCcf.GetEffectsFromAreaList([area])

        for f in effects:
            f.StartUpdate()
            f.PopulateParameters()
            pm = f.parameters.FindByName('DecalClip')
            if pm:
                pm.value = 1.0
            f.EndUpdate()

    def SetInteriorShaderForFx_t(self, effect, asyncMeshes, mesh, wrinkleFx, doll):
        path = effect.effectFilePath.lower()
        if 'masked.fx' in path:
            return
        if self.BindCustomShader(effect, doll.useFastShader, doll):
            return
        if asyncMeshes:
            asyncMeshes[mesh] = True
        suffix = '.fx'
        if doll.useFastShader and ('_fast.fx' in path or path in pdDef.SHADERS_THAT_CAN_SWITCH_TO_FAST_SHADER_MODE):
            suffix = '_fast.fx'
        if doll.useDXT5N and ('_dxt5n.fx' in path or path in pdDef.SHADERS_TO_ENABLE_DXT5N):
            suffix = '{0}_dxt5n.fx'.format(suffix[:-3])
        self.BindInteriorShader(effect, wrinkleFx, doll, suffix)

    def BindCustomShader(self, effect, useFastShaders, doll):
        name = effect.name.lower()
        if name.startswith('c_custom') or name.startswith('c_s2'):
            pdPor.PortraitTools.BindCustomShaders(effect, useFastShaders, doll)
            return True
        return False

    def BindClothShaders(self, mesh, doll, isHair):
        if doll.currentLOD <= 0:
            fx = pdCcf.GetEffectsFromMesh(mesh)
            for f in iter(fx):
                f.StartUpdate()
                try:
                    isHair = pdPor.PortraitTools.BindHeroHairShader(f, '.fx') or isHair
                    if doll.currentLOD <= pdDef.LOD_SKIN:
                        pdPor.PortraitTools.BindHeroClothShader(f, doll.useDXT5N)
                finally:
                    f.EndUpdate()

        return isHair

    def BindInteriorShader(self, effect, wrinkleFx, doll, suffix):
        effect.StartUpdate()
        try:
            path = effect.effectFilePath.lower()
            if pdDef.DOLL_PARTS.HAIR not in path:
                if doll.currentLOD >= 0:
                    if 'skinnedavatarbrdf' not in path:
                        effect.effectFilePath = '{0}{1}'.format(pdDef.INTERIOR_AVATAR_EFFECT_FILE_PATH[:-3], suffix)
                        if not effect.resources.FindByName('FresnelLookupMap'):
                            res = trinity.TriTextureParameter()
                            res.name = 'FresnelLookupMap'
                            res.resourcePath = pdDef.FRESNEL_LOOKUP_MAP
                            effect.resources.append(res)
                elif doll.currentLOD == pdDef.LOD_A:
                    pass
                elif doll.currentLOD in [pdDef.LOD_SKIN]:
                    pdPor.PortraitTools.BindSkinShader(effect, wrinkleFx, scattering=False, buildDataManager=doll.buildDataManager, gender=doll.gender, use_png=pdDef.USE_PNG, fxSuffix=suffix)
                    pdPor.PortraitTools.BindLinearAvatarBRDF(effect, suffix)
                elif doll.currentLOD == pdDef.LOD_SCATTER_SKIN:
                    pdPor.PortraitTools.BindSkinShader(effect, wrinkleFx, scattering=True, buildDataManager=doll.buildDataManager, gender=doll.gender, use_png=pdDef.USE_PNG, fxSuffix=suffix)
                    pdPor.PortraitTools.BindLinearAvatarBRDF(effect, suffix)
            elif doll.currentLOD <= 0:
                pdPor.PortraitTools.BindHeroHairShader(effect, suffix)
        finally:
            effect.EndUpdate()

    def OnFinalizeAvatar(self, visualModel, avatar, updateRuleBundle, doll, factory):
        if updateRuleBundle.meshesChanged:
            if self.wrinkleFx:
                pdPor.PortraitTools().SetupWrinkleMapControls(avatar, self.wrinkleFx, doll)

    def OnEndUpdate(self, avatar, visualModel, doll, factory, **kwargs):
        pass
