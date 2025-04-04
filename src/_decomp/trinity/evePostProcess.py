#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\trinity\evePostProcess.py
import decometaclass
import evegraphics.settings as gfxsettings
from .renderJobUtils import renderTargetManager as rtm
from . import _trinity as trinity
PP_GROUP_FOG = 'PP_GROUP_FOG'
PP_GROUP_BLOOM = 'PP_GROUP_BLOOM'
PP_GROUP_LUT = 'PP_GROUP_LUT'
POST_PROCESS_ASTEROID_FOG = 'ASTEROID_FOG'
POST_PROCESS_ICE_FOG = 'ICE_FOG'
POST_PROCESS_BLOOM_HIGH = 'BLOOM_HIGH'
POST_PROCESS_BLOOM_LOW = 'BLOOM_LOW'
POST_PROCESS_DESATURATE = 'DESATURATE'
POST_PROCESS_FADE_OUT = 'FADE_OUT'
POST_PROCESS_INCURSION_OVERLAY = 'INCURSION_OVERLAY'
POST_PROCESS_SHATTEREDWORMHOLE_OVERLAY = 'SHATTEREDWORMHOLE_OVERLAY'
POST_PROCESS_DEFAULT_LUT = 'POST_PROCESS_DEFAULT_LUT'
POST_PROCESS_GROUPS = {POST_PROCESS_ASTEROID_FOG: PP_GROUP_FOG,
 POST_PROCESS_ICE_FOG: PP_GROUP_FOG,
 POST_PROCESS_BLOOM_HIGH: PP_GROUP_BLOOM,
 POST_PROCESS_BLOOM_LOW: PP_GROUP_BLOOM,
 POST_PROCESS_INCURSION_OVERLAY: PP_GROUP_LUT,
 POST_PROCESS_SHATTEREDWORMHOLE_OVERLAY: PP_GROUP_LUT,
 POST_PROCESS_DEFAULT_LUT: PP_GROUP_LUT}
POST_PROCESS_PATHS = {POST_PROCESS_ASTEROID_FOG: 'res:/fisfx/postprocess/AsteroidFog.red',
 POST_PROCESS_ICE_FOG: 'res:/fisfx/postprocess/IcefieldFog.red',
 POST_PROCESS_INCURSION_OVERLAY: 'res:/dx9/scene/postprocess/sanshaInfest.red',
 POST_PROCESS_DESATURATE: 'res:/fisfx/postprocess/desaturate.red',
 POST_PROCESS_BLOOM_LOW: 'res:/fisfx/postprocess/BloomExp.red',
 POST_PROCESS_BLOOM_HIGH: 'res:/fisfx/postprocess/BloomVivid.red',
 POST_PROCESS_SHATTEREDWORMHOLE_OVERLAY: 'res:/dx9/scene/postprocess/TheraLUT.red',
 POST_PROCESS_DEFAULT_LUT: 'res:/dx9/scene/postprocess/DefaultLUT.red',
 POST_PROCESS_FADE_OUT: 'res:/fisfx/postprocess/FadeToBlack.red'}

class EvePostProcess(object):

    def __init__(self, name, path, key = None):
        self.name = name
        self.path = path
        self.key = key
        self.postProcess = trinity.Load(path)
        self.steps = []
        self.sourceSize = (0, 0)
        self.swapSize = (0, 0)
        self.buffer1 = None
        self.buffer2 = None
        self.viewport = None

    def RemoveSteps(self, rj):
        for each in self.steps:
            rj.steps.fremove(each)

        self._ClearSteps()

    def Prepare(self, source):
        if source is None:
            return
        self.sourceSize = (source.width, source.height)
        if len(self.postProcess.stages) < 2:
            return
        width = max(16, min(1024, (source.width & -16) / 2))
        height = max(16, min(1024, (source.height & -16) / 2))
        self.swapSize = (width, height)
        if self.buffer1 is None or not rtm.CheckRenderTarget(self.buffer1, width, height, source.format):
            self.buffer1 = rtm.GetRenderTargetAL(width, height, 1, source.format, index=1)
            if self.buffer1 is not None:
                self.buffer1.name = 'Post Process Bounce Target 1'
            self.buffer2 = rtm.GetRenderTargetAL(width, height, 1, source.format, index=2)
            if self.buffer2 is not None:
                self.buffer2.name = 'Post Process Bounce Target 2'

    def _SwapBuffers(self):
        tempTarget = self.buffer1
        self.buffer1 = self.buffer2
        self.buffer2 = tempTarget

    def _AppendStep(self, rj, step, name = None):
        rj.steps.append(step)
        self.steps.append(step)
        if name is not None:
            step.name = name

    def SetPSData(self, psData):
        for each in self.steps:
            if each.__bluetype__ != 'trinity.TriStepRenderEffect':
                continue
            each.shaderBuffer = psData

    def AddSteps(self, rj, psData, texcoords = None):
        del self.steps[:]
        effects = self.postProcess.stages
        if len(effects) > 1:
            self._AppendStep(rj, trinity.TriStepPushRenderTarget(), 'Store RT')
            value = (1.0 / self.swapSize[0],
             1.0 / self.swapSize[1],
             self.swapSize[0],
             self.swapSize[1])
            self._AppendStep(rj, trinity.TriStepSetVariableStore('g_texelSize', value), 'Set swap texelSize')
            self._AppendStep(rj, trinity.TriStepSetRenderTarget(self.buffer1), 'Set RT')
            self._AppendStep(rj, trinity.TriStepRenderEffect(effects[0], psData), effects[0].name)
            for i in range(1, len(effects) - 1):
                self._AppendStep(rj, trinity.TriStepSetRenderTarget(self.buffer2), 'Swap RT')
                self._AppendStep(rj, trinity.TriStepSetViewport(self.viewport), 'Set Viewport')
                self._AppendStep(rj, trinity.TriStepSetVariableStore('BlitCurrent', self.buffer1), 'Override var BlitCurrent')
                self._AppendStep(rj, trinity.TriStepRenderEffect(effects[i], psData), effects[i].name)
                self._SwapBuffers()

            self._AppendStep(rj, trinity.TriStepSetVariableStore('BlitCurrent', self.buffer1), 'Override var BlitCurrent')
            self._AppendStep(rj, trinity.TriStepPopRenderTarget(), 'Restore RT')
            value = (1.0 / self.sourceSize[0],
             1.0 / self.sourceSize[1],
             self.sourceSize[0],
             self.sourceSize[1])
            self._AppendStep(rj, trinity.TriStepSetVariableStore('g_texelSize', value), 'Set source texelSize')
        step = trinity.TriStepRenderEffect(effects[-1])
        self._AppendStep(rj, step, effects[-1].name)

    def _ClearSteps(self):
        del self.steps[:]

    def Release(self):
        self._ClearSteps()
        self.buffer1 = None
        self.buffer2 = None


