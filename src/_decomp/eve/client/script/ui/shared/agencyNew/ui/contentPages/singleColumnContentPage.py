#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\singleColumnContentPage.py
from carbonui import uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.shared.agencyNew.ui import agencyUIConst
from eve.client.script.ui.shared.agencyNew.ui.agencyUIConst import CONTENTCARD_WIDTH, PAD_CARDS, CONTENTCARD_HEIGHT
from eve.client.script.ui.shared.agencyNew.ui.contentPages.baseContentPage import BaseContentPage
from carbonui.control.section import Section
from localization import GetByLabel

class SingleColumnContentPage(BaseContentPage):
    default_name = 'SingleColumnContentPage'
    scrollSectionWidth = CONTENTCARD_WIDTH + 31

    def ConstructContentContainer(self):
        self.contentContainer = Container(name='contentContainer', parent=self, padding=(6, 0, 6, 0), bgColor=agencyUIConst.COLOR_BG, align=uiconst.TOLEFT, width=agencyUIConst.LAYOUT_CONTAINER_WIDTH / 2)

    def _ConstructScrollContainer(self):
        self.scrollSection = Section(name='scrollSection', parent=self, align=uiconst.TOLEFT, width=self.scrollSectionWidth, padRight=6)
        self.contentScroll = ScrollContainer(parent=self.scrollSection)
        self.contentScroll.mainCont.padRight = 4
        self.contentScroll.onDownButtonSignal.connect(self.OnDownButton)
        self.contentScroll.onUpButtonSignal.connect(self.OnUpButton)

    def UpdateNumResultsLabel(self):
        if len(self.cards) > 0:
            text = GetByLabel('UI/Agency/ShowingXResults', numResults=len(self.cards))
        else:
            text = GetByLabel('UI/Inflight/Scanner/FilteredResults')
        self.scrollSection.SetText(text)

    def ConstructLayout(self):
        super(SingleColumnContentPage, self).ConstructLayout()
        self.ConstructInfoContainer()

    def ConstructLoadingWheel(self):
        self.loadingWheel = LoadingWheel(parent=self.scrollSection, state=uiconst.UI_HIDDEN, align=uiconst.CENTER)

    def ConstructInfoContainer(self):
        self.infoContainer = None

    def _ConstructCards(self, contentPieces):
        self.cards = [ self._ConstructCard(contentPiece) for contentPiece in contentPieces ]

    def _ConstructCard(self, contentPiece):
        if not contentPiece:
            return
        contentCardClass = self.GetContentCardClass()
        return contentCardClass(parent=self.contentScroll, contentPiece=contentPiece, align=uiconst.TOTOP, width=CONTENTCARD_WIDTH, height=CONTENTCARD_HEIGHT, padBottom=PAD_CARDS, contentGroupID=self.contentGroupID)

    def OnCardSelected(self, selectedCard):
        self._UpdateCardSelectedState(selectedCard)
        if self.infoContainer:
            self.infoContainer.UpdateContentPiece(selectedCard.contentPiece)

    def ConstructCards(self):
        super(SingleColumnContentPage, self).ConstructCards()
        if not self.cards and self.infoContainer:
            self.infoContainer.Empty()
