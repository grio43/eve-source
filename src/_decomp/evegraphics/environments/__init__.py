#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\environments\__init__.py
import blue
import trinity

class BaseEnvironmentObject(object):
    DEBUG_MODE = False

    @staticmethod
    def EnableDebugMode():
        BaseEnvironmentObject.DEBUG_MODE = True

    @staticmethod
    def DisableDebugMode():
        BaseEnvironmentObject.DEBUG_MODE = False

    def __init__(self, *args):
        self.environmentPosition = (0, 0, 0)
        self.environmentTranslationCurves = []
        self.environmentRadius = 0
        self.scene = None
        self.renderJob = None

    def InClientMode(self):
        try:
            return cfg.mapSystemCache is not None and session.solarsystemid is not None
        except AttributeError:
            return False
        except NameError:
            return False

    def Load(self, path):
        return trinity.Load(path, nonCached=self.DEBUG_MODE)

    def IsDisabled(self):
        return False

    def Setup(self):
        raise NotImplementedError('Setup is not implemented')

    def SetEnvironmentPosition(self, environmentPosition):
        self.environmentPosition = environmentPosition

    def SetEnvironmentTranslationCurves(self, translationCurves):
        self.environmentTranslationCurves = translationCurves

    def SetEnvironmentRadius(self, radius):
        self.environmentRadius = radius

    def GetLocalEnvironmentPosition(self):
        if len(self.environmentTranslationCurves) == 0:
            return [0, 0, 0]
        pos = [0, 0, 0]
        for curve in self.environmentTranslationCurves:
            curvePos = curve.GetVectorAt(blue.os.GetSimTime())
            pos[0] += curvePos.x
            pos[1] += curvePos.y
            pos[2] += curvePos.z

        return pos

    def ApplyToRenderJob(self, renderJob):
        self.renderJob = renderJob
        self.scene = self.renderJob.scene.object

    def ApplyToCamera(self, camera):
        pass

    def ApplyToScene(self):
        raise NotImplementedError('ApplyToScene is not implemented')

    def Refresh(self):
        pass

    def TearDown(self):
        raise NotImplementedError('TearDown is not implemented')

    def LinkToDistanceField(self, distanceFieldEnvironmentItem):
        pass

    def GetLockedAttributes(self):
        pass

    def SetIgnoredAttributes(self, attributes):
        pass
