#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\trinity\renderJobUtils.py
from . import _trinity
from . import _singletons
import blue as _blue

class RenderTargetManager(object):

    def __init__(self):
        self.targets = {}

    def _Get(self, key, function, *args):
        if key in self.targets and self.targets[key].object is not None:
            rt = self.targets[key].object
            if not rt.isValid:
                function(target=rt, *args)
            return rt

        def DeleteObject():
            self.targets.pop(key)

        rt = function(*args)
        self.targets[key] = _blue.BluePythonWeakRef(rt)
        self.targets[key].callback = DeleteObject
        return rt

    @staticmethod
    def _CreateDepthStencilAL(width, height, format, msaaType, msaaQuality, target = None):
        if target is None:
            target = _trinity.Tr2DepthStencil()
        target.Create(width, height, format, msaaType, msaaQuality)
        return target

    def GetDepthStencilAL(self, width, height, format, msaaType = 1, msaaQuality = 0, index = 0):
        key = (RenderTargetManager._CreateDepthStencilAL,
         index,
         width,
         height,
         format,
         msaaType,
         msaaQuality)
        return self._Get(key, RenderTargetManager._CreateDepthStencilAL, width, height, format, msaaType, msaaQuality)

    @staticmethod
    def _CreateRenderTargetAL(width, height, mipLevels, format, target = None):
        if target is None:
            target = _trinity.Tr2RenderTarget()
        target.Create(width, height, mipLevels, format)
        return target

    @staticmethod
    def _CreateRenderTargetMsaaAL(width, height, format, msaaType, msaaQuality, target = None):
        if target is None:
            target = _trinity.Tr2RenderTarget()
        target.Create(width, height, 1, format, msaaType, msaaQuality)
        return target

    def GetRenderTargetAL(self, width, height, mipLevels, format, index = 0):
        key = (RenderTargetManager._CreateRenderTargetAL,
         index,
         width,
         height,
         mipLevels,
         format)
        return self._Get(key, RenderTargetManager._CreateRenderTargetAL, width, height, mipLevels, format)

    def GetRenderTargetMsaaAL(self, width, height, format, msaaType, msaaQuality, index = 0):
        key = (RenderTargetManager._CreateRenderTargetMsaaAL,
         index,
         width,
         height,
         format,
         msaaType,
         msaaQuality)
        return self._Get(key, RenderTargetManager._CreateRenderTargetMsaaAL, width, height, format, msaaType, msaaQuality)

    def CheckRenderTarget(self, target, width, height, format):
        return target.width == width and target.height == height and target.format == format


renderTargetManager = RenderTargetManager()
