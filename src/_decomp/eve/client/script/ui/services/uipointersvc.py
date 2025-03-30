#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\uipointersvc.py
import blue
import collections
import uthread
import sys
import log
import carbonui.const as uiconst
import telemetry
import mathext
import utillib
from carbon.common.script.sys.service import Service
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.control.window import Window
from eve.client.script.ui.shared.neocom.neocom import neocomSettings
from localization import GetByLabel
from uihighlighting.const import UiHighlightDirections
from uihighlighting.ui.uiutil import UI_CLASS_BY_NAME, DEFAULT_UI_CLASS
from uihighlighting.ui.spaceobjectpointer import SpaceObjectPointer, SpaceObjectUiPointerData
from uihighlighting.ui.uipointer import CustomUiPointer, UiPointerData
from uihighlighting.ui.uipointer import UIPOINTER_WIDTH, UIPOINTER_HEIGHT, POINTER_ARROW_WIDTH, POINTER_ARROW_HEIGHT
from uihighlighting import uihighlightaudio
from uihighlighting.statelogger import StateLogger
from carbonui.uicore import uicore
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
WAITING_FOR_ELEMENT_TO_COME_BACK_MS = 500
HINT_WORKER_DELAY_MS = 2000
HINT_DISPLAY_DELAY_MS = 250

