#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\MobileWarpDisruptor.py
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject
SOUND_EFFECT_EMITTER_NAME = 'forcefield_audio'

class MobileWarpDisruptor(SpaceObject):

    def Assemble(self):
        godmaStateManager = self.sm.GetService('godma').GetStateManager()
        godmaType = godmaStateManager.GetType(self.typeID)
        self.effectRadius = godmaType.warpScrambleRange
        if self.model is not None:
            anchored = not self.isFree
            if anchored:
                self.ShowForcefield(animated=False)
            else:
                self.SetColor('green')
        self.ScaleAttenuation(self.effectRadius)

    def ShowForcefield(self, animated = True):
        self.SetRadius(self.effectRadius)
        for cs in self.model.Find('trinity.TriCurveSet'):
            if cs.name == 'Collapse':
                if animated:
                    cs.Play()
                else:
                    cs.PlayFrom(cs.GetMaxCurveDuration())
                break

    def SetColor(self, col):
        if col == 'red':
            self.ShowForcefield()
        elif col == 'green':
            self.SetRadius(0.0)
            self.FadeOutEffectSound()

    def SetRadius(self, r):
        scale = r / 20000.0
        for cs in self.model.Find('trinity.TriCurveSet'):
            if cs.name == 'Collapse':
                cs.bindings[0].scale = scale
                break

    def ScaleAttenuation(self, effectRadius):
        emitter = self.GetNamedAudioEmitterFromObservers(SOUND_EFFECT_EMITTER_NAME)
        if emitter is not None:
            emitter.SetAttenuationScalingFactor(effectRadius)

    def FadeOutEffectSound(self):
        emitter = self.GetNamedAudioEmitterFromObservers(SOUND_EFFECT_EMITTER_NAME)
        if emitter is not None:
            emitter.SendEvent('fade_out')
