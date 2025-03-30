#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\iconrendering2\renderers\renderer_fromfile.py
from renderer_base import IconRenderer
from utils_renderer import RenderToBitmapFromIcon
from iconrendering2.const import Language
_savingInProgress = []

class FromFileIconRenderer(IconRenderer):

    def __init__(self, language = Language.ENGLISH):
        super(FromFileIconRenderer, self).__init__(language)
        self.useAsyncSave = True

    def __str__(self):
        return 'From File Icon Renderer <%s>' % hex(id(self))

    def _Render(self, renderInfo):
        global _savingInProgress
        if renderInfo.inputIcon:
            bitmap = RenderToBitmapFromIcon(renderInfo)
            if self.useAsyncSave:
                _savingInProgress = [ x for x in _savingInProgress if not x.IsSaveCompleted() ]
                bitmap.SaveAsync(renderInfo.outputPath)
                _savingInProgress.append(bitmap)
            else:
                bitmap.Save(renderInfo.outputPath)