class UIPointerSvc(Service):
    __exportedcalls__ = {}
    __guid__ = 'svc.uipointerSvc'
    __notifyevents__ = ['OnSessionChanged',
     'ProcessSessionReset',
     'OnEveMenuShown',
     'DoBallRemove',
     'OnUIScalingChange',
     'OnToggleWindowed',
     'DoBallsRemove',
     'OnInvItemDropEnded']
    __servicename__ = 'UIPointers'
    __displayname__ = 'UI Pointer Service'
    __dependencies__ = ['michelle']
    specialCasedPointers = (pConst.UNIQUE_NAME_LOCAL_CHAT,
     pConst.UNIQUE_NAME_CORP_CHAT,
     pConst.UNIQUE_NAME_FLEET_CHAT,
     pConst.UNIQUE_NAME_NEXT_IN_ROUTE)

    def __init__(self):
        Service.__init__(self)
        self.running = True
        self.pointersAreSuppressed = False
        self.oldObscurers = {}
        self.statelogger = StateLogger(self)

    def Run(self, memStream = None):
        self.elementUrls = collections.defaultdict(list)
        self.pointerUIByItemID = {}
        self.spaceObjectPointerLock = uthread.Semaphore()
        self.pointerDataByItemID = {}
        self.pointerDataByDungeonObjectID = {}
        self.pointerDataByDungeonEntityGroupID = {}
        self.pointerDataByTypeID = {}
        self.pointerDataByByGroupID = {}
        self.pointerDataNextInRoute = None
        self.suppressedSpaceObjectUiPointers = set()
        self.spaceObjectUiPointerUpdater = None
        self.uiPointersByPointToID = {}
        self.uiElementsToHighlight = set()
        self.neocomSvc = sm.GetService('neocom')
        self.uiPointerUpdateThread = None

    def Stop(self, memStream = None):
        self.running = False
        self.ClearPointers()

    def ProcessSessionReset(self):
        self.ClearPointers()

    def OnSessionChanged(self, isremote, sess, change):
        if 'charid' in change and change['charid'][1] is not None:
            self.Run()
        if 'shipid' in change:
            oldShipID, newShipID = change['shipid']
            if newShipID is not None:
                self.FlushSpaceObjectPointer(newShipID)

    def OnEveMenuShown(self):
        for pointer in self.uiPointersByPointToID.values():
            if pointer.pointToElement.name == 'eveMenuBtn':
                self.ClearPointers()

    def OnUIScalingChange(self, change, *args):
        for pointToID in self.uiElementsToHighlight.copy():
            self.RestartUiPointer(pointToID)

        if self.spaceObjectUiPointerUpdater is not None:
            self.RestartSpacePointers(clearPointers=True)

    def OnToggleWindowed(self, isWindowed):
        if not isWindowed:
            self.RestartSpacePointers(clearPointers=True)

    def ShouldHidePointers(self):
        if uicore.layer.systemmenu.isopen:
            return True
        if sm.GetService('viewState').IsViewActive('charactercreation'):
            return True
        return self.pointersAreSuppressed

    def SuppressPointers(self):
        self.pointersAreSuppressed = True

    def RevealPointers(self):
        self.pointersAreSuppressed = False

    def UpdatePointers(self):
        if not self.uiElementsToHighlight:
            self.uiPointerUpdateThread = None
        for pointToID in self.uiElementsToHighlight.copy():
            try:
                self._UpdatePointer(pointToID)
            except:
                log.LogException("UpdatePointers failed for pointToID '%s'." % str(pointToID))

    def _UpdatePointer(self, pointToID):
        currentPointer = self.uiPointersByPointToID.get(pointToID, None)
        if currentPointer is None:
            return
        if self.ShouldHidePointers():
            self.HidePointer(pointToID)
        else:
            uiPointerElement = currentPointer.uiPointerElement
            pointToElement = currentPointer.pointToElement
            considerations = currentPointer.considerations
            oldPointLeft = currentPointer.oldPointLeft
            oldPointUp = currentPointer.oldPointUp
            oldPointDown = currentPointer.oldPointDown
            basicData = currentPointer.basicData
            if pointToElement is None or pointToElement.destroyed or isinstance(pointToElement, Window) and pointToElement.stacked:
                blue.pyos.synchro.SleepWallclock(WAITING_FOR_ELEMENT_TO_COME_BACK_MS)
                elementUrl = self.elementUrls.get(pointToID, None)
                rediscoveredKeyVal = self.FindElementToPointTo(elementUrl)
                rediscoveredElement = rediscoveredKeyVal.pointToElement if rediscoveredKeyVal else None
                if rediscoveredElement is None or rediscoveredElement.destroyed:
                    self.HidePointer(pointToID)
                    return
                pointToElement = rediscoveredElement
                currentPointer.pointToElement = rediscoveredElement
                uiPointerElement.UpdatePointToElement(rediscoveredElement)
            locationData = self.GetLocation(basicData, pointToElement, considerations)
            cumTop, cumLeft, pointLeft, pointUp, pointDown, isObscured, arrowPos = locationData
            if cumTop <= 0 and cumLeft <= 0 or pointToElement.state == uiconst.UI_HIDDEN:
                self.HidePointer(pointToID)
            else:
                self.ShowPointer(pointToID)
            if uiPointerElement.destroyed or pointLeft != oldPointLeft or pointUp != oldPointUp or pointDown != oldPointDown:
                self.ClearPointer(pointToID)
                basicData.audioSetting = False
                elementContainer = self.ConstructPointer(pointLeft, pointUp, pointDown, arrowPos, basicData, pointToElement)
                elementContainer.SetPosition(cumLeft, cumTop)
                self.uiPointersByPointToID[pointToID] = UiPointerData(uiPointerElement=elementContainer, pointToElement=pointToElement, considerations=considerations, oldPointLeft=pointLeft, oldPointUp=pointUp, oldPointDown=pointDown, basicData=basicData)
                uthread.new(self._UpdatePointer, pointToID)
            else:
                uiPointerElement.SetPosition(cumLeft, cumTop)

    def FindDeep(self, element, idOfItemToFind, shouldExcludeInvisible = False):
        if getattr(element, 'uniqueUiName', None) == idOfItemToFind or getattr(element, 'name', None) == idOfItemToFind:
            if not shouldExcludeInvisible or getattr(element, 'display', False):
                return element
        children = getattr(element, 'children', None)
        if not children:
            return
        for child in children:
            results = self.FindDeep(child, idOfItemToFind, shouldExcludeInvisible)
            if results is not None:
                return results

    def GetLocation(self, basicData, element, directive):
        pointToID = basicData.pointToID
        defaultDirection = basicData.defaultDirection
        offset = basicData.offset or 0
        try:
            parent = element
            while hasattr(parent, 'parent'):
                if parent is None or parent.state == uiconst.UI_HIDDEN:
                    return (-999,
                     -999,
                     False,
                     False,
                     False,
                     False,
                     0)
                if self.SkipElementDueToClipping(element, parent) and not basicData.showEvenOffscreen:
                    return (-999,
                     -999,
                     False,
                     False,
                     False,
                     False,
                     0)
                parent = parent.parent

            if pointToID in self.uiPointersByPointToID:
                uiPointer = self.uiPointersByPointToID[pointToID]
                pointerWidth = uiPointer.uiPointerElement.width
                pointerHeight = uiPointer.uiPointerElement.height
            else:
                uiPointer = None
                pointerWidth, pointerHeight = UIPOINTER_WIDTH, UIPOINTER_HEIGHT
            if directive == 'shipui' and element.parent.name == 'slotsContainer':
                if element.parent.name == 'slotsContainer':
                    slotsContainer = element.parent
                    cumTop, cumLeft = slotsContainer.absoluteTop + element.top, slotsContainer.absoluteLeft + element.left + 5
            elif directive == 'bracket':
                parent = element.parent
                cumTop, cumLeft = parent.absoluteTop + element.top, parent.absoluteLeft + element.left - 2
            elif directive == 'neocom':
                cumTop, cumLeft = element.absoluteTop, element.absoluteLeft
            elif hasattr(element, 'absoluteTop') and hasattr(element, 'absoluteLeft'):
                cumTop, cumLeft = element.absoluteTop - 2, element.absoluteLeft - 2
            else:
                cumTop, cumLeft = element.parent.absoluteTop + element.top - 2, element.parent.absoluteLeft + element.left - 2
            pointLeft = True
            height = element.height if element.height else element.absoluteBottom - element.absoluteTop
            width = element.width if element.width else element.absoluteRight - element.absoluteLeft
            cumTop += height / 2 - pointerHeight / 2
            if defaultDirection in (UiHighlightDirections.UP, UiHighlightDirections.DOWN):
                pointerLeft = cumLeft + width / 2 - pointerWidth / 2
            else:
                pointerLeft = cumLeft - offset - pointerWidth
            if pointerLeft <= 0:
                cumLeft = self._MoveToRightSide(element, directive, cumLeft) + offset
            else:
                pointLeft = False
                cumLeft = self._MoveToLeftSide(cumLeft, pointerWidth) - offset
            pointUp = False
            pointDown = False
            arrowPos = 0
            if cumTop < 0 or defaultDirection == UiHighlightDirections.UP and cumTop - pointerHeight / 2 < 0:
                if directive == 'neocom':
                    additionalSpace = 8
                    arrowPos = cumTop - additionalSpace
                    cumTop = additionalSpace
                else:
                    pointUp = True
                    cumTop, cumLeft = self._MoveToBottom(element, directive, cumTop, height, pointerWidth, pointerHeight)
                    cumTop += offset
            elif cumTop + pointerHeight > uicore.desktop.height:
                if directive == 'neocom':
                    additionalSpace = 8
                    cumTop = uicore.desktop.height - pointerHeight - additionalSpace
                else:
                    pointDown = True
                    cumTop, cumLeft = self._MoveToTop(pointToID, element, pointerWidth, pointerHeight)
                    cumTop -= offset
            elif pointLeft == False:
                if directive == 'bracket':
                    cumTop -= 3
            elif directive == 'bracket':
                cumLeft += POINTER_ARROW_WIDTH
                cumTop -= 3
            if directive == 'eveMenuBtn':
                cumTop, cumLeft, pointLeft, pointUp, pointDown, arrowPos = self.GetEveMenuLocation(pointerHeight, pointerWidth)
            if self._ShouldMoveToAuthoredSide(defaultDirection, pointLeft, pointUp, pointDown):
                if defaultDirection == UiHighlightDirections.RIGHT:
                    newLeft = self._MoveToRightSide(element, directive, cumLeft) + pointerWidth
                    newLeft += 2 * offset
                    if self._IsLeftInView(newLeft, pointerWidth):
                        pointLeft = True
                        cumLeft = newLeft
                elif defaultDirection == UiHighlightDirections.UP:
                    newTop, newLeft = self._MoveToTop(pointToID, element, pointerWidth, pointerHeight)
                    newTop -= offset
                    if self._IsInView(newLeft, newTop, pointerWidth, pointerHeight):
                        pointDown = True
                        cumLeft = newLeft
                        cumTop = newTop
                elif defaultDirection == UiHighlightDirections.DOWN:
                    if uiPointer and uiPointer.uiPointerElement.pointDirections:
                        if not uiPointer.uiPointerElement.pointDirections[0]:
                            pointerHeight += POINTER_ARROW_HEIGHT
                    newTop, newLeft = self._MoveToBottom(element, directive, cumTop, height, pointerWidth, pointerHeight)
                    newTop += offset
                    if self._IsInView(newLeft, newTop, pointerWidth, pointerHeight):
                        pointUp = True
                        cumLeft = newLeft
                        cumTop = newTop
            if basicData.showEvenOffscreen:
                cumLeft = mathext.clamp(cumLeft, 0, uicore.desktop.width - width)
                cumTop = mathext.clamp(cumTop, 0, uicore.desktop.height - height)
            isObscured = self.CheckIsElementObscured(pointToID, cumTop, cumLeft, pointLeft, element)
            return (cumTop,
             cumLeft,
             pointLeft,
             pointUp,
             pointDown,
             isObscured,
             arrowPos)
        except:
            log.LogException('GetLocation encountered an Exception.')
            sys.exc_clear()
            return (-999,
             -999,
             False,
             False,
             False,
             False,
             0)

    def SkipElementDueToClipping(self, element, parent):
        if getattr(element, pConst.ALLOWS_POINTER_CLIPPING, False):
            return False
        clipped = element.IsCompletelyClipped(parent)
        return clipped

    def _IsInView(self, left, top, pointerWidth, pointerHeight):
        return self._IsLeftInView(left, pointerWidth) and self._IsTopInView(top, pointerHeight)

    def _IsLeftInView(self, left, pointerWidth):
        return left + pointerWidth < uicore.desktop.width

    def _IsTopInView(self, top, pointerHeight):
        return top + pointerHeight < uicore.desktop.height

    def _ShouldMoveToAuthoredSide(self, defaultDirection, pointLeft, pointUp, pointDown):
        pointRight = not (pointLeft or pointUp or pointDown)
        return defaultDirection and defaultDirection != UiHighlightDirections.LEFT and pointRight

    def _MoveToRightSide(self, element, directive, cumLeft):
        width = self._GetElementWidth(element, directive)
        return cumLeft + width + 2

    def _MoveToLeftSide(self, cumLeft, pointerWidth):
        return cumLeft - pointerWidth + 2

    def _MoveToTop(self, pointToID, element, pointerWidth, pointerHeight):
        pointer = self.uiPointersByPointToID.get(pointToID, None)
        if pointer is None:
            currentPointerHeight = 0
        else:
            uiPointerElement = pointer.uiPointerElement
            currentPointerHeight = uiPointerElement.height
            if currentPointerHeight < 1:
                currentPointerHeight = pointerHeight
        newTop = element.absoluteTop - currentPointerHeight
        newLeft = element.absoluteLeft - pointerWidth / 2 + (element.absoluteRight - element.absoluteLeft) / 2
        if newLeft < 0:
            newLeft = 0
        elif newLeft + pointerWidth > uicore.desktop.width:
            newLeft = uicore.desktop.width - pointerWidth
        return (newTop, newLeft)

    def _MoveToBottom(self, element, directive, cumTop, height, pointerWidth, pointerHeight):
        newTop = cumTop + height / 2 + pointerHeight / 2
        if hasattr(element, 'absoluteLeft') and hasattr(element, 'absoluteRight'):
            newLeft = element.absoluteLeft - pointerWidth / 2 + (element.absoluteRight - element.absoluteLeft) / 2
        else:
            newLeft = element.parent.absoluteLeft + element.left - pointerWidth / 2
        if newLeft < 0:
            newLeft = 0
        elif newLeft + pointerWidth > uicore.desktop.width:
            newLeft = uicore.desktop.width - pointerWidth
        if directive == 'bracket':
            newTop -= 8
        return (newTop, newLeft)

    def _GetElementWidth(self, element, directive):
        if directive == 'neocom':
            neocom = sm.GetService('neocom').GetNeocomContainer()
            if neocom is not None:
                width = neocom.width
            else:
                width = element.width
                if width == 0:
                    width = element.absoluteRight - element.absoluteLeft
        else:
            width = element.width
            if width < 1:
                width = element.absoluteRight - element.absoluteLeft
        return width

    def GetEveMenuLocation(self, pointerHeight, pointerWidth):
        neocomIsLeftAligned = neocomSettings.neocom_align_setting.get() == uiconst.TOLEFT
        pointLeft = neocomIsLeftAligned
        pointUp = False
        pointDown = False
        eveMenuWidth, eveMenuHeight = self.neocomSvc.GetEveMenuButtonSize()
        cumTop = 0
        cumLeft = eveMenuWidth if neocomIsLeftAligned else uicore.desktop.width - eveMenuWidth - pointerWidth
        arrowPos = (eveMenuHeight - pointerHeight) / 2 if eveMenuHeight else 0
        return (cumTop,
         cumLeft,
         pointLeft,
         pointUp,
         pointDown,
         arrowPos)

    def CheckIsElementObscured(self, pointToID, top, left, pointLeft, element):
        globalLayer = uicore.layer.main
        abovemain = uicore.layer.abovemain
        candidates = self.GetObscureCandidates(globalLayer, element, False)
        candidates.extend(self.GetObscureCandidates(abovemain, element, True))
        left, top, width, height = element.GetAbsolute()
        elementPoints = []
        elementPoints.append(utillib.KeyVal(x=left, y=top))
        elementPoints.append(utillib.KeyVal(x=left, y=top + height))
        elementPoints.append(utillib.KeyVal(x=left + width, y=top))
        elementPoints.append(utillib.KeyVal(x=left + width, y=top + height))
        occluded = False
        occludors = []
        for candidate in candidates:
            absLeft, absTop, width, height = candidate.GetAbsolute()
            absRight = absLeft + width
            absBottom = absTop + height
            for point in elementPoints:
                if point.x > absLeft and point.x < absRight and point.y > absTop and point.y < absBottom:
                    occluded = True
                    occludors.append(candidate)
                    break

        self.UpdateObscurers(pointToID, occludors)
        return occluded

    def GetObscureCandidates(self, layer, pointToElement, topLayer):
        parentWindow = self.GetElementsParent(pointToElement)
        parentIdx = self.GetElementIdx(parentWindow)
        if parentIdx is None:
            return []
        list = []
        for window in layer.children:
            windowIdx = self.GetElementIdx(window)
            if windowIdx is None:
                return []
            if hasattr(window, 'name') and window.name not in ('UIPointer',
             'locationInfo',
             'snapIndicator',
             'windowhilite',
             parentWindow.name) and hasattr(window, 'state') and window.state != uiconst.UI_HIDDEN and hasattr(window, 'absoluteTop') and hasattr(window, 'absoluteBottom') and hasattr(window, 'absoluteRight') and hasattr(window, 'absoluteLeft'):
                if not topLayer and windowIdx < parentIdx:
                    list.append(window)
                elif topLayer:
                    list.append(window)

        return list

    def UpdateObscurers(self, pointToID, obscurers):
        oldObscurers = self.oldObscurers.get(pointToID, [])
        for window in oldObscurers:
            if window not in obscurers:
                window.opacity = 1.0

        for window in obscurers:
            window.opacity = 0.6

        self.oldObscurers[pointToID] = obscurers

    def ClearObscurers(self, pointToID):
        oldObscurers = self.oldObscurers.pop(pointToID, [])
        for window in oldObscurers:
            window.opacity = 1.0

    def GetElementIdx(self, element):
        if element.name == 'aura9':
            return 0
        parent = element.parent
        if not parent:
            return None
        elementIndex = 0
        for child in parent.children:
            if child == element:
                break
            elementIndex += 1

        return elementIndex

    def GetElementsParent(self, element):
        parentWindow = element
        while True:
            if not hasattr(parentWindow.parent, 'parent'):
                break
            elif not hasattr(parentWindow.parent.parent, 'parent'):
                break
            elif not hasattr(parentWindow.parent.parent.parent, 'parent'):
                break
            else:
                parentWindow = parentWindow.parent

        return parentWindow

    def FindElementToPointTo(self, elementUrl, shouldExcludeInvisible = False, blinkNeocom = True, findWindow = False):
        elementKeyVal = utillib.KeyVal(pointToElement=None)
        if not elementUrl:
            return elementKeyVal
        if isinstance(elementUrl, basestring):
            elementUrl = elementUrl.split('.')
        if len(elementUrl) == 1:
            elementName = elementUrl[0]
            if elementName in self.specialCasedPointers:
                return self.FindSpecialCasedElements(elementName)
            pointToElement = self.FindDeep(uicore.desktop, elementName, shouldExcludeInvisible)
        elif len(elementUrl) == 2 and elementUrl[0] == 'neocom':
            wndID = elementUrl[1]
            pointToElement = self._FindNeocomeElementToPointTo(elementUrl, findWindow)
            neocomSvc = sm.GetService('neocom')
            if not neocomSvc.IsButtonVisible(wndID) and blinkNeocom:
                neocomSvc.Blink(wndID)
        else:
            parent = uicore.desktop
            for path in elementUrl[:-1]:
                parent = self.FindDeep(parent, path, shouldExcludeInvisible)

            pointToElement = self.FindDeep(parent, elementUrl[-1], shouldExcludeInvisible)
        if isinstance(pointToElement, Window) and pointToElement.stacked:
            pointToElement = pointToElement.sr.tab
        elementKeyVal.pointToElement = pointToElement
        return elementKeyVal

    def _FindNeocomeElementToPointTo(self, elementUrl, findWindow = False):
        wndID = elementUrl[1]
        neocomSvc = sm.GetService('neocom')
        pointToElement, node = neocomSvc.GetUIObjectAndNodeByID(wndID)
        if findWindow and node:
            newPointToElement = self._FindPointToElmentFromNode(node)
            if newPointToElement:
                pointToElement = newPointToElement
        if pointToElement is None:
            pointToElement = neocomSvc.FindParentGroupBtn(wndID)
        if pointToElement is None:
            uniqueUiName = '.'.join(elementUrl)
            pointToElement = neocomSvc.GetUIObjectByUniqueUiName(uniqueUiName)
        if pointToElement:
            btnData = getattr(pointToElement, 'btnData', None)
            if neocomSvc.IsBtnInOverflowList(btnData):
                pointToElement = neocomSvc.GetNeocomContainer().overflowBtn
        return pointToElement

    def _FindPointToElmentFromNode(self, node):
        wndClass = getattr(node, 'wndCls', None)
        if not wndClass:
            return
        wnd = wndClass.GetIfOpen()
        if wnd and not wnd.destroyed and not wnd.IsMinimized() and wnd.IsVisible():
            if wnd.stacked:
                return wnd.stack
            else:
                return wnd

    def PointTo(self, basicData):
        self.LogInfo('PointTo', basicData.pointToID, basicData.uiPointerText, basicData.uiPointerTitle)
        if basicData.pointToID is None or basicData.pointToID == '':
            return
        self.uiElementsToHighlight.add(basicData.pointToID)
        if self.uiPointerUpdateThread is None:
            self.uiPointerUpdateThread = AutoTimer(20, self.UpdatePointers)
        uthread.new(self._PointToThread, basicData)
        sm.ScatterEvent('OnUiHighlightCreated', basicData.pointToID)

    def _PointToThread(self, basicData):
        while basicData.pointToID in self.uiElementsToHighlight and basicData.pointToID not in self.uiPointersByPointToID:
            self._PointToElementByID(basicData)
            blue.pyos.synchro.SleepWallclock(20)

    def StopPointingTo(self, pointToID):
        if pointToID not in self.uiElementsToHighlight:
            return
        self.uiElementsToHighlight.remove(pointToID)
        self.ClearPointer(pointToID)
        self.elementUrls.pop(pointToID, None)
        data = self.uiPointersByPointToID.pop(pointToID, None)
        if data and data.basicData.highlightContent:
            data.basicData.highlightContent.Close()
        sm.ScatterEvent('OnUiHighlightDeleted', pointToID)

    def IsAnyPointerActive(self):
        return bool(self.uiElementsToHighlight)

    def _GetConsiderationsForPointToElement(self, pointToID, pointToElement):
        considerations = None
        elementUrl = self.elementUrls.get(pointToID, None)
        if elementUrl and elementUrl[0] in ('neocom', pConst.UNIQUE_NAME_CLOCK_CALENDAR):
            considerations = 'neocom'
        elif elementUrl and elementUrl[0].replace(pConst.UNIQUE_UI_PREFIX, '') == 'eveMenuBtn':
            considerations = 'eveMenuBtn'
        parent = pointToElement
        while considerations is None and getattr(parent, 'parent', None) and hasattr(parent.parent, 'name'):
            parent = parent.parent
            if parent.name == 'shipui':
                considerations = 'shipui'
            elif parent.name == 'l_bracket':
                considerations = 'bracket'

        return considerations

    def _PointToElementByID(self, basicData):
        pointToID = basicData.pointToID
        if pointToID in self.uiPointersByPointToID:
            return
        self.elementUrls[pointToID] = pointToID.split('.')
        if not self.ShouldHidePointers():
            elementUrl = self.elementUrls.get(pointToID, None)
            pointToElement = None
            if basicData.shouldPrioritizeVisible:
                elementKeyVal = self.FindElementToPointTo(elementUrl, shouldExcludeInvisible=True)
                pointToElement = elementKeyVal.pointToElement if elementKeyVal else None
            if not pointToElement:
                elementKeyVal = self.FindElementToPointTo(elementUrl)
                pointToElement = elementKeyVal.pointToElement if elementKeyVal else None
            if pointToElement is not None and pointToElement.state != uiconst.UI_HIDDEN:
                considerations = self._GetConsiderationsForPointToElement(pointToID, pointToElement)
                locationData = self.GetLocation(basicData, pointToElement, considerations)
                cumTop, cumLeft, pointLeft, pointUp, pointDown, isObscured, arrowPos = locationData
                elementContainer = self.ConstructPointer(pointLeft, pointUp, pointDown, arrowPos, basicData, pointToElement)
                self.uiPointersByPointToID[pointToID] = UiPointerData(uiPointerElement=elementContainer, pointToElement=pointToElement, considerations=considerations, oldPointLeft=pointLeft, oldPointUp=pointUp, oldPointDown=pointDown, basicData=basicData)
                self._UpdatePointer(pointToID)
                self.statelogger.log_visible(pointToID)
            elif pointToElement is None:
                self.statelogger.log_element_not_found(pointToID)
            else:
                self.statelogger.log_element_invisible(pointToID)

    def ClearPointer(self, pointToID):
        pointer = self.uiPointersByPointToID.get(pointToID, None)
        if pointer is not None:
            element = pointer.uiPointerElement
            element.Close()
            if element in uicore.layer.hint.children:
                uicore.layer.hint.children.remove(element)
        self.ClearObscurers(pointToID)
        self.statelogger.clear_pointer(pointToID)

    def ClearPointers(self):
        for pointToID in self.uiElementsToHighlight.copy():
            self.StopPointingTo(pointToID)

        self.uiPointersByPointToID.clear()

    def RestartUiPointer(self, pointToID):
        pointer = self.uiPointersByPointToID.get(pointToID, None)
        if not pointer:
            return
        basicData = pointer.basicData
        self.StopPointingTo(pointToID)
        self.PointTo(basicData)

    def GetUiPointerClass(self, basicData):
        if basicData.highlightContent:
            return CustomUiPointer
        uiClass = basicData.uiClass
        if uiClass in UI_CLASS_BY_NAME:
            return UI_CLASS_BY_NAME[uiClass]
        return DEFAULT_UI_CLASS

    def ConstructPointer(self, pointLeft, pointUp, pointDown, arrowPosition, basicData, pointToElement):
        layer = uicore.layer.hint
        if basicData.audioSetting:
            uihighlightaudio.manager.play_highlight_appeared_sound()
        rectTop = 128
        if pointLeft:
            rectTop = 0
        defaultWidth = UIPOINTER_WIDTH
        defaultHeight = UIPOINTER_HEIGHT
        if pointUp or pointDown:
            defaultHeight -= POINTER_ARROW_WIDTH
        else:
            defaultWidth -= POINTER_ARROW_HEIGHT
        uiPointerClass = self.GetUiPointerClass(basicData)
        idx = basicData.idx if basicData.idx is not None else -1
        uiPointer = uiPointerClass(parent=layer, name='uiPointer', idx=idx, width=defaultWidth, height=defaultHeight, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, rectTop=rectTop, pointDirections=(pointUp, pointDown, pointLeft), arrowPositionModifier=arrowPosition, useArrowPointer=True, basicData=basicData, highlightContent=basicData.highlightContent, pointToElement=pointToElement)
        uiPointer.ConstructContent()
        return uiPointer

    def HidePointer(self, pointToID):
        pointer = self.uiPointersByPointToID.get(pointToID, None)
        if pointer is not None:
            self.statelogger.log_hidden(pointToID)
            pointer.uiPointerElement.Hide()

    def ShowPointer(self, pointToID):
        pointer = self.uiPointersByPointToID.get(pointToID, None)
        if pointer is not None:
            self.statelogger.log_visible(pointToID)
            pointer.uiPointerElement.Show()

    def _AddSpaceObjectTypeUiPointer(self, typeID, groupID, message, hint, audioSetting, localize = True, itemID = None, objectID = None, entityGroupID = None, showBox = True, highlightBracket = True):
        self.LogInfo('AddSpaceObjectTypeUiPointer', typeID, groupID, message, hint, localize, itemID, objectID)
        with self.spaceObjectPointerLock:
            if itemID is not None and itemID not in self.pointerUIByItemID:
                self.pointerDataByItemID[itemID] = SpaceObjectUiPointerData(None, None, itemID, message, hint, audioSetting, localize, showBox, highlightBracket)
            elif objectID is not None and objectID not in self.pointerDataByDungeonObjectID:
                self.pointerDataByDungeonObjectID[objectID] = SpaceObjectUiPointerData(None, None, None, message, hint, audioSetting, localize, showBox, highlightBracket)
            elif entityGroupID is not None and entityGroupID not in self.pointerDataByDungeonEntityGroupID:
                self.pointerDataByDungeonEntityGroupID[entityGroupID] = SpaceObjectUiPointerData(None, None, None, message, hint, audioSetting, localize, showBox, highlightBracket)
            elif typeID is not None and typeID not in self.pointerDataByTypeID:
                self.pointerDataByTypeID[typeID] = SpaceObjectUiPointerData(typeID, None, None, message, hint, audioSetting, localize, showBox, highlightBracket)
            elif groupID is not None and groupID not in self.pointerDataByByGroupID:
                self.pointerDataByByGroupID[groupID] = SpaceObjectUiPointerData(None, groupID, None, message, hint, audioSetting, localize, showBox, highlightBracket)
        self.RestartSpacePointers(clearPointers=False)

    def AddSpaceObjectTypeUiPointer(self, typeID, groupID, message, hint, audioSetting, localize = True, itemID = None, objectID = None, entityGroupID = None, showBox = True, highlightBracket = True):
        uthread.new(self._AddSpaceObjectTypeUiPointer, typeID, groupID, message, hint, audioSetting, localize=localize, itemID=itemID, objectID=objectID, entityGroupID=entityGroupID, showBox=showBox, highlightBracket=highlightBracket)

    def AddNextInRouteUiPointer(self, message, hint, audioSetting, showBox = True, highlightBracket = True):
        self.pointerDataNextInRoute = SpaceObjectUiPointerData(None, None, message, hint, audioSetting, False, showBox, highlightBracket)
        self.RestartSpacePointers(clearPointers=False)

    def RestartSpacePointers(self, clearPointers = False):
        self.KillSpacePointerUpdater()
        if clearPointers:
            for itemID in self.pointerUIByItemID.keys():
                self.FlushSpaceObjectPointer(itemID)

        self.StartPointerUpdater()

    def StartPointerUpdater(self):
        if self.spaceObjectUiPointerUpdater is None and any([bool(self.pointerDataByItemID),
         bool(self.pointerDataByTypeID),
         bool(self.pointerDataByByGroupID),
         bool(self.pointerDataByDungeonObjectID),
         bool(self.pointerDataByDungeonEntityGroupID)]):
            self.spaceObjectUiPointerUpdater = uthread.new(self.UpdateSpaceObjectUiPointersThread)

    def KillSpacePointerUpdater(self):
        if self.spaceObjectUiPointerUpdater is not None:
            self.spaceObjectUiPointerUpdater.kill()
            self.spaceObjectUiPointerUpdater = None

    def UpdateSpaceObjectUiPointersThread(self):
        blue.pyos.synchro.SleepWallclock(HINT_DISPLAY_DELAY_MS)
        while self.spaceObjectUiPointerUpdater is not None:
            if not self._UpdateSpaceObjectUiPointers():
                return
            blue.pyos.synchro.SleepWallclock(HINT_WORKER_DELAY_MS)

    def _UpdateSpaceObjectUiPointers(self):
        bp = self.michelle.GetBallpark()
        if bp is None:
            return False
        with self.spaceObjectPointerLock:
            self.CheckAddOrRemovePointers(bp)
        return True

    def CheckAddOrRemovePointers(self, bp):
        for slimItem in bp.slimItems.values():
            if slimItem.charID:
                continue
            elif slimItem.itemID in self.suppressedSpaceObjectUiPointers:
                continue
            data = self._GetPointerData(slimItem)
            if data is not None:
                if slimItem.itemID not in self.pointerUIByItemID:
                    self.pointerUIByItemID[slimItem.itemID] = SpaceObjectPointer(slimItem, data)
                    self.LogInfo('Creating UI Pointer for item', slimItem.itemID, 'of type', slimItem.typeID)
                    sm.ScatterEvent('OnItemHighlighted', slimItem.itemID, True)
            elif slimItem.itemID in self.pointerUIByItemID:
                self.FlushSpaceObjectPointer(slimItem.itemID)

    def _GetPointerData(self, slimItem):
        dunObjectID = getattr(slimItem, 'dunObjectID', None)
        dunObjectNameID = getattr(slimItem, 'dunObjectNameID', None)
        dunEntityGroupID = getattr(slimItem, 'entityGroupID', None)
        data = self.pointerDataByItemID.get(slimItem.itemID, None)
        if data is None and dunObjectID:
            data = self.pointerDataByDungeonObjectID.get(dunObjectID)
        if data is None:
            data = self.pointerDataByDungeonEntityGroupID.get(dunEntityGroupID)
        if data is None:
            data = self.pointerDataByTypeID.get(slimItem.typeID)
        if data is None:
            data = self.pointerDataByByGroupID.get(slimItem.groupID)
        if data is None and self.pointerDataNextInRoute and slimItem.itemID == sm.GetService('autoPilot').GetNextItemIDInRoute():
            data = self.pointerDataNextInRoute
        return data

    def _RemoveSpaceObjectUiPointers(self):
        self.KillSpacePointerUpdater()
        with self.spaceObjectPointerLock:
            self.pointerDataByItemID.clear()
            self.pointerDataByDungeonObjectID.clear()
            self.pointerDataByDungeonEntityGroupID.clear()
            self.pointerDataByTypeID.clear()
            self.pointerDataByByGroupID.clear()
            self.pointerDataNextInRoute = None
            self.suppressedSpaceObjectUiPointers.clear()
            for pointerID in self.pointerUIByItemID.keys():
                self.FlushSpaceObjectPointer(pointerID)

        self.LogInfo('Removing all space object pointers')

    def RemoveSpaceObjectUiPointers(self):
        uthread.new(self._RemoveSpaceObjectUiPointers)

    def _RemoveSpaceObjectUiPointersByAttribute(self, attributeName, attributeValue):
        self.KillSpacePointerUpdater()
        pointersByAttribute = {'itemID': self.pointerDataByItemID,
         'typeID': self.pointerDataByTypeID,
         'groupID': self.pointerDataByByGroupID,
         'dunObjectID': self.pointerDataByDungeonObjectID,
         'dunEntityGroupID': self.pointerDataByDungeonEntityGroupID}
        with self.spaceObjectPointerLock:
            allAttributePointers = pointersByAttribute[attributeName]
            pointersToRemove = []
            for pointer in allAttributePointers.values():
                attributeValueInPointer = getattr(pointer, attributeName, None)
                if attributeValueInPointer is not None and attributeValueInPointer == attributeValue:
                    pointersToRemove.append(pointer)

            if attributeValue in allAttributePointers:
                del allAttributePointers[attributeValue]
            for pointer in pointersToRemove:
                itemID = pointer.itemID
                self.FlushSpaceObjectPointer(itemID)
                if itemID in self.suppressedSpaceObjectUiPointers:
                    self.suppressedSpaceObjectUiPointers.remove(itemID)

        self._UpdateSpaceObjectUiPointers()
        self.StartPointerUpdater()

    def RemoveSpaceObjectUiPointersByItem(self, itemID):
        uthread.new(self._RemoveSpaceObjectUiPointersByAttribute, 'itemID', itemID)

    def RemoveSpaceObjectUiPointersByDungeonObject(self, objectID):
        uthread.new(self._RemoveSpaceObjectUiPointersByAttribute, 'dunObjectID', objectID)

    def RemoveSpaceObjectUiPointersByDungeonEntityGroup(self, entityGroupID):
        uthread.new(self._RemoveSpaceObjectUiPointersByAttribute, 'dunEntityGroupID', entityGroupID)

    def RemoveSpaceObjectUiPointersByType(self, typeID):
        uthread.new(self._RemoveSpaceObjectUiPointersByAttribute, 'typeID', typeID)

    def RemoveSpaceObjectUiPointersByGroup(self, groupID):
        uthread.new(self._RemoveSpaceObjectUiPointersByAttribute, 'groupID', groupID)

    def FlushSpaceObjectPointer(self, itemID):
        pointer = self.pointerUIByItemID.pop(itemID, None)
        if pointer is not None:
            pointer.Close()
            sm.ScatterEvent('OnItemHighlighted', itemID, False)

    def SuppressSpaceObjectPointer(self, itemID):
        self.suppressedSpaceObjectUiPointers.add(itemID)
        self.LogInfo('space object pointer for', itemID, 'was suppressed')
        self.FlushSpaceObjectPointer(itemID)

    @telemetry.ZONE_METHOD
    def DoBallsRemove(self, pythonBalls, isRelease):
        for ball, slimItem, terminal in pythonBalls:
            self.DoBallRemove(ball, slimItem, terminal)

    def DoBallRemove(self, ball, slimItem, terminal):
        self.FlushSpaceObjectPointer(slimItem.itemID)

    def OnInvItemDropEnded(self, name):
        if name:
            self.RestartUiPointer(name)

    def FindSpecialCasedElements(self, elementName):
        if elementName == pConst.UNIQUE_NAME_NEXT_IN_ROUTE:
            from eve.client.script.ui.inflight.overview.overviewWindowUtil import GetOverviewWndIfOpen
            overview = GetOverviewWndIfOpen()
            if not overview:
                return
            panel, direction = overview.GetNextInRouteNodeAndDirection()
            textList = None
            if direction == 'up':
                textList = [GetByLabel('UI/Overview/HelpPointerScrollUp')]
            elif direction == 'down':
                textList = [GetByLabel('UI/Overview/HelpPointerScrollDown')]
            return utillib.KeyVal(pointToElement=panel, extraTextLines=textList)
        helpPointer = sm.GetService('helpPointer')
        if elementName == pConst.UNIQUE_NAME_LOCAL_CHAT:
            return utillib.KeyVal(pointToElement=helpPointer.FindLocalChatWindow(elementName))
        if elementName == pConst.UNIQUE_NAME_CORP_CHAT:
            return utillib.KeyVal(pointToElement=helpPointer.FindCorpChatWindow(elementName))
        if elementName == pConst.UNIQUE_NAME_FLEET_CHAT:
            return utillib.KeyVal(pointToElement=helpPointer.FindFleetChatWindow(elementName))
        return utillib.KeyVal(pointToElement=None)
