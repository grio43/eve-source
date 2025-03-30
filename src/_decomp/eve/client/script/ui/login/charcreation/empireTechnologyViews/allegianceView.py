#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation\empireTechnologyViews\allegianceView.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from charactercreator.client.empireSelectionData import GetEmpireLogo
from charactercreator.client.scalingUtils import SMALL_SCREEN_HEIGHT, BIG_SCREEN_HEIGHT
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.login.charcreation.empireTechnologyViews.technologyView import TechnologyView
from eve.client.script.ui.login.charcreation.empireui.empireBanner import MinimalEmpireBanner
from eve.client.script.ui.login.charcreation.technologyViewUtils import LineDecoration, LINE_DECORATION_GRADIENT_HEIGHT
from eve.client.script.ui.util.uix import GetTextHeight
from eve.common.lib.appConst import factionAmarrEmpire, factionCaldariState, factionGallenteFederation, factionMinmatarRepublic, factionTheBloodRaiderCovenant, factionGuristasPirates, factionSerpentis, factionAngelCartel, factionByRace, raceByFaction
from eve.common.script.util.facwarCommon import GetOccupationEnemyFaction
ELEMENTS_PADDING_TOP = -40
LINE_DECORATION_WIDTH = 1000
LINE_DECORATION_HEIGHT = 4
INTERNAL_MARGIN_H = 40
INTERNAL_MARGIN_V = 40
PEOPLE_DESCRIPTION_WIDTH = 450
PEOPLE_DESCRIPTION_FONTSIZE = 16
PEOPLE_DESCRIPTION_PAD_TOP = 60
PORTRAIT_WIDTH = 450
PORTRAIT_HEIGHT = 308
PORTRAIT_PAD_LEFT = 30
POLITICAL_RELATIONSHIP_PAD_TOP = 10
POLITICAL_RELATIONSHIP_PAD_BOT = 10
POLITICAL_RELATIONSHIP_ICON_SIZE = 150
POLITICAL_RELATIONSHIP_TEXT_WIDTH = 320
POLITICAL_RELATIONSHIP_TEXT_FONTSIZE = 16
POLITICAL_RELATIONSHIP_TEXT_PAD_TOP = 10
POLITICAL_RELATIONSHIP_INTERNAL_PAD = 20
POLITICAL_RELATIONSHIP_ICON_TEXT_FONTSIZE = 14
POLITICAL_RELATIONSHIP_FRAME_WIDTH = 128
POLITICAL_RELATIONSHIP_FRAME_HEIGHT = 200
SCALE_FACTOR_AT_SMALL_SCREEN_HEIGHT = 0.71
ICON_COLOR_BY_FACTION = {factionAmarrEmpire: (0.51, 0.44, 0.32),
 factionCaldariState: (0.29, 0.43, 0.5),
 factionGallenteFederation: (0.21, 0.4, 0.4),
 factionMinmatarRepublic: (0.4, 0.22, 0.2),
 factionTheBloodRaiderCovenant: (0.43, 0.0, 0.0),
 factionGuristasPirates: (0.8, 0.51, 0.0),
 factionSerpentis: (0.47, 0.44, 0.29),
 factionAngelCartel: (0.36, 0.39, 0.43)}
PIRATE_LOGO_BY_FACTION = {factionTheBloodRaiderCovenant: 'res:/UI/Texture/Classes/EmpireSelection/pirateLogo_Bloodraiders.png',
 factionGuristasPirates: 'res:/UI/Texture/Classes/EmpireSelection/pirateLogo_Guristas.png',
 factionSerpentis: 'res:/UI/Texture/Classes/EmpireSelection/pirateLogo_Serpentis.png',
 factionAngelCartel: 'res:/UI/Texture/Classes/EmpireSelection/pirateLogo_AngelCartel.png'}
LOGO_SIZE = 128
TRADTIONAL_PIRATE_OPPOSITION_BY_RACE = {factionAmarrEmpire: factionTheBloodRaiderCovenant,
 factionCaldariState: factionGuristasPirates,
 factionGallenteFederation: factionSerpentis,
 factionMinmatarRepublic: factionAngelCartel}

