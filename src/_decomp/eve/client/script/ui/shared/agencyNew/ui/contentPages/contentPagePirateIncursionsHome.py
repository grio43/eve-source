#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\contentPagePirateIncursionsHome.py
import eveicon
from carbonui.control.scrollContainer import ScrollContainer
import localization
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.control.section import SectionAutoSize
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.ui.agencyUIConst import CONTENT_PAGE_WIDTH_HALF
from eve.client.script.ui.shared.agencyNew.ui.contentGroupCards import contentGroupCardConstants
from eve.client.script.ui.shared.agencyNew.ui.contentGroupCards.horizontalContentGroupCard import HorizontalContentGroupCard
from eve.client.script.ui.shared.agencyNew.ui.contentGroupPages.baseContentGroupPage import BaseContentGroupPage
MAIN_CONT_PADDING = 10

class ContentPagePirateIncursionsHome(BaseContentGroupPage):
    default_name = 'ContentPagePirateIncursionsHome'
    contentGroupID = contentGroupConst.contentGroupPirateIncursionsHome
    default_top = 0
    mainContHeight = 500 + 2 * MAIN_CONT_PADDING
    clippingParentTop = 0

    def ConstructLayout(self):
        super(ContentPagePirateIncursionsHome, self).ConstructLayout()
        self.ConstructLeftContainer()
        self.ConstructRightContainer()

    def ConstructRightContainer(self):
        self.rightMainContainer = Container(name='rightMainContainer', parent=self.mainCont, align=uiconst.CENTERTOP, pos=(0,
         0,
         CONTENT_PAGE_WIDTH_HALF,
         self.mainContHeight - 2 * MAIN_CONT_PADDING))
        self.enlistmentCont = SectionAutoSize(name='enlistmentCont', parent=self.rightMainContainer, align=uiconst.TOTOP, headerText=localization.GetByLabel('UI/Agency/PirateIncursions/enlistmentHeader'))
        EveLabelMedium(name='enlistmentLabel', parent=self.enlistmentCont, align=uiconst.TOTOP, text=localization.GetByLabel('UI/Agency/PirateIncursions/enlistment'))
        Button(name='openEnlistmentButton', parent=Container(parent=self.enlistmentCont, align=uiconst.TOTOP, height=35, top=10), align=uiconst.CENTERLEFT, texturePath=eveicon.open_window, label=localization.GetByLabel('UI/Agency/PirateIncursions/openPirateEnlistmentWindow'), func=sm.GetService('cmd').OpenFwEnlistment)
        Button(name='openEnlistmentButton', parent=Container(parent=self.enlistmentCont, align=uiconst.TOTOP, height=35, top=10), align=uiconst.CENTERLEFT, texturePath=eveicon.pirate_insurgencies, label=localization.GetByLabel('UI/Agency/PirateIncursions/OpenPirateInsurgencyWindow'), func=sm.GetService('cmd').OpenInsurgencyDashboard)
        self.takeMeToCont = SectionAutoSize(name='takeMeToCont', parent=self.rightMainContainer, align=uiconst.TOTOP, headerText=localization.GetByLabel('UI/Agency/PirateIncursions/takeMeToHeader'))

    def ConstructLeftContainer(self):
        self.leftMainContainer = Container(name='leftMainContainer', parent=self.mainCont, align=uiconst.CENTERTOP, pos=(0,
         0,
         496,
         self.mainContHeight - 2 * MAIN_CONT_PADDING), insidePadding=(20,
         MAIN_CONT_PADDING,
         20,
         0))
        self.overviewCont = SectionAutoSize(name='overviewCont', parent=self.leftMainContainer, align=uiconst.TOTOP, headerText=localization.GetByLabel('UI/Agency/PirateIncursions/overviewHeader'))
        overviewScroll = ScrollContainer(parent=self.overviewCont, align=uiconst.TOTOP, height=200)
        EveLabelMedium(name='overviewLabel', parent=overviewScroll, align=uiconst.TOTOP, text=localization.GetByLabel('UI/Agency/PirateIncursions/overview'))
        self.additionalInfoCont = SectionAutoSize(name='additionalInfoCont', parent=self.leftMainContainer, align=uiconst.TOTOP, headerText=localization.GetByLabel('UI/Agency/PirateIncursions/additionalInfoHeader'))
        infoScroll = ScrollContainer(parent=self.additionalInfoCont, align=uiconst.TOTOP, height=190)
        EveLabelMedium(parent=infoScroll, name='additionalInfoLabel', align=uiconst.TOTOP, text=localization.GetByLabel('UI/Agency/PirateIncursions/additionalInformation'))

    def _ConstructContentGroupCard(self, contentGroup, index):
        cardContainer = Container(name='cardContainer', parent=self.takeMeToCont, align=uiconst.TOTOP, height=contentGroupCardConstants.HORIZONTAL_CARD_HEIGHT, top=10 if index > 0 else 0)
        self.cards.append(HorizontalContentGroupCard(parent=cardContainer, align=uiconst.CENTER, state=uiconst.UI_NORMAL, contentGroup=contentGroup, contentGroupID=self.contentGroupID))

    def ConstructContentGroupCards(self):
        super(ContentPagePirateIncursionsHome, self).ConstructContentGroupCards()
        self.mainCont.columns = 2
