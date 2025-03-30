#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation\empireTechnologyViews\statisticsPanel.py
import carbonui.const as uiconst
from carbonui.control.editPlainText import LINESPLIT
from carbonui.primitives.container import Container
from carbonui.primitives.gradientSprite import GradientSprite
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from carbonui.fontconst import EVE_MEDIUM_FONTSIZE
from eve.client.script.ui.util.uix import GetTextHeight, GetTextWidth
STATISTICS_TEXT_BOX_MARGIN = 10
STATISTICS_GRADIENT_COLOR = (0.0, 0.0, 0.0)
STATISTICS_GRADIENT_OPACITY = 1.0

def FormatStatisticsText(statisticsText):
    formattedLines = LINESPLIT.sub('\n', statisticsText).splitlines(True)
    return ''.join(formattedLines)


def AddStatisticsLineToContainer(line, container):
    if line != '\n':
        line = line.rstrip()
    statisticsTextContainer = Container(name='statisticsTextContainer', parent=container, align=uiconst.TOTOP, width=GetTextWidth(line, fontsize=EVE_MEDIUM_FONTSIZE), height=GetTextHeight(line, maxLines=1, fontsize=EVE_MEDIUM_FONTSIZE))
    EveLabelMedium(name='statisticsLabel', parent=statisticsTextContainer, align=uiconst.CENTERRIGHT, text=line)


class StatisticsPanel(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        unFormattedStatisticsText = attributes.Get('statisticsText', '')
        self.statisticsText = FormatStatisticsText(unFormattedStatisticsText)
        statisticsTextHeight = GetTextHeight(strng=self.statisticsText, fontsize=EVE_MEDIUM_FONTSIZE)
        statisticsWrapper = Container(name='statisticsWrapper', parent=self, align=uiconst.TOTOP, width=self.width, height=statisticsTextHeight + 2 * STATISTICS_TEXT_BOX_MARGIN)
        self.statisticsTextBox = Container(name='statisticsTextBox', parent=statisticsWrapper, align=uiconst.TORIGHT, width=self.width, height=statisticsTextHeight + 2 * STATISTICS_TEXT_BOX_MARGIN)
        GradientSprite(name='statisticsGradient', bgParent=self.statisticsTextBox, rgbData=((0, STATISTICS_GRADIENT_COLOR),), alphaData=[(0.0, 0.0),
         (0.2, 0.1),
         (0.7, 0.6),
         (1.0, 0.8)], opacity=STATISTICS_GRADIENT_OPACITY)
        self.LoadStatisticsText()

    def IterLines(self):
        return self.statisticsText.splitlines(True)

    def LoadStatisticsText(self):
        statisticsTextContainer = Container(parent=self.statisticsTextBox, align=uiconst.CENTER, width=self.statisticsTextBox.width - 2 * STATISTICS_TEXT_BOX_MARGIN, height=self.statisticsTextBox.height - 2 * STATISTICS_TEXT_BOX_MARGIN)
        for line in self.IterLines():
            AddStatisticsLineToContainer(line, statisticsTextContainer)
