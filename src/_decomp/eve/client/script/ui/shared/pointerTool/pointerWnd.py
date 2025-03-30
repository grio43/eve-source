#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\pointerTool\pointerWnd.py
import uthread
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.util.various_unsorted import IsUnder
from carbonui.control.checkbox import Checkbox
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelSmall
from eve.client.script.ui.control.eveScroll import Scroll
from carbonui.control.window import Window
import carbonui.const as uiconst
from carbonui.uicore import uicore
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.shared.pointerTool.pointerFrame import PointerFrame
from eve.client.script.ui.shared.pointerTool.pointerToolConst import SOURCE_LOCATION_WINDOW
from eve.client.script.ui.shared.pointerTool.pointerToolFraming import CreateBinding, RemoveAllFrames, RemoveOldFrames
from eve.client.script.ui.shared.pointerTool.pointerToolFunctions import GetScreenElementsByUniqueName, FindElementUnderMouse
from eve.client.script.ui.shared.pointerTool.pointerToolUtil import GetFilteredScrollList
from globalConfig.getFunctions import ArePointerLinksActive
from localization import GetByLabel
import log
FRAME_UPDATE_INTERVAL_MSEC = 200

class PointerToolWnd(Window):
    __guid__ = 'pointerToolWnd'
    __notifyevents__ = ['OnMapShortcut', 'OnFavoriteGroupChanged']
    default_height = 500
    default_width = 500
    default_minSize = (300, 300)
    default_windowID = 'pointerToolWnd'
    default_iconNum = 'res:/UI/Texture/WindowIcons/UIHelper.png'
    default_captionLabelPath = 'UI/Help/PointerWndName'
    default_isCompactable = True

    def DebugReload(self, *args):
        self.Close()
        uthread.new(PointerToolWnd)

    def ApplyAttributes(self, attributes):
        self.updateFrameThread = None
        Window.ApplyAttributes(self, attributes)
        if not ArePointerLinksActive(sm.GetService('machoNet')):
            log.LogError("Trying to open the pointer tool when it's not allowed")
            Window.Close(self)
            return
        self.frameCurveSet = uicore.animations.CreateCurveSet(useRealTime=True)
        self.frameCurveSet.name = 'frameCurveSet'
        self.frameCurveSet.Play()
        self.pythonBindings = {}
        self.frameCont = getattr(uicore.desktop, 'pointerFrameCont', None)
        if not self.frameCont or self.frameCont.destroyed:
            self.frameCont = Container(name='pointerFrameCont', parent=uicore.desktop, align=uiconst.TOALL, state=uiconst.UI_DISABLED, idx=0)
            uicore.desktop.pointerFrameCont = self.frameCont
        self.frameCont.Flush()
        self.frameDict = {}
        self._selectedObject = None
        self._hiliteFrame = Fill(parent=uicore.desktop, align=uiconst.ABSOLUTE, color=(0, 1, 0, 0.3), idx=0, state=uiconst.UI_DISABLED)
        self._selectedFrame = Frame(parent=uicore.desktop, align=uiconst.ABSOLUTE, color=(0, 1, 0, 0.3), idx=0, state=uiconst.UI_DISABLED)
        aboutWndCont = ContainerAutoSize(name='aboutWndCont', parent=self.sr.main, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, minHeight=16)
        aboutIcon = MoreInfoIcon(parent=aboutWndCont, align=uiconst.TOPLEFT, hint=GetByLabel('UI/Help/PointerWndText'))
        text = GetByLabel('UI/Help/AboutHelpPointerWindow')
        labelLeft = aboutIcon.left + aboutIcon.width + 12
        label = EveLabelMedium(text=text, parent=aboutWndCont, padLeft=labelLeft, state=uiconst.UI_NORMAL, color=None, align=uiconst.TOTOP)
        label.opacity = 0.75
        self.shortcutLabel = None
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdGetUiPointer')
        if cmd:
            shortcutCont = ContainerAutoSize(name='shortcutCont', parent=self.sr.main, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, minHeight=16)
            moreInfoIcon = MoreInfoIcon(parent=shortcutCont, align=uiconst.TOPLEFT, hint=GetByLabel('UI/Help/PointerWndTextWithoutShortcut', cmdName=cmd.GetName()))
            text = self.GetShortcutText()
            labelLeft = moreInfoIcon.left + moreInfoIcon.width + 12
            self.shortcutLabel = EveLabelMedium(text=text, parent=shortcutCont, padLeft=labelLeft, state=uiconst.UI_NORMAL, color=None, align=uiconst.TOTOP)
            self.shortcutLabel.opacity = 0.75
        text = GetByLabel('UI/Help/PointerWndShowHighlights')
        areFramesVisible = settings.user.ui.Get('poingerWnd_showFrames', False)
        cb = Checkbox(text=text, parent=self.sr.main, settingsPath=('user', 'ui'), settingsKey='poingerWnd_showFrames', checked=areFramesVisible, callback=self.CheckBoxChange, align=uiconst.TOTOP)
        self.cbText = EveLabelMedium(name='cbText', parent=self.sr.main, text=GetByLabel('UI/Help/PointerWndShowHighlightsDesc'), align=uiconst.TOTOP, padLeft=cb.padLeft + cb.label.padLeft, padBottom=8)
        self.SetDisplaysFromCheckbox(cb)
        self.topRightCont = ContainerAutoSize(name='topRightCont2', parent=self.sr.main, align=uiconst.TOTOP, clipChildren=True, padding=(0, 0, 0, 4))
        filterEditCont = ContainerAutoSize(parent=self.topRightCont, align=uiconst.TOTOP, maxWidth=120)
        self.filterEdit = QuickFilterEdit(name='filterEdit', parent=filterEditCont, hintText=GetByLabel('UI/Inventory/Filter'), maxLength=64, align=uiconst.TOPRIGHT, OnClearFilter=self.OnFilterEditCleared, width=120, isTypeField=True)
        self.filterEdit.ReloadFunction = self.OnFilterEdit
        self.scroll = Scroll(parent=self.sr.main, padding=(0, 4, 0, 0), id='pointerScroll')
        self.scroll.multiSelect = False
        self.LoadContent()
        self._keyDownCookie = uicore.uilib.RegisterForTriuiEvents([uiconst.UI_KEYDOWN], self.OnGlobalKeyDown)
        if areFramesVisible:
            self._UpdateFrames()
            self.updateFrameThread = AutoTimer(FRAME_UPDATE_INTERVAL_MSEC, self._UpdateFrames)
        sm.RegisterNotify(self)
        uicore.registry.SetFocus(self.filterEdit)

    def GetShortcutText(self):
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdGetUiPointer')
        if cmd:
            if cmd.shortcut:
                shortcut = '<b>%s</b>' % cmd.GetShortcutAsString()
            else:
                shortcut = GetByLabel('UI/Help/ShortcutNotSet')
            return GetByLabel('UI/Help/PointerWndTextWithShortcut', shortcut=shortcut)
        return ''

    def OnMapShortcut(self, *args):
        if self.shortcutLabel:
            self.shortcutLabel.text = self.GetShortcutText()

    def CheckBoxChange(self, cb, *args):
        framesAreVisible = cb.checked
        if framesAreVisible:
            self._UpdateFrames()
            self.updateFrameThread = AutoTimer(FRAME_UPDATE_INTERVAL_MSEC, self._UpdateFrames)
        else:
            self.updateFrameThread = False
        self.SetDisplaysFromCheckbox(cb)

    def SetDisplaysFromCheckbox(self, cb):
        text = GetByLabel('UI/Help/PointerWndShowHighlights')
        framesAreVisible = cb.checked
        self.cbText.display = framesAreVisible
        self.frameCont.display = framesAreVisible
        for eachFrame in self.frameDict.itervalues():
            if eachFrame and not eachFrame[0].destroyed:
                eachFrame[0].display = framesAreVisible

        cb.label.text = text

    def LoadContent(self, selectedName = None):
        scrollList = self.GetScrollList(selectedName)
        self.scroll.LoadContent(contentList=scrollList, noContentHint=GetByLabel('UI/Common/NothingFound'))

    def GetScrollList(self, selectedName = None):
        filterText = self.filterEdit.GetValue().strip().lower()
        scrollList = GetFilteredScrollList(filterText, selectedName, sourceLocation=SOURCE_LOCATION_WINDOW)
        if len(scrollList) == 1:
            scrollList[0]['forceOpen'] = True
        return scrollList

    def OnFilterEditCleared(self):
        self.LoadContent()

    def OnFilterEdit(self):
        self.LoadContent()

    def _FrameElements(self, elementsToFrame):
        for key, eachElement in elementsToFrame.iteritems():
            if eachElement is None or eachElement.destroyed or not eachElement.display:
                continue
            f, _ = self.frameDict.get(key, (None, None))
            if f and not f.destroyed:
                continue
            try:
                if isinstance(eachElement, Window) and eachElement.sr.underlay:
                    bgParent = eachElement.sr.underlay
                else:
                    bgParent = eachElement
                f = PointerFrame(bgParent=bgParent, idx=0, state=uiconst.UI_DISABLED, color=(0.2, 0.6, 1, 0.3))
            except StandardError as e:
                elementPos = eachElement.GetAbsolute()
                f = PointerFrame(parent=self.frameCont, align=uiconst.ABSOLUTE, color=(0.2, 0.6, 1, 0.3), idx=0, state=uiconst.UI_DISABLED, pos=elementPos)
                self._CreateBinding(key, eachElement, f)

            uicore.animations.FadeTo(f, 0.4, 0.6, duration=1.5, loops=uiconst.ANIM_REPEAT, curveType=uiconst.ANIM_BOUNCE)
            self.frameDict[key] = (f, eachElement)

    def _RemoveOldFrames(self):
        RemoveOldFrames(self.frameDict, self.pythonBindings, self.frameCurveSet)

    def _UpdateFrames(self):
        if not settings.user.ui.Get('poingerWnd_showFrames', False):
            self.updateFrameThread = None
            return
        self._RemoveOldFrames()
        allPointers = sm.GetService('helpPointer').GetAllPointersByElementName()
        missingElementNames = [ x for x in allPointers.iterkeys() if x not in self.frameDict ]
        if missingElementNames:
            dictOfMissingElements = GetScreenElementsByUniqueName(missingElementNames)
            if dictOfMissingElements:
                self._FrameElements(dictOfMissingElements)

    def _CreateBinding(self, key, element, elementFrame):
        CreateBinding(key, element, elementFrame, self.pythonBindings, self.frameCurveSet)

    def OnGlobalKeyDown(self, *args, **kwds):
        if not settings.user.ui.Get('poingerWnd_showFrames', False):
            return True
        if self.destroyed:
            return False
        ctrl = uicore.uilib.Key(uiconst.VK_CONTROL)
        mo = uicore.uilib.mouseOver
        if ctrl and not (IsUnder(mo, self) or mo is self):
            uthread.new(self.ShowUIObject, mo)
        return True

    def ShowUIObject(self, mouseOver):
        selectedElmentName = None
        selectedNode = self.scroll.GetSelected()
        if selectedNode:
            selectedElmentName = selectedNode[0].uiElementName
        uiElementName, _ = FindElementUnderMouse(mouseOver)
        if not uiElementName:
            self.scroll.DeselectAll()
            return
        if uiElementName == selectedElmentName:
            self.scroll.ScrollToSelectedNode()
            return
        self.scroll.DeselectAll()
        self.filterEdit.SetValue('', docallback=False)
        self.LoadContent(uiElementName)
        self.scroll.ScrollToSelectedNode()

    def OnFavoriteGroupChanged(self):
        self.LoadContent()

    def Close(self, *args, **kwds):
        self.updateFrameThread = None
        try:
            self._RemoveAllFramesAndStopCurveSet()
            uicore.event.UnregisterForTriuiEvents(self._keyDownCookie)
        except StandardError as e:
            print 'e = ', e

        frame = getattr(self, '_hiliteFrame', None)
        if frame:
            frame.Close()
        if getattr(self, '_selectedFrame', None):
            self._selectedFrame.Close()
        Window.Close(self, *args, **kwds)

    def _RemoveAllFramesAndStopCurveSet(self):
        RemoveAllFrames(self.pythonBindings, self.frameDict, self.frameCurveSet)
        self.frameCont.Flush()
        if getattr(uicore.desktop, 'pointerFrameCont', None):
            uicore.desktop.pointerFrameCont.Close()
            delattr(uicore.desktop, 'pointerFrameCont')
        self.frameCurveSet.Stop()
        self.frameCurveSet = None
