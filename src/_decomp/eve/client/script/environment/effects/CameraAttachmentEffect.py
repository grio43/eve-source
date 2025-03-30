#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\effects\CameraAttachmentEffect.py
from eve.client.script.environment.effects.GenericEffect import GenericEffect, STOP_REASON_DEFAULT
import trinity
import logging
log = logging.getLogger(__name__)

class CameraAttachmentEffect(GenericEffect):
    __guid__ = 'effects.CameraAttachmentEffect'

    def __init__(self, trigger, effect = None, graphicFile = None):
        super(CameraAttachmentEffect, self).__init__(trigger, effect, graphicFile)
        self.fileName = self.graphicFile
        self.fxSequencer = sm.GetService('FxSequencer')
        self.scene = self.fxSequencer.GetScene()
        if graphicFile is not None:
            self.effect = self.RecycleOrLoad(graphicFile)
        else:
            self.effect = None
        print self.effect

    def Start(self, duration):
        if self.effect:
            self.effect.StartControllers()
            if self.scene:
                self.scene.cameraAttachments.append(self.effect)
        else:
            log.error('Could not load cameraAttachment %s.' % self.fileName)

    def Stop(self, reason = STOP_REASON_DEFAULT):
        if self.scene and self.scene.cameraAttachments:
            if self.effect in self.scene.cameraAttachments:
                self.scene.cameraAttachments.fremove(self.effect)
        self.scene = None
        self.effect = None
