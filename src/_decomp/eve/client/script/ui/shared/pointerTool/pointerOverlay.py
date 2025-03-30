#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\pointerTool\pointerOverlay.py
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
import carbonui.const as uiconst
from carbonui.control.window import Window
from eve.client.script.ui.shared.pointerTool.pointerFrame import PointerFill
from eve.client.script.ui.shared.pointerTool.pointerToolFraming import RemoveOldFrames, RemoveAllFrames, CreateBinding
from eve.client.script.ui.shared.pointerTool.pointerToolFunctions import GetScreenElementsByUniqueName
import log

class PointerOverlay(object):

    def __init__(self):
        self.fillDict = {}
        self.pythonBindings = {}
        self.fillCurveSet = uicore.animations.CreateCurveSet(useRealTime=True)
        self.fillCont = Container(name='pointerFillCont', parent=uicore.desktop, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN, idx=0)
        self.isActive = False

    def ShowOverlay(self):
        log.LogInfo('UI Pointer overlay:ShowOverlay')
        self._RemoveAllFills()
        try:
            self.isActive = True
            self.FrameAllUiElements()
        except:
            self.HideOverlay()
            raise

    def HideOverlay(self):
        log.LogInfo('UI Pointer overlay:HideOverlay')
        self.isActive = False
        self._RemoveAllFills()
        if self.fillCont:
            self.fillCont.Flush()

    def _RemoveAllFills(self):
        log.LogInfo('UI Pointer overlay:_RemoveAllFills')
        RemoveAllFrames(self.pythonBindings, self.fillDict, self.fillCurveSet)
        self.ForceCleanupAllFills()

    def FrameAllUiElements(self):
        log.LogInfo('UI Pointer overlay:FrameAllUiElements')
        RemoveOldFrames(self.fillDict, self.pythonBindings, self.fillCurveSet)
        allPointers = sm.GetService('helpPointer').GetAllPointersByElementName()
        allUiElementNames = allPointers.keys()
        dictOfElementsToFrame = GetScreenElementsByUniqueName(allUiElementNames)
        self._FrameElements(dictOfElementsToFrame)

    def _FrameElements(self, elementsToFrame):
        for key, eachElement in elementsToFrame.iteritems():
            if not self.isActive:
                return
            if eachElement is None or eachElement.destroyed or not eachElement.display:
                continue
            f, _ = self.fillDict.get(key, (None, None))
            if f and not f.destroyed:
                pass
            else:
                try:
                    if isinstance(eachElement, Window) and eachElement.sr.underlay:
                        parent = eachElement
                    else:
                        parent = eachElement
                    f = PointerFill(parent=parent, idx=0, state=uiconst.UI_NORMAL, colorRGB=(0.2, 0.6, 1), uiElementName=key)
                except StandardError as e:
                    elementPos = eachElement.GetAbsolute()
                    f = PointerFill(parent=self.fillCont, align=uiconst.ABSOLUTE, colorRGB=(0.2, 0.6, 1), idx=0, state=uiconst.UI_NORMAL, pos=elementPos, uiElementName=key)
                    self._CreateBinding(key, eachElement, f)

                if f:
                    self.fillDict[key] = (f, eachElement)
                    uicore.animations.FadeTo(f, 0.4, 0.6, duration=1.5, loops=uiconst.ANIM_REPEAT, curveType=uiconst.ANIM_BOUNCE)

        if not self.isActive:
            self._RemoveAllFills()

    def _CreateBinding(self, key, element, elementFrame):
        CreateBinding(key, element, elementFrame, self.pythonBindings, self.fillCurveSet)

    def ForceCleanupAllFills(self):
        toClose = []
        self.FindDeepPointerFill(uicore.desktop, toClose)
        for eachElement in toClose:
            if eachElement and not eachElement.destroyed:
                eachElement.Close()

        if toClose:
            log.LogTraceback('Pointer Overlay: had to manually remove fills')

    def FindDeepPointerFill(self, element, fillsToClose):
        if isinstance(element, PointerFill):
            fillsToClose.append(element)
        children = getattr(element, 'children', None)
        if not children:
            return
        for child in children:
            results = self.FindDeepPointerFill(child, fillsToClose)
            if results is not None:
                return results
