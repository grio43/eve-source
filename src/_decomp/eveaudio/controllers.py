#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveaudio\controllers.py
import trinity
from .helpers import FindEmitterByName

def GetEmittersFromOwner(controllerOwner, targetChild = ''):
    emitters = []
    if isinstance(controllerOwner, trinity.EveMultiEffect):
        for parameter in controllerOwner.parameters:
            if targetChild and targetChild != parameter.name:
                continue
            emitters.extend(GetEmittersFromOwner(parameter.object))

    elif hasattr(controllerOwner, 'Find'):
        emitters = controllerOwner.Find('audio2.AudEmitter')
    return emitters


def StopControllerSounds(controller):
    owner = controller.GetOwner()
    playSoundActions = controller.Find('trinity.Tr2ActionPlaySound')
    for action in playSoundActions:
        if action.event:
            emitter = FindEmitterByName(action.emitter, owner)
            if emitter:
                emitter.StopEvent(action.event)
