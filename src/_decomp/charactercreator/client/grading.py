#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\charactercreator\client\grading.py
from trinity.renderJobUtils import renderTargetManager as rtm
import trinity
import blue
import walk
import os
import log

class PostProcess(object):

    def __init__(self, path, backbuffer, viewport = None, format = None):
        self.job = trinity.evePostProcess.EvePostProcessingJob()
        self.job.name = 'Post Processing'
        self.backbuffer = backbuffer
        self.format = format
        if viewport is not None:
            self.vp = trinity.TriViewport()
            self.viewport = blue.BluePythonWeakRef(self.vp)
            self.UpdateViewport(viewport.object)
        else:
            self.vp = None
            self.viewport = None
        trinity.device.RegisterResource(self)
        self.SetPostProcess(path)

    def OnInvalidate(self, *args):
        self.blitTexture = None
        self.job.Release()

    def OnCreate(self, device):
        width = self.backbuffer.width
        height = self.backbuffer.height
        if self.format is None:
            self.format = trinity.device.GetRenderContext().GetBackBufferFormat()
        blitFormat = self.format
        self.blitTexture = rtm.GetRenderTargetAL(width, height, 1, blitFormat, index=1)
        self.job.Prepare(self.backbuffer, self.blitTexture, self.backbuffer, self.viewport)
        self.job.CreateSteps()

    def SetPostProcess(self, path):
        self.job.AddPostProcess('postProcess', path)
        self.OnCreate(trinity.device)

    def GetJob(self):
        return self.job

    def UpdateViewport(self, new_viewport):
        if self.viewport is not None:
            self.viewport.object.width = new_viewport.width
            self.viewport.object.height = new_viewport.height
            self.viewport.object.x = new_viewport.x
            self.viewport.object.y = new_viewport.y


def bluepynormcase(astring):
    return os.path.normcase(astring).replace('\\', '/')


def GetDDS():
    respaths = list()
    for dir, subdirs, filenames in walk.walk('res:/dx9/scene/postprocess/'):
        subdirs[:] = list()
        for filename in filenames:
            if os.path.splitext(filename)[1].lower() == '.dds':
                resPath = os.path.join(dir, filename)
                respaths.append(bluepynormcase(resPath))

    return respaths


def GetTexLUT(job = None):
    if job is not None:
        rj = job
    else:
        rj = trinity.renderJobs.FindByName('BaseSceneRenderJob')
    if rj:
        for step in rj.steps:
            if step.name == 'RJ_POSTPROCESSING':
                for substep in step.job.steps:
                    if substep.name == 'Run Post Process postProcess':
                        for subsubstep in substep.job.steps:
                            if subsubstep.name == 'portraitLUT':
                                for r in subsubstep.effect.resources:
                                    if r.name == 'TexLUT':
                                        return r


def GetLUTIntensity(job = None):
    if job is not None:
        rj = job
    else:
        rj = trinity.renderJobs.FindByName('BaseSceneRenderJob')
    if rj:
        for step in rj.steps:
            if step.name == 'RJ_POSTPROCESSING':
                for substep in step.job.steps:
                    if substep.name == 'Run Post Process postProcess':
                        for subsubstep in substep.job.steps:
                            if subsubstep.name == 'portraitLUT':
                                for r in subsubstep.effect.parameters:
                                    if r.name == 'Influence':
                                        return r


def GetLUTStepRenderEffect(job = None):
    if job is not None:
        rj = job
    else:
        rj = trinity.renderJobs.FindByName('BaseSceneRenderJob')
    if rj:
        for step in rj.steps:
            if step.name == 'Run Post Process postProcess':
                for substep in step.job.steps:
                    if substep.name == 'portraitLUT':
                        return substep
