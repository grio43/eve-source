#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\validators\audioValidation.py
import blue
from evegraphics.validation.commonUtilities import Validate

@Validate('TriObserverLocal')
def UnboundObserverMustHaveName(context, observer):
    if observer.name:
        return
    curves = blue.FindInterface(context.root, 'AudEventCurve')
    referencedObservers = set((x.sourceTriObserver for x in curves))
    if observer not in referencedObservers:
        context.Error(observer, 'observer not referenced by a curve should have a name')


@Validate('TriObserverLocal')
def ObserverMustAnObserverLol(context, observer):
    if not observer.observer:
        context.Error(observer, 'observer must have an observer :)')
