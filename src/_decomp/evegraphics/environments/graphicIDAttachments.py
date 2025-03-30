#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\environments\graphicIDAttachments.py
from evegraphics.environments import BaseEnvironmentObject
import logging
import trinity
from fsdBuiltData.common.graphicIDs import GetGraphicFile
log = logging.getLogger(__name__)

class GraphicIDAttachments(BaseEnvironmentObject):

    def __init__(self, foregroundGraphics, backgroundGraphics):
        super(GraphicIDAttachments, self).__init__()
        self.backgroundGraphicIDs = backgroundGraphics
        self.backgroundGraphicsObjects = []
        self.foregroundGraphicIDs = foregroundGraphics
        self.foregroundGraphicsObjects = []

    def ApplyToScene(self):
        if self.IsDisabled():
            return
        self.scene.objects.extend(self.foregroundGraphicsObjects)
        self.scene.backgroundObjects.extend(self.backgroundGraphicsObjects)

    def Setup(self):
        self.backgroundGraphicsObjects = self._GetGraphicObjects(self.backgroundGraphicIDs)
        self.foregroundGraphicsObjects = self._GetGraphicObjects(self.foregroundGraphicIDs)

    def _GetGraphicObjects(self, graphicIDList):
        result = []
        for graphicID in graphicIDList:
            log.debug("Creating a graphicID with id='%s'", graphicID)
            resPath = GetGraphicFile(graphicID)
            if not resPath:
                log.error('Trying to load a graphicID (%s) that has no graphicFile into environment template' % graphicID)
                continue
            obj = self.Load(resPath)
            if obj:
                result.append(obj)
            else:
                log.error('Could not load GraphicIDAttachment %s.' % resPath)

        return result

    def TearDown(self):
        log.debug('Tearing down GraphicIDAttachments')
        for graphicObjects in self.foregroundGraphicsObjects:
            if self.scene:
                self.scene.objects.fremove(graphicObjects)
            del graphicObjects

        for graphicObjects in self.backgroundGraphicsObjects:
            if self.scene:
                self.scene.backgroundObjects.fremove(graphicObjects)
            del graphicObjects

        self.foregroundGraphicsObjects = []
        self.backgroundGraphicsObjects = []
