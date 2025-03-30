#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\rangeSelector.py
from carbon.common.script.util.mathCommon import FloatCloseEnough
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.gridcontainer import GridContainer
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.themeColored import SpriteThemeColored, FillThemeColored
from carbonui.uicore import uicore
MAINSIDEMARGIN = 6
RANGECOLOR = (0.6,
 0.6,
 0.6,
 1)
OUTOFRANGECOLOR = (0.2,
 0.2,
 0.2,
 1)

class RangeSelector(Container):
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self._fixedFromProportion = None
        self._fixedToProportion = None
        self._minRange = None
        self._maxRange = None
        rangeParent = Container(parent=self, align=uiconst.TOTOP, height=attributes.barHeight or 9, padding=(MAINSIDEMARGIN,
         8,
         MAINSIDEMARGIN,
         0), state=uiconst.UI_NORMAL)
        rangeParent.OnMouseDown = (self.StartMoveRange, rangeParent)
        rangeParent.OnMouseUp = (self.StopMoveRange, rangeParent)
        rangeParent.OnMouseMove = (self.MoveRange, rangeParent)
        for name in ('from', 'to'):
            parent = Container(parent=rangeParent)
            rangeContainer = SizeCappedContainer(name='rangeContainer', parent=parent, align=uiconst.TOLEFT_PROP)
            rangeContainer._background = FillThemeColored(bgParent=rangeContainer, opacity=0.8)
            rangeContainer._pointer = SpriteThemeColored(parent=rangeContainer, align=uiconst.TOPRIGHT, pos=(-8, -7, 16, 16))
            setattr(self, '_' + name + 'Range', rangeContainer)
            configName = '_' + name + 'Handle'
            handle = Container(parent=self, name=configName, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, pos=(0,
             0,
             MAINSIDEMARGIN * 2,
             32), idx=0)
            handle.OnMouseDown = (self.StartMoveHandle, handle)
            handle.OnMouseUp = (self.StopMoveHandle, handle)
            handle.OnMouseMove = (self.MoveHandle, handle)
            setattr(self, configName, handle)

        self._background = FillThemeColored(name='backgroundFill', bgParent=rangeParent, opacity=0.8)
        self._incrementsParent = Container(parent=self, align=uiconst.TOTOP, height=16, padding=(MAINSIDEMARGIN,
         2,
         MAINSIDEMARGIN,
         0), name='_incrementsParent')
        self._increments = None
        self._callbackData = None
        self._fromProportion = attributes.fromProportion or 0.0
        self._toProportion = attributes.toProportion or 1.0
        self._canInvert = bool(attributes.canInvert)
        self.height = 48
        self.UpdateRanges()
        self.UpdateHandles()
        self.OnIncrementChange = attributes.OnIncrementChange
        self.OnChange = attributes.OnChange
        self.OnEndDragChange = attributes.OnEndDragChange

    def StartMoveHandle(self, handle, btn):
        l, t, w, h = handle.GetAbsolute()
        handle.grab = (uicore.uilib.x - l, uicore.uilib.y - t)

    def StopMoveHandle(self, handle, btn):
        self._EnforceMaxRange(handle)
        handle.grab = None
        if self._increments and (self._fromProportion == self._toProportion or self._toProportion == 0 and self._fromProportion == 1.0):
            if handle is self._toHandle:
                for increment, incrementData in self._increments:
                    if increment - self._minRange >= self._toProportion:
                        self._toProportion = increment
                        self.UpdateRanges()
                        self.UpdateHandles()
                        self._DoOnChangeCallback(onEndDrag=True)
                        return

                self._toProportion = self._increments[1][0]
                self.UpdateRanges()
                self.UpdateHandles()
                self._DoOnChangeCallback(onEndDrag=True)
                return
            if handle is self._fromHandle:
                for increment, incrementData in reversed(self._increments):
                    if increment + self._minRange <= self._fromProportion:
                        self._fromProportion = increment
                        self.UpdateRanges()
                        self.UpdateHandles()
                        self._DoOnChangeCallback(onEndDrag=True)
                        return

                self._fromProportion = self._increments[-2][0]
                self.UpdateRanges()
                self.UpdateHandles()
                self._DoOnChangeCallback(onEndDrag=True)
                return
        if self.OnEndDragChange:
            self._DoOnChangeCallback(onEndDrag=True)

    def _EnforceMaxRange(self, handle):
        if not self._increments or self._maxRange is None:
            return
        if not self.IsOverMaxRange(self._fromProportion, self._toProportion):
            return
        if handle is self._toHandle:
            nextIncrements = self.GetNextIncrements(self._toProportion, 'toHandle')
            for prop in nextIncrements:
                if not self.IsOverMaxRange(self._fromProportion, prop):
                    self._toProportion = prop
                    break

        elif handle is self._fromHandle:
            nextIncrements = self.GetNextIncrements(self._fromProportion, 'fromHandle')
            for prop in nextIncrements:
                if not self.IsOverMaxRange(prop, self._toProportion):
                    self._fromProportion = prop
                    break

        self.UpdateRanges()
        self.UpdateHandles()

    def GetNextIncrements(self, prop, handleName):
        lowerThanProp = []
        higherThanProp = []
        for increment, _ in self._increments:
            if increment >= prop:
                higherThanProp.append(increment)
            else:
                lowerThanProp.append(increment)

        if handleName == 'fromHandle':
            return higherThanProp + lowerThanProp
        else:
            lowerThanProp.reverse()
            higherThanProp.reverse()
            return lowerThanProp + higherThanProp

    def IsOverMaxRange(self, fromProp, toProp):
        if self._maxRange is None:
            return False
        adjustedToProp = self.GetAdjustedToProporations(fromProp, toProp)
        rangeProp = adjustedToProp - fromProp
        if FloatCloseEnough(rangeProp, self._maxRange):
            return False
        return rangeProp > self._maxRange

    def GetAdjustedToProporations(self, fromProp, toProp):
        if fromProp > toProp:
            return toProp + 1.0
        return toProp

    def MoveHandle(self, handle, *args):
        if getattr(handle, 'grab', None):
            x, y = handle.grab
            l, t, w, h = handle.parent.GetAbsolute()
            handle.left = pos = min(w - handle.width, max(0, uicore.uilib.x - x - l))
            r = w - handle.width
            proportion = pos / float(r)
            incrementData = None
            closest = self.RoundToIncrement(proportion)
            if closest is not None:
                proportion = closest
            if not self._canInvert:
                if handle is self._fromHandle:
                    self._fromProportion = min(proportion, self._toProportion)
                if handle is self._toHandle:
                    self._toProportion = max(proportion, self._fromProportion)
            else:
                if handle is self._fromHandle:
                    self._fromProportion = proportion
                if handle is self._toHandle:
                    self._toProportion = proportion
            self.UpdateRanges()
            self.UpdateHandles()
            self._DoOnChangeCallback()

    def StartMoveRange(self, rangeParent, btn):
        l, t, w, h = rangeParent.GetAbsolute()
        rangeParent.startProportion = ((uicore.uilib.x - l) / float(w), self._fromProportion, self._toProportion)

    def StopMoveRange(self, rangeParent, btn):
        rangeParent.startProportion = None
        if self.OnEndDragChange:
            self._DoOnChangeCallback(onEndDrag=True)

    def MoveRange(self, rangeParent, *args):
        if getattr(rangeParent, 'startProportion', None):
            l, t, w, h = rangeParent.GetAbsolute()
            newProportion = (uicore.uilib.x - l) / float(w)
            startProportion, fromProportion, toProportion = rangeParent.startProportion
            diff = newProportion - startProportion
            if fromProportion > toProportion:
                if diff < 0:
                    self._toProportion = max(0.0, toProportion + diff)
                    self._fromProportion = self._toProportion + (fromProportion - toProportion)
                else:
                    self._fromProportion = min(1.0, fromProportion + diff)
                    self._toProportion = self._fromProportion - (fromProportion - toProportion)
            elif diff < 0:
                self._fromProportion = max(0.0, fromProportion + diff)
                self._toProportion = self._fromProportion + (toProportion - fromProportion)
            else:
                self._toProportion = min(1.0, toProportion + diff)
                self._fromProportion = self._toProportion - (toProportion - fromProportion)
            closest = self.RoundToIncrement(self._fromProportion)
            if closest is not None:
                self._fromProportion = closest
            closest = self.RoundToIncrement(self._toProportion)
            if closest is not None:
                self._toProportion = closest
            self.UpdateRanges()
            self.UpdateHandles()
            self._DoOnChangeCallback()

    def SetMinRange(self, minRange):
        self._minRange = minRange
        self.UpdateRanges()
        self.UpdateHandles()

    def SetMaxRange(self, maxRange):
        isChanging = self._maxRange != maxRange
        self._maxRange = maxRange
        self._EnforceMaxRange(self._toHandle)
        self.UpdateRanges()
        self.UpdateHandles()
        if isChanging:
            self._DoOnChangeCallback(True)

    def SetFixedRange(self, fixedFromProportion = None, fixedToProportion = None):
        self._fixedFromProportion = fixedFromProportion
        if fixedFromProportion is not None:
            self._fromProportion = fixedFromProportion
            self._fromHandle.display = False
            self._fromRange._pointer.display = False
        else:
            self._fromHandle.display = True
            self._fromRange._pointer.display = True
        self._fixedToProportion = fixedToProportion
        if fixedToProportion is not None:
            self._toProportion = fixedToProportion
            self._toHandle.display = False
            self._toRange._pointer.display = False
        else:
            self._toHandle.display = True
            self._toRange._pointer.display = True
        self.UpdateRanges()
        self.UpdateHandles()

    def SetIncrements(self, increments):
        self._incrementsParent.Flush()
        maxMarkerSize = 0
        labels = []
        self._increments = []
        if increments:
            last = increments.pop(-1)
            stepSize = 1.0 / len(increments)
            c = GridContainer(parent=self._incrementsParent, lines=1, columns=len(increments))
            i = 0
            for incrementData in increments:
                label = incrementData[0]
                markerSize = incrementData[1]
                inc = Container(parent=c, align=uiconst.TOALL)
                if markerSize:
                    maxMarkerSize = max(maxMarkerSize, markerSize)
                    Line(parent=inc, align=uiconst.TOPLEFT, width=1, height=markerSize)
                    self._increments.append((i * stepSize, incrementData))
                if label:
                    if label.startswith('res:'):
                        s = Sprite(parent=inc, texturePath=label, width=16, height=16, align=uiconst.CENTER, idx=0, top=-2, color=(1, 1, 1, 0.7))
                        labels.append(s)
                    else:
                        l = eveLabel.EveLabelSmall(parent=inc, text=label, left=-MAINSIDEMARGIN)
                        if i == 0:
                            l.left = max(-MAINSIDEMARGIN, -l.textwidth / 2)
                        else:
                            l.left = -l.textwidth / 2
                        labels.append(l)
                i += 1

            label = last[0]
            markerSize = last[1]
            inc = Container(parent=self._incrementsParent, align=uiconst.TORIGHT, width=1, idx=0)
            if markerSize:
                maxMarkerSize = max(maxMarkerSize, markerSize)
                Line(parent=inc, align=uiconst.TOPLEFT, width=1, height=markerSize)
                self._increments.append((i * stepSize, last))
            if label:
                if label.startswith('res:'):
                    s = Sprite(parent=inc, texturePath=label, width=16, height=16, align=uiconst.CENTER, idx=0, top=-2, color=(1, 1, 1, 0.7))
                    labels.append(s)
                else:
                    l = eveLabel.EveLabelSmall(parent=inc, text=label, align=uiconst.TOPRIGHT)
                    l.left = max(-MAINSIDEMARGIN, -l.textwidth / 2)
                    labels.append(l)
        self._EnforceMaxRange(self._toHandle)
        maxHeight = 0
        for l in labels:
            l.top += maxMarkerSize
            maxHeight = max(l.top + l.height, maxHeight)

        self._incrementsParent.height = maxHeight
        self.height = sum([ each.height + each.padTop + each.padBottom for each in self.children if each.align == uiconst.TOTOP ])

    def RoundToIncrement(self, proportion, getIncrementData = False):
        closest = None
        closestDiff = None
        closestData = None
        if self._increments:
            for increment, incrementData in self._increments:
                diff = abs(proportion - increment)
                if closestDiff is None or diff < closestDiff:
                    closest = increment
                    closestDiff = diff
                    closestData = incrementData

        if getIncrementData:
            return (closest, closestData)
        return closest

    def UpdateRanges(self):
        if self._fixedFromProportion is not None:
            fromProportion = self._fixedFromProportion
        else:
            fromProportion = self._fromProportion
        if self._fixedToProportion is not None:
            toProportion = self._fixedToProportion
        else:
            toProportion = self._toProportion
        self._fromRange.width = fromProportion
        self._toRange.width = toProportion
        if fromProportion > toProportion:
            self._toRange.parent.SetOrder(0)
            self._toRange._background.SetColorType(uiconst.COLORTYPE_UIHILIGHT)
            self._toRange._pointer.LoadTexture('res:/UI/Texture/classes/RangeSelector/rightPointer.png')
            self._toRange._pointer.top = -7
            self._fromRange._background.SetColorType(uiconst.COLORTYPE_UIBASECONTRAST)
            self._fromRange._pointer.LoadTexture('res:/UI/Texture/classes/RangeSelector/leftPointerDown.png')
            self._fromRange._pointer.top = 0
            self._background.SetColorType(uiconst.COLORTYPE_UIHILIGHT)
        else:
            self._fromRange.parent.SetOrder(0)
            self._fromRange._background.SetColorType(uiconst.COLORTYPE_UIBASECONTRAST)
            self._fromRange._pointer.LoadTexture('res:/UI/Texture/classes/RangeSelector/leftPointer.png')
            self._fromRange._pointer.top = -7
            self._toRange._background.SetColorType(uiconst.COLORTYPE_UIHILIGHT)
            self._toRange._pointer.LoadTexture('res:/UI/Texture/classes/RangeSelector/rightPointerDown.png')
            self._toRange._pointer.top = 0
            self._background.SetColorType(uiconst.COLORTYPE_UIBASECONTRAST)

    def UpdateHandles(self):
        l, t, w, h = self.GetAbsolute()
        r = w - self._fromHandle.width
        if self._fixedFromProportion is not None:
            fromProportion = self._fixedFromProportion
        else:
            fromProportion = self._fromProportion
        if self._fixedToProportion is not None:
            toProportion = self._fixedToProportion
        else:
            toProportion = self._toProportion
        self._fromHandle.left = int(r * fromProportion)
        self._toHandle.left = int(r * toProportion)

    def _DoOnChangeCallback(self, onEndDrag = False):
        if self._callbackData != (self._fromProportion, self._toProportion):
            if self.OnChange:
                self.OnChange(self._fromProportion, self._toProportion)
            if self.OnIncrementChange:
                fromIncr, fromData = self.RoundToIncrement(self._fromProportion, getIncrementData=True)
                toIncr, toData = self.RoundToIncrement(self._toProportion, getIncrementData=True)
                self.OnIncrementChange(self, fromData, toData, fromIncr, toIncr)
            self._callbackData = (self._fromProportion, self._toProportion)
        if onEndDrag and self.OnEndDragChange:
            fromIncr, fromData = self.RoundToIncrement(self._fromProportion, getIncrementData=True)
            toIncr, toData = self.RoundToIncrement(self._toProportion, getIncrementData=True)
            self.OnEndDragChange(self, fromData, toData, fromIncr, toIncr)

    def _OnSizeChange_NoBlock(self, *args):
        self.UpdateHandles()


class SizeCappedContainer(Container):

    @apply
    def displayRect():
        fget = Container.displayRect.fget

        def fset(self, value):
            Container.displayRect.fset(self, value)
            ro = self.renderObject
            if ro:
                ro.displayWidth = max(0.0001, self._displayWidth)
                ro.displayHeight = max(0.0001, self._displayHeight)

        return property(**locals())

    @apply
    def displayWidth():
        fget = Container.displayWidth.fget

        def fset(self, value):
            Container.displayWidth.fset(self, value)
            ro = self.renderObject
            if ro:
                ro.displayWidth = max(0.0001, self._displayWidth)

        return property(**locals())

    @apply
    def displayHeight():
        fget = Container.displayHeight.fget

        def fset(self, value):
            Container.displayHeight.fset(self, value)
            ro = self.renderObject
            if ro:
                ro.displayHeight = max(0.0001, self._displayHeight)

        return property(**locals())
