#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\graphicEffects\audio.py
import audio2
import trinity

def AddEmitterToModel(emitterName, model, effectRadius, position = None, direction = None, scaling = 1.0):
    observer = GetExistingObserver(model, emitterName)
    if observer is None:
        observer = CreateNewAudioEmitter(emitterName, position, direction)
        model.observers.append(observer)
    if getattr(observer, 'observer', None) is not None:
        if effectRadius < 0:
            return
        attenuation = pow(effectRadius, 0.95) * 33 * scaling
        observer.observer.SetAttenuationScalingFactor(attenuation)
        return observer.observer


def GetExistingObserver(location, name):
    if location is not None:
        for observer in location.Find('trinity.TriObserverLocal'):
            if getattr(observer, 'observer', None) is not None:
                if observer.observer.name == name:
                    return observer


def CreateNewAudioEmitter(emitter_name, position = None, direction = None):
    observer = trinity.TriObserverLocal()
    if position:
        observer.position = position
    if direction:
        observer.direction = direction
    entity = audio2.AudEmitter(emitter_name)
    observer.observer = entity
    return observer
