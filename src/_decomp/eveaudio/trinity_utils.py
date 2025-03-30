#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveaudio\trinity_utils.py
import trinity
from utils import create_emitter

def create_observer(name):
    emitter = create_emitter(name)
    observer = trinity.TriObserverLocal()
    observer.name = name
    observer.observer = emitter
    return observer
