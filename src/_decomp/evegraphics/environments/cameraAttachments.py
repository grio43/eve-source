#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\environments\cameraAttachments.py
from evegraphics.environments import BaseEnvironmentObject
import evegraphics.settings as gfxsettings
import logging
import trinity
log = logging.getLogger(__name__)

class CameraAttachments(BaseEnvironmentObject):

    def __init__(self, cameraAttachmentsResPaths):
        super(CameraAttachments, self).__init__(cameraAttachmentsResPaths)
        self.resPaths = cameraAttachmentsResPaths
        self.cameraAttachments = []

    def IsDisabled(self):
        return gfxsettings.Get(gfxsettings.UI_ASTEROID_ATMOSPHERICS) == 0

    def ApplyToScene(self):
        if self.IsDisabled():
            return
        self.scene.cameraAttachments.extend(self.cameraAttachments)

    def Setup(self):
        self.cameraAttachments = []
        for resPath in self.resPaths:
            log.debug("Creating a cameraAttachment with path='%s'", resPath)
            obj = self.Load(resPath)
            if obj:
                self.cameraAttachments.append(obj)
            else:
                log.error('Could not load cameraAttachment %s.' % resPath)

    def TearDown(self):
        log.debug('Tearing down cameraAttachments')
        for attachment in self.cameraAttachments:
            if self.scene:
                self.scene.cameraAttachments.fremove(attachment)
            del attachment

        self.cameraAttachments = []
        self.scene = None
