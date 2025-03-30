#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentGroupPages\abyssalDeadspaceContentGroupPage.py
from carbonui import TextColor, uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import StreamingVideoSprite
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveHeaderLarge
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.ui import agencyUIConst
from eve.client.script.ui.shared.agencyNew.ui.contentGroupCards import contentGroupCardConstants
from eve.client.script.ui.shared.agencyNew.ui.contentGroupCards.horizontalContentGroupCard import HorizontalContentGroupCard
from eve.client.script.ui.shared.agencyNew.ui.contentGroupPages.baseContentGroupPage import BaseContentGroupPage
from carbonui.control.section import SectionAutoSize, Header
from eve.client.script.ui.shared.agencyNew.ui.controls.warningContainer import WarningContainer
from eve.common.lib import appConst
from localization import GetByLabel

class AbyssalDeadspaceContentGroupPage(BaseContentGroupPage):
    default_name = 'AbyssalDeadspaceContentGroupPage'
    contentGroupID = contentGroupConst.contentGroupAbyssalDeadspace
    default_top = 0
    default_alignMode = uiconst.CENTER

    def ConstructLayout(self):
        super(AbyssalDeadspaceContentGroupPage, self).ConstructLayout()
        self.ConstructLeftContainer()
        self.ConstructRightContainer()

    def ConstructRightContainer(self):
        rightMainContainer = Container(name='RightMainContainer', parent=self.mainCont, align=uiconst.TOALL, left=10)
        gameModesSection = SectionAutoSize(name='GameModesSection', parent=rightMainContainer, align=uiconst.TOTOP, headerText=GetByLabel('UI/Agency/AbyssalDeadspace/gameModes'))
        GameModeContainer(parent=gameModesSection, align=uiconst.TOTOP, titleText=GetByLabel('UI/Agency/AbyssalDeadspace/soloCruiser'), descriptionText=GetByLabel('UI/Agency/AbyssalDeadspace/soloAbyssalDescription'), requirements=GetByLabel('UI/Agency/AbyssalDeadspace/soloRequirements'), top=0)
        GameModeContainer(parent=gameModesSection, align=uiconst.TOTOP, titleText=GetByLabel('UI/Agency/AbyssalDeadspace/abyssalDestroyerCoOpTitle'), descriptionText=GetByLabel('UI/Agency/AbyssalDeadspace/abyssalDestroyerCoOpDescription'), requirements=GetByLabel('UI/Agency/AbyssalDeadspace/destroyerCoOpRequirements'), top=0)
        GameModeContainer(parent=gameModesSection, align=uiconst.TOTOP, titleText=GetByLabel('UI/Agency/AbyssalDeadspace/abyssalCoOpTitle'), descriptionText=GetByLabel('UI/Agency/AbyssalDeadspace/abyssalCoOpDescription'), requirements=GetByLabel('UI/Agency/AbyssalDeadspace/coOpRequirements'), top=0)
        self.cardsContainer = SectionAutoSize(name='cardsContainer', parent=rightMainContainer, align=uiconst.TOTOP, top=10, headerText=GetByLabel('UI/Agency/takeMeTo'))

    def ConstructLeftContainer(self):
        leftMainContainer = Container(name='LeftMainContainer', parent=self.mainCont, align=uiconst.TOLEFT_PROP, width=0.5)
        Frame(bgParent=leftMainContainer, texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png', cornerSize=9, color=agencyUIConst.COLOR_BG)
        Header(parent=leftMainContainer, align=uiconst.TOTOP, text=GetByLabel('UI/Overview/Overview'))
        contentContainer = Container(name='contentContainer', parent=leftMainContainer, padding=(10, 10, 10, 0))
        labelScroll = ScrollContainer(name='labelScroll', parent=contentContainer, align=uiconst.TOTOP, height=130)
        EveLabelMedium(name='descriptionLabel', parent=labelScroll, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/AbyssalDeadspace/abyssalSummary', ownerTypeID=appConst.typeFaction, ownerID=appConst.factionTriglavian), state=uiconst.UI_NORMAL)
        videoContainer = Container(name='videoContainer', parent=contentContainer, align=uiconst.TOTOP, height=234, top=10)
        Frame(bgParent=videoContainer, texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Stroke.png', cornerSize=9, opacity=0.2)
        StreamingVideoSprite(parent=videoContainer, align=uiconst.TOALL, videoPath='res:/video/agency/AbyssalSpaceTestv04.webm', videoLoop=True, padding=(10, 10, 10, 10), sendAnalytics=True)
        WarningContainer(parent=contentContainer, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/AbyssalDeadspace/abyssalTimeWarning'), padding=(0, 10, 0, 0), color=eveColor.WARNING_ORANGE)

    def ConstructMainContainer(self):
        self.mainCont = Container(name='mainContainer', parent=self, align=uiconst.CENTER, width=agencyUIConst.CONTENT_PAGE_WIDTH, height=agencyUIConst.CONTENT_PAGE_HEIGHT)

    def _ConstructContentGroupCard(self, contentGroup, index):
        cardContainer = Container(name='cardContainer', parent=self.cardsContainer, align=uiconst.TOTOP, top=10, padBottom=10, height=contentGroupCardConstants.HORIZONTAL_CARD_HEIGHT)
        self.cards.append(HorizontalContentGroupCard(parent=cardContainer, align=uiconst.CENTER, state=uiconst.UI_NORMAL, contentGroup=contentGroup, contentGroupID=self.contentGroupID, descriptionWidth=150))


class GameModeContainer(ContainerAutoSize):
    default_name = 'GameModeContainer'
    default_padBottom = 10
    default_alignMode = uiconst.TOPLEFT

    def ApplyAttributes(self, attributes):
        super(GameModeContainer, self).ApplyAttributes(attributes)
        self.titleText = attributes.titleText
        self.descriptionText = attributes.descriptionText
        self.requirementsText = attributes.get('requirements', '')
        self.titleColor = attributes.get('titleColor', TextColor.HIGHLIGHT)
        self.ConstructLayout()

    def ConstructLayout(self):
        descWidth = 274 if self.requirementsText else 400
        if self.requirementsText:
            EveLabelMedium(name='requirementsLabel', parent=self, align=uiconst.TOPRIGHT, text=GetByLabel('UI/Agency/AbyssalDeadspace/requirements'), color=TextColor.SECONDARY)
            EveLabelMedium(parent=self, align=uiconst.TOPLEFT, left=descWidth, top=20, text='<right>%s</right>' % self.requirementsText, color=TextColor.NORMAL, maxWidth=130)
        EveHeaderLarge(name='titleLabel', parent=self, align=uiconst.TOPLEFT, text=self.titleText, state=uiconst.UI_NORMAL, color=self.titleColor)
        EveLabelMedium(name='descriptionLabel', parent=self, align=uiconst.TOPLEFT, text=self.descriptionText, state=uiconst.UI_NORMAL, top=20, color=TextColor.SECONDARY, maxWidth=descWidth)
