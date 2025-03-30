#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\doubleColumnContentPage.py
from carbonui import uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.flowcontainer import FlowContainer
from eve.client.script.ui.shared.agencyNew.ui import agencyUIConst
from eve.client.script.ui.shared.agencyNew.ui.agencyUIConst import PAD_CARDS
from eve.client.script.ui.shared.agencyNew.ui.contentPages.baseContentPage import BaseContentPage
from carbonui.control.section import Section
from localization import GetByLabel
from eve.client.script.ui.control.statefulButton import StatefulButton

class DoubleColumnContentPage(BaseContentPage):
    scrollSectionWidth = agencyUIConst.LAYOUT_CONTAINER_WIDTH
    __notifyevents__ = ['OnDestinationSet']

    def ApplyAttributes(self, attributes):
        super(DoubleColumnContentPage, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)

    def _ConstructScrollContainer(self):
        self.ConstructButtonContainer()
        self.contentScroll = ScrollContainer(name='contentScroll', parent=self.scrollSection)
        self.contentScroll.onDownButtonSignal.connect(self.OnDownButton)
        self.contentScroll.onUpButtonSignal.connect(self.OnUpButton)

    def _ConstructBaseLayout(self):
        super(DoubleColumnContentPage, self)._ConstructBaseLayout()
        self.ConstructScrollContainer()

    def ConstructScrollContainer(self):
        self.scrollSection = Section(name='scrollContainer', parent=self, padding=(6, 0, 6, 0), align=uiconst.TOLEFT, width=self.scrollSectionWidth)

    def ConstructButtonContainer(self):
        self.buttonRowCont = Container(name='buttonRowContainer', parent=self.scrollSection, align=uiconst.TOBOTTOM, height=30, padTop=10)
        self.primaryActionButton = StatefulButton(parent=self.buttonRowCont, align=uiconst.CENTERRIGHT, iconAlign=uiconst.TORIGHT)

    def UpdateNumResultsLabel(self):
        if len(self.cards) > 0:
            text = GetByLabel('UI/Agency/ShowingXResults', numResults=len(self.cards))
        else:
            text = GetByLabel('UI/Inflight/Scanner/FilteredResults')
        self.scrollSection.SetText(text)

    def _ConstructCards(self, contentPieces):
        self.ConstructFlowContainer()
        self.cards = [ self._ConstructCard(contentPiece) for contentPiece in contentPieces if contentPiece is not None ]

    def ConstructFlowContainer(self):
        self.flowCont = FlowContainer(name='doubleColumnFlowContainer', parent=self.contentScroll, align=uiconst.TOTOP, contentSpacing=(PAD_CARDS, 12))

    def _ConstructCard(self, contentPiece):
        cls = self.GetContentCardClass()
        return cls(parent=self.flowCont, contentPiece=contentPiece, align=uiconst.NOALIGN, contentGroupID=self.contentGroupID)

    def OnCardSelected(self, selectedCard):
        self._UpdateCardSelectedState(selectedCard)
        self.primaryActionButton.SetController(selectedCard.contentPiece)

    def OnDestinationSet(self, destID):
        if not self.selectedCard:
            return
        self.primaryActionButton.SetController(self.selectedCard.contentPiece)
