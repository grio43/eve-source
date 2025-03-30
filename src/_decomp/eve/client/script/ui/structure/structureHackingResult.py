#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\structureHackingResult.py
import carbonui.uiconst as uiconst
import trinity
import uthread
from carbon.common.script.util.commonutils import StripTags
from carbon.common.script.util.format import FmtDate
from carbonui.primitives.container import Container
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import StreamingVideoSprite
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import Label
from carbonui.control.window import Window
from carbonui.uicore import uicore
from eve.client.script.ui.hacking.hackingUIConst import COLOR_WINDOW_BG
from eve.client.script.ui.structure.structureBrowser.controllers.reinforceTimersBundle import GetHourText
from localization import GetByLabel
from menu import MenuLabel
import random
import blue
HOUR_LABEL = GetByLabel('UI/Structures/ReinforcementHour')
NEW_HOUR_LABEL = GetByLabel('UI/Structures/NewReinforcementHour')
NEW_HOUR_SHORT_LABEL = GetByLabel('UI/Structures/NewReinforcementHourShort')

class StructureHackingResultWnd(Window):
    default_name = 'structureHackingResultWnd'
    default_windowID = 'structureHackingResultWnd'
    default_width = 898
    default_height = 631
    default_fixedWidth = default_width
    default_fixedHeight = default_height
    default_isCollapseable = False
    default_captionLabelPath = 'UI/Structures/StructureHackingResults'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.SetMinSize([350, 270])
        innerMain = Container(name='innerMain', parent=self.sr.main, aling=uiconst.TOALL, padding=10)
        self.centerCont = Container(name='centerCont', parent=innerMain, align=uiconst.CENTER, pos=(0, 0, 1, 1))
        self.labelLayoutGrid = LayoutGrid(parent=self.centerCont, margin=0, cellSpacing=(20, 0), columns=2, align=uiconst.CENTERLEFT)
        self.backgroundVideo = StreamingVideoSprite(bgParent=innerMain, videoPath='res:/video/hacking/bgLoop_alpha.webm', videoLoop=True, spriteEffect=trinity.TR2_SFX_COPY, color=COLOR_WINDOW_BG)
        self.resultLabelHour = self.GetLabel(name='resultLabelHour', align=uiconst.CENTERRIGHT, text=HOUR_LABEL)
        self.resultLabelHourValue = self.GetLabel(name='resultLabelHourValue', align=uiconst.CENTERLEFT)
        self.labelLayoutGrid.AddCell(cellObject=Container(pos=(0, 0, 0, 20), align=uiconst.TOPLEFT), colSpan=2)
        self.resultLabelNextHour = self.GetLabel(name='resultLabelNextHour', align=uiconst.CENTERRIGHT, fontsize=20)
        self.resultLabelNextHourValue = self.GetLabel(name='resultLabelNextHourValue', align=uiconst.CENTERLEFT, fontsize=20)
        self.takesEffectLabel = self.GetLabel(name='takesEffect', align=uiconst.CENTERRIGHT, text=GetByLabel('UI/StructureBrowser/TakesEffect'), fontsize=20)
        self.takesEffectLabelValue = self.GetLabel(name='takesEffectLabelValue', align=uiconst.CENTERLEFT, text='', fontsize=20)
        self.allLabels = [self.resultLabelHour,
         self.resultLabelHourValue,
         self.takesEffectLabel,
         self.takesEffectLabelValue,
         self.resultLabelNextHour,
         self.resultLabelNextHourValue]
        self.leftWidth = self._GetTextWidth(self.resultLabelHour) + 20
        self.structureID = attributes.structureID
        self.structureTypeID = attributes.structureTypeID
        self.reinforceTimers = attributes.reinforceTimers
        if self.structureID and self.reinforceTimers:
            self.LoadWndWithResult(self.structureID, self.reinforceTimers, self.structureTypeID)

    def GetLabel(self, name, align, text = '', fontsize = 30):
        label = Label(name=name, parent=self.labelLayoutGrid, align=align, text=text, bold=True, fontsize=fontsize, idx=0, color=Color.WHITE)
        label.SetAlpha(0.75)
        return label

    def _GetTextWidth(self, label, text = None):
        if text == None:
            text = label.text
        return uicore.font.GetTextWidth('<b>%s</b>' % text, label.fontsize)

    def LoadWndWithResult(self, structureID, reinforceTimers, structureTypeID):
        self.structureID = structureID
        self.structureTypeID = structureTypeID
        self.reinforceTimers = reinforceTimers
        uicore.animations.FadeTo(self, 0, 1.0)
        textHour = GetByLabel('UI/Structures/ReinforcementHour')
        self.resultLabelHour.text = textHour
        uthread.new(self.AnimateResults_thread, reinforceTimers)
        self.SetWindowPosition()

    def AnimateResults_thread(self, reinforceTimers):
        resultHour = reinforceTimers.GetReinforceHour()
        hourText = GetHourText(resultHour)
        totalWidth = self.leftWidth
        self.labelLayoutGrid.left = int(-totalWidth / 2)
        isThereNewHour = self.IsNewHour(reinforceTimers, resultHour)
        for each in self.allLabels:
            each.display = False

        self.resultLabelNextHour.text = ' ' if isThereNewHour else ''
        self._AdjustTextLocation(reinforceTimers, isThereNewHour, hourText)
        allLetters = GetByLabel('UI/Structures/AllLetters')
        self.resultLabelHour.display = True
        self._AnimateTime(hourText, self.resultLabelHourValue)
        applyNext = reinforceTimers.GetNextApply()
        if applyNext:
            resultNextHour = reinforceTimers.GetNextReinforceHour()
            nextHourText = GetHourText(resultNextHour)
            if isThereNewHour:
                self.resultLabelNextHour.display = True
                text = NEW_HOUR_LABEL
                self.resultLabelNextHour.text = text
                self._AnimateTime(nextHourText, self.resultLabelNextHourValue)
            self.takesEffectLabel.display = True
            dateText = FmtDate(applyNext, 'ls')
            self._AnimateWord(dateText, self.takesEffectLabelValue, allLetters='0123456789', sleep=30)

    def IsNewHour(self, reinforceTimers, currentHour):
        resultNextHour = reinforceTimers.GetNextReinforceHour()
        return currentHour != resultNextHour

    def _AdjustTextLocation(self, reinforceTimers, isThereNewHour, hourText):
        leftTextWidths = [self._GetTextWidth(self.resultLabelHour)]
        if isThereNewHour:
            leftTextWidths.append(self._GetTextWidth(self.resultLabelNextHour, text=NEW_HOUR_LABEL))
        leftWidth = max(leftTextWidths)
        rightTextWidths = [0]
        applyNext = reinforceTimers.GetNextApply()
        if applyNext:
            dateText = FmtDate(applyNext, 'ls')
            rightTextWidths.append(self._GetTextWidth(self.takesEffectLabelValue, text=dateText))
        rightWidth = max(rightTextWidths)
        totalWidth = leftWidth + rightWidth + 20
        self.labelLayoutGrid.left = int(-totalWidth / 2)

    def _AnimateWord(self, dayName, dayLabel, allLetters, sleep = 50):
        dayLabel.display = True
        lenDayName = len(dayName)
        for x in xrange(lenDayName * 2):
            current = x / 2
            dayRandomText = dayName[:current]
            for _ in xrange(lenDayName - current):
                nextChar = random.choice(allLetters)
                if x == 0:
                    nextChar = nextChar.upper()
                dayRandomText += nextChar
                dayLabel.text = dayRandomText

            blue.synchro.SleepWallclock(sleep)

        dayLabel.text = dayName

    def _AnimateTime(self, hourText, hourLabel):
        hourLabel.display = True
        for _ in xrange(5):
            h = random.randint(0, 23)
            m = random.randint(0, 59)
            timeText = '%.2d:%.2d' % (h, m)
            hourLabel.text = timeText
            blue.synchro.SleepWallclock(100)
            hourLabel.text = hourText

    def _GetWindowPosition(self):
        windowSizesAndPositions = settings.char.windows.Get('windowSizesAndPositions_1', {}).get('HackingWindow')
        if windowSizesAndPositions:
            return windowSizesAndPositions[:2]
        dw, dh = uicore.desktop.width, uicore.desktop.height
        return ((dw - self.width) / 2, (dh - self.height) / 2)

    def PostApplyAttributes(self, attributes):
        Window.PostApplyAttributes(self, attributes)
        self.SetWindowPosition()

    def SetWindowPosition(self):
        l, t = self._GetWindowPosition()
        self.left = l
        self.top = t

    def GetMenu(self, *args):
        m = [(MenuLabel('UI/Fitting/FittingWindow/FittingManagement/ExportToClipboard'), self.CopyToClipboard)]
        m += Window.GetMenu(self, *args)
        return m

    def CopyToClipboard(self, *args):
        resultHour = self.reinforceTimers.GetReinforceHour()
        hourText = GetHourText(resultHour)
        structureInfo = sm.GetService('structureDirectory').GetStructureInfo(self.structureID)
        results = [structureInfo.itemName, '%s\t%s' % (HOUR_LABEL, hourText)]
        applyNext = self.reinforceTimers.GetNextApply()
        if applyNext:
            resultNextHour = self.reinforceTimers.GetNextReinforceHour()
            nextHourText = GetHourText(resultNextHour)
            effectText = GetByLabel('UI/StructureBrowser/TakesEffect')
            dateText = FmtDate(applyNext, 'ls')
            results += ['%s\t%s' % (NEW_HOUR_LABEL, nextHourText), '%s\t%s' % (effectText, dateText)]
        resultText = '\n'.join(results)
        strippedText = StripTags(resultText)
        if strippedText:
            blue.pyos.SetClipboardData(strippedText)