class AllegianceView(TechnologyView):

    def ApplyAttributes(self, attributes):
        TechnologyView.ApplyAttributes(self, attributes)
        centralContainer = Container(name='centralContainer', parent=self, align=uiconst.ANCH_TOPLEFT, width=self.width, height=self.height)
        lineDecorationWidth = self._GetLineDecorationWidth()
        portraitWidth, portraitHeight = self._GetPortraitViewSize()
        peopleDescriptionText = self.technology.GetMainText(self.raceID)
        peopleWidth, peopleHeight = self._GetPeopleDescriptionSize(peopleDescriptionText)
        peopleHeight += PEOPLE_DESCRIPTION_PAD_TOP * self._GetScaleFactor()
        relationshipFrameWidth, relationshipFrameHeight = self._GetPoliticalRelationshipFrameSize()
        pirateEnemyText = self.GetPirateEnemyText()
        enemyText = self.GetEnemyText()
        relationshipTextWidth = self._GetRelationshipDescriptionWidth()
        relationshipTextHeight = self._GetRelationshipDescriptionHeight(relationshipTextWidth, pirateEnemyText, enemyText) + POLITICAL_RELATIONSHIP_TEXT_PAD_TOP
        relationshipsVPad = POLITICAL_RELATIONSHIP_PAD_TOP + POLITICAL_RELATIONSHIP_PAD_BOT
        relationshipsWidth = relationshipFrameWidth + relationshipTextWidth + POLITICAL_RELATIONSHIP_INTERNAL_PAD
        relationshipsHeight = max(relationshipFrameHeight, relationshipTextHeight) + relationshipsVPad
        topViewHeight = max(portraitHeight, peopleHeight)
        lineViewHeight = 2 * INTERNAL_MARGIN_V + LINE_DECORATION_GRADIENT_HEIGHT
        centralViewWidth = lineDecorationWidth
        centralViewHeight = topViewHeight + lineViewHeight + relationshipsHeight
        centralView = Container(name='centralView', parent=centralContainer, align=uiconst.CENTER, width=centralViewWidth, height=centralViewHeight, top=ELEMENTS_PADDING_TOP * self._GetScaleFactor())
        self.BuildTopView(parent=centralView, width=centralViewWidth, height=topViewHeight, portraitWidth=portraitWidth, portraitHeight=portraitHeight, peopleDescriptionText=peopleDescriptionText, peopleWidth=peopleWidth)
        self.BuildLineView(parent=centralView, width=centralViewWidth, height=lineViewHeight)
        self.BuildBottomView(parent=centralView, width=relationshipsWidth * 2, height=relationshipsHeight, frameWidth=relationshipFrameWidth, frameHeight=relationshipFrameHeight, textWidth=relationshipTextWidth, pirateEnemyText=pirateEnemyText, enemyText=enemyText)

    def BuildTopView(self, parent, width, height, portraitWidth, portraitHeight, peopleDescriptionText, peopleWidth):
        self.topView = Container(name='topView', parent=parent, align=uiconst.TOTOP, width=width, height=height, opacity=1.0)
        self.AddPeopleDescription(peopleDescriptionText, peopleWidth, height)
        self.AddPortraitView(portraitWidth, portraitHeight)

    def AddPeopleDescription(self, text, width, height):
        topLeftView = Container(name='topLeftView', parent=self.topView, align=uiconst.TOLEFT, width=self.topView.width / 2, height=self.topView.height)
        peopleDescriptionContainer = Container(name='peopleDescriptionContainer', parent=topLeftView, width=width, height=height, align=uiconst.TORIGHT)
        Label(name='peopleDescriptionLabel', parent=peopleDescriptionContainer, width=width, height=height, text=text, fontsize=self._GetPeopleDescriptionFontsize(), top=PEOPLE_DESCRIPTION_PAD_TOP * self._GetScaleFactor())

    def AddPortraitView(self, width, height):
        topRightView = Container(name='topRightView', parent=self.topView, align=uiconst.TORIGHT, width=self.topView.width / 2, height=self.topView.height)
        portraitView = self.technology.GetMainView(self.raceID)
        portraitViewContainer = Container(name='portraitViewContainer', parent=topRightView, align=uiconst.TOPLEFT, width=width, height=height, padLeft=PORTRAIT_PAD_LEFT)
        Sprite(name='portraitView', parent=portraitViewContainer, align=uiconst.TOTOP, texturePath=portraitView, useSizeFromTexture=False, width=width, height=height)

    def BuildLineView(self, parent, width, height):
        lineView = Container(name='lineView', parent=parent, align=uiconst.TOTOP, width=width, height=height)
        self.line = LineDecoration(name='lineDecoration', parent=lineView, align=uiconst.TOTOP, width=width, height=LINE_DECORATION_HEIGHT, lineWidth=width, opacity=1.0, padTop=INTERNAL_MARGIN_V)

    def BuildBottomView(self, parent, width, height, frameWidth, frameHeight, textWidth, pirateEnemyText, enemyText):
        self.bottomView = Container(name='bottomView', parent=parent, align=uiconst.TOTOP, width=width, height=height, padTop=POLITICAL_RELATIONSHIP_PAD_TOP, padBottom=POLITICAL_RELATIONSHIP_PAD_BOT)
        fontsize = self._GetPoliticalRelationshipFontsize()
        iconFontsize = self._GetPoliticalRelationshipIconFontsize()
        self.AddEnemiesView(frameWidth, frameHeight, height, textWidth, enemyText, fontsize, iconFontsize)
        self.AddPirateEnemiesView(frameWidth, frameHeight, height, textWidth, pirateEnemyText, fontsize, iconFontsize)

    def AddEnemiesView(self, frameWidth, frameHeight, height, textWidth, text, fontsize, iconFontsize):
        bottomLeftView = Container(name='bottomLeftView', parent=self.bottomView, align=uiconst.TOLEFT, width=self.bottomView.width / 2, height=self.bottomView.height)
        factionID = factionByRace[self.raceID]
        enemyFactionID = GetOccupationEnemyFaction(factionID)
        enemyRaceID = raceByFaction.get(enemyFactionID)
        iconColor = ICON_COLOR_BY_FACTION[enemyFactionID]
        logo = GetEmpireLogo(enemyRaceID)
        logoSize = self._GetLogoSize()
        self.enemy = PoliticalRelationshipView(logo=logo, logoSize=logoSize, text=text, iconText=self.GetEnemyTitle(), iconTextFontsize=iconFontsize, iconView=self.GetEnemyIcon(), iconColor=iconColor, frameWidth=frameWidth, frameHeight=frameHeight, textWidth=textWidth, fontsize=fontsize, parent=bottomLeftView, align=uiconst.TOPLEFT, width=frameWidth + textWidth + POLITICAL_RELATIONSHIP_INTERNAL_PAD, height=height, opacity=1.0)

    def AddPirateEnemiesView(self, frameWidth, frameHeight, height, textWidth, text, fontsize, iconFontsize):
        bottomRightView = Container(name='bottomRightView', parent=self.bottomView, align=uiconst.TORIGHT, width=self.bottomView.width / 2, height=self.bottomView.height)
        factionID = factionByRace[self.raceID]
        enemyFactionID = TRADTIONAL_PIRATE_OPPOSITION_BY_RACE[factionID]
        iconColor = ICON_COLOR_BY_FACTION[enemyFactionID]
        logo = PIRATE_LOGO_BY_FACTION[enemyFactionID]
        logoSize = self._GetLogoSize()
        self.pirateEnemy = PoliticalRelationshipView(logo=logo, logoSize=logoSize, text=text, iconText=self.GetPirateEnemyTitle(), iconTextFontsize=iconFontsize, iconView=self.GetPirateEnemyIcon(), iconColor=iconColor, frameWidth=frameWidth, frameHeight=frameHeight, textWidth=textWidth, fontsize=fontsize, parent=bottomRightView, align=uiconst.TOPRIGHT, width=frameWidth + textWidth + POLITICAL_RELATIONSHIP_INTERNAL_PAD, height=height, opacity=1.0)

    def GetPirateEnemyText(self):
        return self.technology.GetTechExample(2).GetSubtitle(self.raceID)

    def GetEnemyText(self):
        return self.technology.GetTechExample(1).GetSubtitle(self.raceID)

    def GetPirateEnemyTitle(self):
        return self.technology.GetTechExample(2).GetTitle(self.raceID)

    def GetEnemyTitle(self):
        return self.technology.GetTechExample(1).GetTitle(self.raceID)

    def GetPirateEnemyIcon(self):
        return self.technology.GetTechExample(2).GetIcon(self.raceID)

    def GetEnemyIcon(self):
        return self.technology.GetTechExample(1).GetIcon(self.raceID)

    def _GetLineDecorationWidth(self):
        scaleFactor = self._GetScaleFactor()
        width = LINE_DECORATION_WIDTH * scaleFactor
        return width

    def _GetPortraitViewSize(self):
        return self._GetImageSize(PORTRAIT_WIDTH, PORTRAIT_HEIGHT)

    def _GetPoliticalRelationshipFrameSize(self):
        return self._GetImageSize(POLITICAL_RELATIONSHIP_FRAME_WIDTH, POLITICAL_RELATIONSHIP_FRAME_HEIGHT)

    def _GetImageSize(self, baseWidth, baseHeight):
        scaleFactor = self._GetScaleFactor()
        width = baseWidth * scaleFactor
        height = baseHeight * scaleFactor
        return (width, height)

    def _GetLogoSize(self):
        return LOGO_SIZE * self._GetScaleFactor()

    def _GetPeopleDescriptionFontsize(self):
        return PEOPLE_DESCRIPTION_FONTSIZE * self._GetScaleFactor()

    def _GetPeopleDescriptionSize(self, text):
        width = PEOPLE_DESCRIPTION_WIDTH * self._GetScaleFactor()
        height = GetTextHeight(strng=text, width=width, fontsize=self._GetPeopleDescriptionFontsize())
        return (width, height)

    def _GetPoliticalRelationshipFontsize(self):
        return POLITICAL_RELATIONSHIP_TEXT_FONTSIZE * self._GetScaleFactor()

    def _GetPoliticalRelationshipIconFontsize(self):
        return POLITICAL_RELATIONSHIP_ICON_TEXT_FONTSIZE * self._GetScaleFactor()

    def _GetRelationshipDescriptionWidth(self):
        return POLITICAL_RELATIONSHIP_TEXT_WIDTH * self._GetScaleFactor()

    def _GetRelationshipDescriptionHeight(self, width, pirateEnemyText, enemyText):
        pirateEnemyHeight = GetTextHeight(strng=pirateEnemyText, width=width, fontsize=self._GetPoliticalRelationshipFontsize())
        enemyHeight = GetTextHeight(strng=enemyText, width=width, fontsize=self._GetPoliticalRelationshipFontsize())
        return max(pirateEnemyHeight, enemyHeight)

    def _GetScaleFactor(self):
        desktopHeight = uicore.desktop.height
        if desktopHeight > BIG_SCREEN_HEIGHT:
            desktopHeight = BIG_SCREEN_HEIGHT
        return SCALE_FACTOR_AT_SMALL_SCREEN_HEIGHT * desktopHeight / SMALL_SCREEN_HEIGHT


