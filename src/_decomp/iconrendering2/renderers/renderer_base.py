#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\iconrendering2\renderers\renderer_base.py
import os
import blue
import trinity
import time
import logging
from iconrendering2.const import IconBackground, IconOverlay, Language

class IconRenderInfo(object):

    def __init__(self, folder, filename, size, renderFormat):
        self.outputFolder = folder
        self.outputFilename = filename
        self.renderSize = size
        self.renderFormat = renderFormat
        self.inputIcon = None
        self.background = IconBackground.NONE
        self.backgroundColor = None
        self.backgroundTransparent = False
        self.overlay = IconOverlay.NONE
        self.foreground = None
        self.outlineColor = None
        self.metadata = None
        self.language = Language.ENGLISH
        self.style = None

    @property
    def outputPath(self):
        return os.path.join(self.outputFolder, self.outputFilename)

    def __eq__(self, other):
        return self.outputPath == other.outputPath

    def __hash__(self):
        return hash(self.outputPath)


class OutputInfo(object):

    def __init__(self, renderInfo):
        self.outputPath = renderInfo.outputPath
        self.size = renderInfo.renderSize
        self.style = renderInfo.style
        self.language = renderInfo.language


class IconRenderer(object):

    def __init__(self, language = Language.ENGLISH):
        self._renderInfos = set()
        self._language = language

    def __str__(self):
        raise NotImplementedError

    def AddRenderInfo(self, renderInfo):
        self._renderInfos.add(renderInfo)

    def RemoveRenderInfo(self, outputPath):
        for each in self._renderInfos:
            if each.outputPath == outputPath:
                self._renderInfos.remove(each)
                break

    def HasRenderInfos(self):
        return len(self._renderInfos) > 0

    def GetOutputList(self):
        return [ OutputInfo(info) for info in self._renderInfos ]

    def GetOutputPaths(self):
        return [ info.outputPath for info in self._renderInfos ]

    def Render(self):
        start = time.clock()
        prevLanguageID = None
        if self._language:
            blue.motherLode.clear()
            prevLanguageID = blue.os.languageID
            blue.os.languageID = self._language
            trinity.WaitForResourceLoads()
        errors = []
        self._PrepareRender()
        for renderInfo in self._renderInfos:
            try:
                import os
                os.makedirs(os.path.dirname(renderInfo.outputPath))
            except OSError:
                pass

            try:
                self._Render(renderInfo)
            except RenderException as e:
                errors.append((e.target, e.message))

        self._FinishRender()
        if self._language:
            blue.os.languageID = prevLanguageID
            blue.motherLode.clear()
        end = time.clock()
        elapsed = end - start
        if len(self.GetOutputPaths()) > 0:
            logging.debug('%s (%.3f seconds):' % (self, elapsed))
            for output in self.GetOutputPaths():
                logging.debug('- %s' % output)

        return errors

    def _PrepareRender(self):
        pass

    def _FinishRender(self):
        pass

    def _Render(self, renderInfo):
        raise NotImplementedError


class RenderException(Exception):

    def __init__(self, errorMessage, target):
        super(RenderException, self).__init__(errorMessage)
        self.target = target
