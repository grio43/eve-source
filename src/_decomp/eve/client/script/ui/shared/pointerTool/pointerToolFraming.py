#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\pointerTool\pointerToolFraming.py
import trinity
from carbonui.uicore import uicore
import carbonui.const as uiconst

def CreateBinding(key, element, elementFrame, bindingDict, curveSet):
    RemoveBindingFromDict(key, bindingDict, curveSet)
    elementRenderObject = getattr(element, 'renderObject', None)
    elementFrameRenderObject = getattr(elementFrame, 'renderObject', None)
    if not elementRenderObject or not elementFrameRenderObject:
        return
    leftBinding = trinity.CreatePythonBinding(curveSet, element, 'absoluteLeft', elementFrame, 'left')
    topBinding = trinity.CreatePythonBinding(curveSet, element, 'absoluteTop', elementFrame, 'top')
    widthBinding = trinity.CreatePythonBinding(curveSet, element, 'absoluteRight', elementFrame, 'frameWidth')
    heightBinding = trinity.CreatePythonBinding(curveSet, element, 'absoluteBottom', elementFrame, 'frameHeight')
    bindingDict[key] = [leftBinding,
     topBinding,
     widthBinding,
     heightBinding]


def RemoveBindingFromDict(key, bindingDict, curveSet):
    bindings = bindingDict.pop(key, None)
    if bindings:
        RemoveBindings(bindings, curveSet)


def RemoveBindings(bindings, curveSet):
    l, t, w, h = bindings
    curveSet.bindings.fremove(l)
    curveSet.bindings.fremove(t)
    curveSet.bindings.fremove(w)
    curveSet.bindings.fremove(h)


def RemoveAllFrames(bindingDict, frameDict, curveSet):
    for key, bindings in bindingDict.iteritems():
        RemoveBindings(bindings, curveSet)

    bindingDict.clear()
    for eachFrameInfo in frameDict.itervalues():
        eachFrame, _ = eachFrameInfo
        _CloseFrame(eachFrame)

    frameDict.clear()


def RemoveOldFrames(frameDict, bindingDict, curveSet):
    framesToRemove = set()
    for eachKey, eachFrameInfo in frameDict.iteritems():
        f, element = eachFrameInfo
        if not element or element.destroyed or not element.IsVisible():
            framesToRemove.add(eachKey)

    for keyName in framesToRemove:
        RemoveBindingFromDict(keyName, bindingDict, curveSet)
        frameInfo = frameDict.pop(keyName, None)
        if frameInfo:
            f, _ = frameInfo
            _CloseFrame(f)


def _CloseFrame(frame):
    if frame and not frame.destroyed:
        uicore.animations.StopAllAnimations(frame)
        frame.Close()


def ChangePickStateOfAllFrames(frameDict, isEnabled):
    newState = uiconst.UI_NORMAL if isEnabled else uiconst.UI_DISABLED
    for eachFrame, _ in frameDict.itervalues():
        eachFrame.state = newState