class PoliticalRelationshipView(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        logo = attributes.logo
        logoSize = attributes.logoSize
        text = attributes.text
        iconText = attributes.iconText
        iconTextFontsize = attributes.iconTextFontsize
        iconView = attributes.iconView
        iconColor = attributes.iconColor
        frameWidth = attributes.frameWidth
        frameHeight = attributes.frameHeight
        textWidth = attributes.textWidth
        fontsize = attributes.fontsize
        bannerContainer = Container(name='relationshipBannerContainer', parent=self, align=uiconst.TOLEFT, width=frameWidth, height=frameHeight, padRight=POLITICAL_RELATIONSHIP_INTERNAL_PAD)
        MinimalEmpireBanner(name='relationshipBanner', parent=bannerContainer, width=frameWidth, height=frameHeight, align=uiconst.TOTOP, logo=logo, logoSize=logoSize, iconText=iconText, iconTextFontsize=iconTextFontsize, iconView=iconView, iconColor=iconColor)
        descriptionContainer = Container(name='relationshipDescriptionContainer', parent=self, align=uiconst.TOLEFT, width=textWidth, height=self.height, padTop=POLITICAL_RELATIONSHIP_TEXT_PAD_TOP)
        Label(name='relationshipDescriptionLabel', parent=descriptionContainer, align=uiconst.TOTOP, width=textWidth, height=self.height - POLITICAL_RELATIONSHIP_TEXT_PAD_TOP, text=text, fontsize=fontsize)
