#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\environments\environmentAudio.py
import audio2
import logging
import trinity
from carbon.client.script.environment.audioService import GetAudioService
from evegraphics.environments import BaseEnvironmentObject
from tacticalNavigation import ballparkFunctions
log = logging.getLogger(__name__)

class EnvironmentAudio(BaseEnvironmentObject):

    def __init__(self, audioTriggers):
        super(EnvironmentAudio, self).__init__()
        self.audioEffectRoot = None
        self.ball = None
        self.emitter = None
        self.onEnterSoundID = audioTriggers.onEnter

    def Setup(self):
        pass

    def ApplyToScene(self):
        from environmentManager import EnvironmentManager
        if EnvironmentManager.BALLPARK_MODE:
            self.ball = ballparkFunctions.AddClientBall(self.environmentPosition)
        if self.onEnterSoundID:
            self.audioEffectRoot = trinity.EveEffectRoot2()
            self.audioEffectRoot.name = 'EnvironmentSound'
            self.audioEffectRoot.translationCurve = self.ball
            observerLocal = trinity.TriObserverLocal()
            self.emitter = audio2.AudEmitter('environment_ambience_sfx')
            observerLocal.observer = self.emitter
            self.audioEffectRoot.observers.append(observerLocal)
            if self.scene:
                self.scene.objects.append(self.audioEffectRoot)
            GetAudioService().HandleFsdSoundID(self.onEnterSoundID, emitter=self.emitter)

    def TearDown(self):
        if self.scene and self.audioEffectRoot in self.scene.objects:
            self.scene.objects.fremove(self.audioEffectRoot)
        del self.audioEffectRoot
        self.audioEffectRoot = None
        if self.ball is not None:
            ballparkFunctions.RemoveClientBall(self.ball)
        self.emitter = None
        self.scene = None
