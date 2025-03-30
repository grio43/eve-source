#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\trinity\sceneRenderJobSpaceTransition.py
from .sceneRenderJobSpace import SceneRenderJobSpace
from .renderJob import renderJobs

def CreateSceneRenderJobSpaceTransition(name = None):
    newRJ = SceneRenderJobSpaceTransition()
    if name is not None:
        newRJ.ManualInit(name)
    else:
        newRJ.ManualInit()
    return newRJ


class SceneRenderJobSpaceTransition(SceneRenderJobSpace):

    def Start(self):
        self.renderOrder = 1
        super(SceneRenderJobSpaceTransition, self).Start()
        self.EnableGpuEmission(True)
        self.ScheduleUpdateJob()
