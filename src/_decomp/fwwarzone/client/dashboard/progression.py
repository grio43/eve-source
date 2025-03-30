#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fwwarzone\client\dashboard\progression.py
import logging
from carbonui import TextColor, uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.primitives.vectorline import VectorLine
from eve.client.script.ui.control.eveLabel import EveCaptionLarge, EveLabelLarge
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
from eve.client.script.ui.util.uix import GetRankSprite
from fwwarzone.client.dashboard.const import FACTION_ID_TO_COLOR, FACTION_ID_TO_COLOR_BACKGROUND, PROGRESSION_SCREEN_FLAG_FRAME
from fwwarzone.client.dashboard.statisticsController import StatisticsController
from localization import GetByLabel
from utillib import KeyVal
logger = logging.getLogger(__name__)

class PersonalStatsPanel(ContainerAutoSize):

    def ApplyAttributes(self, attributes):
        super(PersonalStatsPanel, self).ApplyAttributes(attributes)
        statsController = attributes.get('statsController')
        allData = statsController.GetStatisticsScrollData('personal')
        self.headers = allData['header']
        self.dataLines = allData['data']
        self.ConstructLayout()

    def ConstructLayout(self):
        layoutGrid = LayoutGrid(parent=self, align=uiconst.TOPLEFT, rows=len(self.dataLines) + 1, columns=len(self.headers), cellSpacing=(100, 1))
        for header in self.headers:
            headerlabel = EveLabelLarge(text=header, align=uiconst.CENTERRIGHT, color=TextColor.SECONDARY)
            layoutGrid.AddCell(headerlabel)

        for line in self.dataLines:
            for cellText in line.split('<t>'):
                cellLabel = EveLabelLarge(text=cellText, align=uiconst.CENTERRIGHT)
                layoutGrid.AddCell(cellLabel)


