#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\war\landingPageCont.py
import itertools
import carbonui
import uthread
from carbonui import TextColor
from menu import MenuLabel
from carbon.common.script.util.commonutils import StripTags
from carbonui.primitives.containerAutoSize import ContainerAutoSize
import carbonui.const as uiconst
from eve.client.script.ui.control.infoIcon import QuestionMarkGlyphIcon
import blue

class LandingPageCont(ContainerAutoSize):
    default_align = uiconst.TOTOP
    default_alignMode = uiconst.TOTOP
    default_state = uiconst.UI_NORMAL
    default_minHeight = 30
    default_padTop = 32

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.showLoading = True
        self.headerText = attributes.headerText
        self.text = attributes.text
        self.tooltipText = attributes.tooltipText
        padLeft = 36
        dIcon = QuestionMarkGlyphIcon(name='moreIcon', parent=self, align=uiconst.TOPLEFT, left=4, top=4, hint=self.tooltipText)
        dIcon.LoadTooltipPanel = self.LoadDescriptionTooltipPanel
        dIcon.GetTooltipPointer = self.LoadDescriptionTooltipPointer
        dIcon.GetMenu = self.GetDescriptionIconMenu
        carbonui.TextHeader(text=self.headerText, parent=self, align=uiconst.TOTOP, padLeft=padLeft, color=TextColor.HIGHLIGHT)
        carbonui.TextBody(text=self.text, parent=self, align=uiconst.TOTOP, padding=(padLeft,
         2,
         0,
         0))
        self.currentStatus = carbonui.TextBody(text='', parent=self, align=uiconst.TOTOP, padLeft=padLeft, padRight=0, state=uiconst.UI_NORMAL)
        self.currentStatus.CopyText = self.CopyText
        uthread.new(self.LoadingUpdate_thread)

    def LoadingUpdate_thread(self):
        i = itertools.cycle(('.', '..', '...'))
        while self.showLoading and not self.destroyed:
            self.currentStatus.text = i.next()
            blue.pyos.synchro.SleepWallclock(500)

    def UpdateCurrentStatus(self, currentStatusText):
        self.showLoading = False
        self.currentStatus.text = currentStatusText
        self.currentStatus.display = bool(currentStatusText)

    def LoadDescriptionTooltipPointer(self):
        return uiconst.POINT_RIGHT_2

    def LoadDescriptionTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.AddLabelMedium(text=self.tooltipText, wrapWidth=500)

    def GetMenu(self):
        return [(MenuLabel('UI/Common/Copy'), self.CopyText)]

    def CopyText(self, *args):
        text = self.GetAllContText()
        blue.pyos.SetClipboardData(text)

    def GetAllContText(self):
        text = '\n'.join([self.headerText, self.text, self.currentStatus.text])
        strippedText = StripTags(text)
        return strippedText

    def GetDescriptionIconMenu(self):
        return [(MenuLabel('UI/Common/Copy'), self.CopyTooltipText)]

    def CopyTooltipText(self, *args):
        blue.pyos.SetClipboardData(self.tooltipText)