class EvePostProcessingJob(object):
    __cid__ = 'trinity.TriRenderJob'
    __metaclass__ = decometaclass.BlueWrappedMetaclass
    _postProcessOrder = [PP_GROUP_FOG,
     PP_GROUP_BLOOM,
     PP_GROUP_LUT,
     POST_PROCESS_DESATURATE,
     POST_PROCESS_FADE_OUT]

    def __init__(self, *args):
        self.resolveTarget = None
        self.destination = None
        self.liveCount = 0
        self.prepared = False
        self.key = None
        self.postProcessPSData = None
        self.postProcesses = []
        for _ in self._postProcessOrder:
            self.postProcesses.append(None)

    def _FindPostProcess(self, ppID):
        index = -1
        postProcess = None
        for postProcess in self.postProcesses:
            if getattr(postProcess, 'name', None) == ppID:
                index = self.postProcesses.index(postProcess)
                break

        if index < 0 and id in self._postProcessOrder:
            index = self._postProcessOrder.index(ppID)
            postProcess = self.postProcesses[index]
        if index < 0:
            postProcess = None
        return (postProcess, index)

    def SetActiveKey(self, key = None):
        if self.key == key:
            return
        dirty = False
        for pp in self.postProcesses:
            ppKey = getattr(pp, 'key', None)
            if ppKey is None:
                continue
            if ppKey == key or ppKey == self.key:
                dirty = True
                break

        self.key = key
        if dirty:
            self.CreateSteps()

    def GetPostProcesses(self):
        postProcesses = []
        for each in self.postProcesses:
            if each is not None:
                postProcesses.append(each)

        return postProcesses

    def GetPostProcess(self, ppID):
        return self._FindPostProcess(self.GetGroupOrID(ppID))[0]

    def GetGroupOrID(self, ppID):
        ppIDOrGroup = ppID
        if ppID in POST_PROCESS_GROUPS:
            ppIDOrGroup = POST_PROCESS_GROUPS[ppID]
        return ppIDOrGroup

    def AddPostProcess(self, ppID, path = None, key = None):
        ppIDOrGroup = self.GetGroupOrID(ppID)
        postProcess, i = self._FindPostProcess(ppIDOrGroup)
        if path is None:
            if ppID not in POST_PROCESS_PATHS:
                return
            path = POST_PROCESS_PATHS[ppID]
        if ppIDOrGroup in self._postProcessOrder:
            i = self._postProcessOrder.index(ppIDOrGroup)
            postProcess = self.postProcesses[i]
            if postProcess is None:
                self.liveCount += 1
                postProcess = self.postProcesses[i] = EvePostProcess(ppIDOrGroup, path, key)
            elif postProcess.path != path:
                postProcess = self.postProcesses[i] = EvePostProcess(ppIDOrGroup, path, key)
        elif postProcess is None:
            self.liveCount += 1
            postProcess = EvePostProcess(ppIDOrGroup, path, key)
            self.postProcesses.append(postProcess)
        elif postProcess.path != path:
            postProcess = self.postProcesses[i] = EvePostProcess(ppIDOrGroup, path, key)
        if self.prepared:
            postProcess.Prepare(self.source)
        self.CreateSteps()
        return postProcess

    def RemovePostProcess(self, ppID):
        index = -1
        ppIDOrGroup = self.GetGroupOrID(ppID)
        for each in self.postProcesses:
            if getattr(each, 'name', None) == ppIDOrGroup:
                index = self.postProcesses.index(each)
                break

        if index < 0:
            return
        self.liveCount -= 1
        self.postProcesses[index].RemoveSteps(self)
        self.postProcesses[index].Release()
        if ppIDOrGroup in self._postProcessOrder:
            self.postProcesses[index] = None
        else:
            self.postProcesses.remove(each)
        self.CreateSteps()

    def SetPostProcessVariable(self, ppID, variable, value):
        ppIDOrGroup = self.GetGroupOrID(ppID)
        for pp in self.postProcesses:
            if pp is not None and pp.name == ppIDOrGroup:
                for effect in pp.postProcess.stages:
                    for param in effect.parameters:
                        if param.name == variable:
                            param.value = value
                            return

                    for res in effect.resources:
                        if res.name == variable:
                            res.SetResource(value)
                            return

    def _AppendStep(self, name, step, rj = None):
        if rj is None:
            rj = self
        rj.steps.append(step)
        step.name = name

    def _DoPostProcess(self, pp, source):
        job = trinity.TriRenderJob()
        job.name = 'Run Post Process ' + str(pp.name)
        self._AppendStep('Set var BlitOriginal', trinity.TriStepSetVariableStore('BlitOriginal', self.resolveTarget), job)
        self._AppendStep('Set var BlitCurrent', trinity.TriStepSetVariableStore('BlitCurrent', self.resolveTarget), job)
        texcoords = None
        if hasattr(self, 'viewport') and self.viewport.object is not None:
            self._AppendStep('Set Viewport', trinity.TriStepSetViewport(self.viewport.object), job)
        pp.AddSteps(job, self.postProcessPSData, texcoords)
        self._AppendStep(job.name, trinity.TriStepRunJob(job))

    def SetPostProcessPSData(self, psData):
        self.postProcessPSData = psData
        for pp in self.postProcesses:
            if pp is not None:
                pp.SetPSData(psData)

    def Prepare(self, source, blitTexture, destination = None, viewport = None):
        self.prepared = True
        self.resolveTarget = blitTexture
        self.source = source
        self.destination = destination
        if viewport is not None:
            self.viewport = viewport
        for each in self.postProcesses:
            if each is not None:
                each.Prepare(source)

    def Release(self):
        self.prepared = False
        self.ClearSteps()
        self.resolveTarget = None
        self.source = None
        self.destination = None
        for each in self.postProcesses:
            if each is not None:
                each.Release()

    def CreateSteps(self):
        if not self.prepared:
            return
        self.ClearSteps()
        if self.liveCount < 1:
            return
        if self.source.width < 1 or self.source.height < 1:
            return
        postProcesses = []
        for each in self.postProcesses:
            ppKey = getattr(each, 'key', None)
            if each is not None and each.name == PP_GROUP_FOG:
                if gfxsettings.Get(gfxsettings.GFX_SHADER_QUALITY) != gfxsettings.SHADER_MODEL_HIGH:
                    continue
            if each is not None and (ppKey is None or ppKey == self.key):
                postProcesses.append(each)

        if self.destination is not None:
            self._AppendStep('Push Destination RT', trinity.TriStepPushRenderTarget(self.destination))
        if len(postProcesses) > 1:
            self._AppendStep('Push Source RT', trinity.TriStepPushRenderTarget(self.source))
        self._AppendStep('Push null depth stencil', trinity.TriStepPushDepthStencil(None))
        if self.resolveTarget is not None:
            self._AppendStep('Resolve render target', trinity.TriStepResolve(self.resolveTarget, self.source))
        self._AppendStep('Set render states', trinity.TriStepSetStdRndStates(trinity.RM_FULLSCREEN))
        value = (1.0 / self.source.width,
         1.0 / self.source.height,
         self.source.width,
         self.source.height)
        self._AppendStep('Set var texelSize', trinity.TriStepSetVariableStore('g_texelSize', value))
        for pp in postProcesses:
            if pp == postProcesses[-1] and len(postProcesses) > 1:
                self._AppendStep('Pop source RT', trinity.TriStepPopRenderTarget())
            self._DoPostProcess(pp, self.resolveTarget)
            if pp != postProcesses[-1] and self.resolveTarget is not None:
                self._AppendStep('Resolve render target', trinity.TriStepResolve(self.resolveTarget, self.source))

        if self.destination is not None:
            self._AppendStep('Pop destination RT', trinity.TriStepPopRenderTarget())
        self._AppendStep('Restore depth stencil', trinity.TriStepPopDepthStencil())

    def ClearSteps(self):
        for each in self.postProcesses:
            if each is not None:
                each.RemoveSteps(self)

        del self.steps[:]
