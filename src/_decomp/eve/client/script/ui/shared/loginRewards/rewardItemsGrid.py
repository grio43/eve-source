#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\loginRewards\rewardItemsGrid.py
import itertoolsext
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui import uiconst
from carbonui.uianimations import animations
from eve.client.script.ui.shared.loginRewards.rewardUiConst import SCROLL_ANIMATION
import mathext

class RewardItemsGrid(LayoutGrid):
    default_name = 'rewardGrid'

    def ApplyAttributes(self, attributes):
        self.panelConst = attributes.panelConst
        self.isScrolling = False
        self.numAllEntries = attributes.numAllEntries
        self.entries = {}
        self.cells = {}
        self.selectedIdx = 0
        self.offset = attributes.offset or 0
        LayoutGrid.ApplyAttributes(self, attributes)

    def SetGridPosition(self, newPosValue, animateTime = SCROLL_ANIMATION):
        allEntriesWidth = self.numAllEntries * self.panelConst.ENTRY_WIDTH
        if newPosValue > self.GetMinPosValue() or newPosValue < -allEntriesWidth:
            self._StopScrolling()
            return False
        if animateTime:
            animations.MorphScalar(self, 'left', startVal=self.left, endVal=newPosValue, duration=animateTime, curveType=uiconst.ANIM_SMOOTH, callback=self._StopScrolling)
        else:
            self.left = newPosValue
            self._StopScrolling()
        return True

    def GetMinPosValue(self):
        return 10 + self.offset

    def IsScrolling(self):
        return self.isScrolling

    def _StopScrolling(self, *args):
        self.isScrolling = False

    def GoToSelectedEntry(self, entryIdx, animateTime = SCROLL_ANIMATION, *args):
        if self.isScrolling:
            return
        self.isScrolling = True
        newEntryIdx = max(0, entryIdx - self.panelConst.SELECTED_CELL)
        return self.GoToEntry(newEntryIdx, animateTime=animateTime)

    def OnBrowse(self, direction, currentFirstVisibleEntry, *args):
        if self.isScrolling:
            return
        self.isScrolling = True
        newIdx = direction + currentFirstVisibleEntry
        return self.GoToEntry(newIdx)

    def GoToEntry(self, entryIdx, animateTime = SCROLL_ANIMATION):
        if self.AreEntriesFewerThanMaxVisible():
            self.align = uiconst.CENTER
            self._StopScrolling()
            return
        self.align = uiconst.CENTERLEFT
        newEntryIdx = mathext.clamp(entryIdx, 0, self.numAllEntries - self.panelConst.NUM_VISIBLE_ITEMS)
        cellAtIdx = self.cells.get(newEntryIdx, None)
        if not cellAtIdx:
            self._StopScrolling()
            return
        numLowerIdx = itertoolsext.count((i for i in self.cells.iterkeys() if i < newEntryIdx))
        newValue = -numLowerIdx * self.panelConst.ENTRY_WIDTH + self.offset
        moved = self.SetGridPosition(newValue, animateTime=animateTime)
        if moved:
            return newEntryIdx

    def AreEntriesFewerThanMaxVisible(self):
        return self.numAllEntries < self.panelConst.NUM_VISIBLE_ITEMS

    def GetEntriesWidth(self):
        return len(self.entries) * self.panelConst.ENTRY_WIDTH

    def GetNumEntries(self):
        return self.numAllEntries

    def LoadEntries(self, entryInfo):
        self.entries.clear()
        self.cells.clear()
        self._LoadEntries(entryInfo)

    def _LoadEntries(self, entryInfo):
        for i, info in enumerate(entryInfo):
            entryClass = info['entryClass']
            entry = entryClass(**info)
            c = self.AddCell(cellObject=entry)
            self.entries[i] = entry
            self.cells[i] = c

    def GetEntry(self, entryNum):
        return self.entries.get(entryNum, None)

    def SetEntryAsSelected(self, entryNum, withTransition = False):
        animateTime = 0.75 if withTransition else 0
        for eIdx, entry in self.entries.iteritems():
            entry.SetSelectedState(eIdx == entryNum, animateTime)

    def UpdateEntryState(self, selectedIdx, updateKeyVal):
        for eIdx, entry in self.entries.iteritems():
            entry.UpdateEntryState(eIdx, selectedIdx, updateKeyVal)


class RewardItemsGridCycle(RewardItemsGrid):

    def ApplyAttributes(self, attributes):
        panelConst = attributes.panelConst
        attributes.columns += panelConst.NUM_VISIBLE_ITEMS + panelConst.SELECTED_CELL
        attributes.numAllEntries += panelConst.NUM_VISIBLE_ITEMS + panelConst.SELECTED_CELL
        RewardItemsGrid.ApplyAttributes(self, attributes)

    def _GetMaxDay(self):
        return self.numAllEntries

    def _LoadEntries(self, entryInfo):
        minIdx = min(self.entries) if self.entries else 0
        for eachInfo in reversed(entryInfo):
            if len(self.entries) >= self.panelConst.SELECTED_CELL:
                break
            entryClass = eachInfo['entryClass']
            entry = entryClass(**eachInfo)
            c = self.AddCell(cellObject=entry)
            minIdx -= 1
            self.entries[minIdx] = entry
            self.cells[minIdx] = c

        RewardItemsGrid._LoadEntries(self, entryInfo)
        maxIdx = max(self.entries) if self.entries else 0
        for eachInfo in entryInfo:
            entryClass = eachInfo['entryClass']
            entry = entryClass(**eachInfo)
            c = self.AddCell(cellObject=entry)
            maxIdx += 1
            self.entries[maxIdx] = entry
            self.cells[maxIdx] = c
            if len(self.entries) >= self.numAllEntries:
                break


class DayGrid(RewardItemsGrid):
    default_name = 'dayGrid'

    def LoadEntries(self, entryInfo):
        self.entries.clear()
        self.cells.clear()
        self._LoadEntries(entryInfo)

    def _LoadEntries(self, entryInfo):
        for i, info in enumerate(entryInfo):
            entryClass = info['entryClass']
            entry = entryClass(**info)
            c = self.AddCell(cellObject=entry)
            self.entries[i] = entry
            self.cells[i] = c

    def SetDayEntryAsSelected(self, entryNum, withTransition = False):
        animateTime = 0.75 if withTransition else 0
        for eIdx, entry in self.entries.iteritems():
            entry.SetDaySelectedState(eIdx == entryNum, animateTime)

    def UpdateEntryState(self, selectedIdx, updateKeyVal):
        for eIdx, entry in self.entries.iteritems():
            entry.UpdateEntryState(eIdx, selectedIdx, updateKeyVal)