class FWProgressionPanel(Container):
    TOP_PADDING = 44
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.factionId = attributes.get('factionId')
        self.mainCont = None

    def LoadPanel(self):
        if self.mainCont:
            return
        if self.factionId == None:
            EveCaptionLarge(parent=self, text=GetByLabel('UI/FactionWarfare/frontlinesDashboard/notEngagedInFW'), align=uiconst.CENTER, color=TextColor.SECONDARY)
            return
        self.mainCont = ContainerAutoSize(parent=self, align=uiconst.TOALL, padTop=FWProgressionPanel.TOP_PADDING)
        topCont = ContainerAutoSize(align=uiconst.TOTOP, parent=self.mainCont, state=uiconst.UI_DISABLED)
        Sprite(name='background_swirl_sprite', parent=topCont, align=uiconst.CENTERTOP, texturePath=FACTION_ID_TO_COLOR_BACKGROUND[self.factionId], width=926, height=350)
        currentRankCont = Container(name='CurrentRankCont', parent=topCont, align=uiconst.CENTERTOP, height=318, width=817, padding=(105,
         FWProgressionPanel.TOP_PADDING,
         105,
         0))
        factionMilitiaId = sm.GetService('facwar').GetFactionMilitiaCorporation(self.factionId)
        standing = sm.GetService('standing').GetStanding(factionMilitiaId, session.charid)
        currentRankObject = sm.GetService('facwar').GetCharacterRankInfo(session.charid)
        if not currentRankObject:
            logger.error('currentRankObject is unavailable - character is not in FW?')
            return
        Sprite(name='flag_sprite', parent=currentRankCont, align=uiconst.TOPLEFT, color=FACTION_ID_TO_COLOR[self.factionId], texturePath=PROGRESSION_SCREEN_FLAG_FRAME, pos=(0, 0, 128, 219), opacity=0.5)
        currentRank = currentRankObject.currentRank
        icon = GetRankSprite(currentRank, self.factionId, align=uiconst.CENTER)
        rankCont = Transform(parent=currentRankCont, align=uiconst.TOLEFT, width=128, height=128, top=-25, idx=0)
        icon.SetParent(rankCont)
        icon.SetState(uiconst.UI_DISABLED)
        facwar = sm.GetService('facwar')
        rankName, rankDescription = facwar.GetRankLabel(session.warfactionid, currentRank)
        rankDescriptionCont = ContainerAutoSize(parent=currentRankCont, align=uiconst.TOLEFT, alignMode=uiconst.TOTOP, width=466, padding=(53,
         FWProgressionPanel.TOP_PADDING / 2,
         0,
         0))
        EveCaptionLarge(align=uiconst.TOTOP, parent=rankDescriptionCont, text=rankName)
        EveLabelLarge(align=uiconst.TOTOP, parent=rankDescriptionCont, text=rankDescription)
        ranksRowCont = ContainerAutoSize(name='ranksRowCont', parent=self.mainCont, align=uiconst.TOTOP)
        topRankRow = ContainerAutoSize(parent=ranksRowCont, align=uiconst.TOTOP)
        bottomRankRow = ContainerAutoSize(parent=ranksRowCont, align=uiconst.TOTOP)
        progressionTableCont = Container(name='progressionTableCont', parent=self.mainCont, align=uiconst.TOTOP, height=352)
        Line(parent=progressionTableCont, align=uiconst.TOTOP, color=(1.0, 1.0, 1.0, 0.1), top=45)
        self.personalStats = PersonalStatsPanel(statsController=StatisticsController(None), parent=progressionTableCont, align=uiconst.CENTER, alignMode=uiconst.TOPLEFT)
        centeredRanksCont = ContainerAutoSize(name='centeredRanksCont', parent=topRankRow, align=uiconst.CENTER, height=20, alignMode=uiconst.TOLEFT)
        centeredRanksSpriteCont = ContainerAutoSize(name='centeredRanksSpriteCont', parent=bottomRankRow, align=uiconst.CENTER, alignMode=uiconst.TOLEFT, height=50, padTop=16, left=13)
        infoSvc = sm.GetService('info')
        for i in range(10):
            value = 0.0
            if standing >= i:
                value = 1.0
                opacity = 0.8
            else:
                value = standing - float(i - 1)
                opacity = 1.0
            GaugeCircular(parent=centeredRanksCont, align=uiconst.TOLEFT, radius=10, value=value, colorStart=FACTION_ID_TO_COLOR[self.factionId], colorEnd=FACTION_ID_TO_COLOR[self.factionId], showMarker=False, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, state=uiconst.UI_DISABLED, opacity=opacity)
            if i < 9:
                lineCont = Container(parent=centeredRanksCont, align=uiconst.TOLEFT, width=57)
                if value < 1.0:
                    outputMode = uiconst.OUTPUT_COLOR
                else:
                    outputMode = uiconst.OUTPUT_COLOR_AND_GLOW
                VectorLine(parent=lineCont, translationFrom=(0, 10), translationTo=(57, 10), colorFrom=FACTION_ID_TO_COLOR[self.factionId], colorTo=FACTION_ID_TO_COLOR[self.factionId], widthFrom=0.75, widthTo=0.75, outputMode=outputMode, glowBrightness=2.0)
            icon = GetRankSprite(i, self.factionId, align=uiconst.CENTER)
            rankCont = Transform(parent=centeredRanksSpriteCont, align=uiconst.TOLEFT, width=50, scale=(0.5, 0.5))
            icon.SetParent(rankCont)
            icon.hint, _ = facwar.GetRankLabel(self.factionId, i)

            def CreateOnClick(rankIdx):

                def OnClick():
                    abstractinfo = KeyVal(warFactionID=self.factionId, currentRank=rankIdx)
                    infoSvc.ShowInfo(const.typeRank, abstractinfo=abstractinfo)

                return OnClick

            icon.OnClick = CreateOnClick(i)
            if i < 9:
                Container(name='spacerCont', parent=centeredRanksSpriteCont, align=uiconst.TOLEFT, width=27)
