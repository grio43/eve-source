#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\baseContentPage.py
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.shared.agencyNew import agencySignals, agencyFilters
from eve.client.script.ui.shared.agencyNew.ui import agencyUIConst
from eve.client.script.ui.shared.agencyNew.ui.agencyUIConst import PAD_CARDS, NUM_ROWS, NUM_COLUMNS
from eve.client.script.ui.shared.agencyNew.ui.contentCards import contentCardProvider
from carbonui.control.section import SectionAutoSize
from eve.client.script.ui.shared.agencyNew.ui.filters import filterContProvider
from eveservices.xmppchat import GetChatService
from localization import GetByLabel

class BaseContentPage(ContainerAutoSize):
    default_name = 'BaseContentPage'
    default_align = uiconst.CENTER
    default_height = agencyUIConst.LAYOUT_CONTAINER_HEIGHT
    default_alignMode = uiconst.TOLEFT

    def ApplyAttributes(self, attributes):
        super(BaseContentPage, self).ApplyAttributes(attributes)
        self.contentGroup = attributes.contentGroup
        self.contentGroup.ApplyDefaultFilters()
        self.contentGroupID = self.contentGroup.contentGroupID
        self.itemID = attributes.get('itemID', None)
        self._InitVariables()
        self._ConstructBaseLayout()
        self.ConstructLayout()
        self.ConstructCards()
        self.UpdateNumResultsLabel()
        agencySignals.on_content_pieces_constructed.connect(self.OnContentPiecesConstructed)
        agencyFilters.onFilterChanged.connect(self.OnAgencyFilterChanged)
        self.SelectFirstCard()

    def _InitVariables(self):
        self.contentType = self.contentGroup.GetContentType()
        self.selectedCard = None
        self.cards = []
        self.loadingWheel = None
        self.filterCls = self.GetFilterContainerClass()
        self.chatChannelID = self.contentGroup.GetChatChannelID()

    def Close(self):
        agencySignals.on_content_pieces_constructed.disconnect(self.OnContentPiecesConstructed)
        agencyFilters.onFilterChanged.disconnect(self.OnAgencyFilterChanged)
        super(BaseContentPage, self).Close()

    def _ConstructBaseLayout(self):
        if self.ShouldConstructLeftContainer():
            self.ConstructLeftCont()
            self.ConstructInformationContainer()
            if self.filterCls:
                self.ConstructFilterContainer()
            if self.chatChannelID:
                self.ConstructJoinChatButton()
            self.ConstructTooltips()

    def ConstructTooltips(self):
        pass

    def ConstructLayout(self):
        self._ConstructScrollContainer()
        self.ConstructLoadingWheel()

    def ShouldConstructLeftContainer(self):
        return self.filterCls or self.chatChannelID

    def _ConstructScrollContainer(self):
        self.contentScroll = None

    def ConstructLoadingWheel(self):
        self.loadingWheel = LoadingWheel(parent=self, align=uiconst.CENTER)

    def ConstructCards(self):
        self.DeleteCards()
        contentPieces = self.GetContentPiecesCapped()
        if contentPieces:
            self._ConstructCards(contentPieces)
            self.ConnectToCardSelectSignal()
            self.AnimateEnterAllCards()
        if self.loadingWheel:
            self.loadingWheel.Hide()

    def OnAgencyFilterChanged(self, *args, **kwargs):
        self.DeleteCards()

    def DeleteCards(self):
        if self.contentScroll:
            self.contentScroll.Flush()
        self.cards = []
        if self.loadingWheel:
            self.loadingWheel.Show()

    def AnimateEnterAllCards(self):
        for i, card in enumerate(self.cards):
            card.AnimEnter(i)

    def _ConstructCards(self, contentPieces):
        pass

    def GetContentCardClass(self):
        return contentCardProvider.GetContentCardCls(self.contentGroup.GetContentType())

    def OnContentPiecesConstructed(self, contentGroupID):
        if contentGroupID == self.contentGroupID:
            self.ConstructCards()
            self.UpdateNumResultsLabel()
            self.SelectFirstCard()

    def UpdateNumResultsLabel(self):
        pass

    def GetContentPiecesCapped(self):
        maxNumContent = NUM_ROWS * NUM_COLUMNS
        contentPieces = self.GetContentPieces()
        return contentPieces[:maxNumContent]

    def GetContentPieces(self):
        return self.contentGroup.GetContentPieces()

    def ConstructLeftCont(self):
        self.leftCont = Container(name='leftCont', parent=self, align=uiconst.TOLEFT, width=agencyUIConst.FILTER_CONTAINER_WIDTH, padRight=PAD_CARDS)

    def ConstructFilterContainer(self):
        self.filterCls(parent=self.leftCont, contentGroupID=self.contentGroupID)

    def GetFilterContainerClass(self):
        return filterContProvider.GetFilterCls(self.contentType)

    def ConstructInformationContainer(self):
        self.informationContainer = SectionAutoSize(name='informationContainer', parent=self.leftCont, align=uiconst.TOBOTTOM, headerText=GetByLabel('UI/Common/Information'), idx=0)

    def ConstructJoinChatButton(self):
        Button(parent=self.informationContainer, align=uiconst.TOTOP, func=lambda x: GetChatService().JoinChannel(self.chatChannelID), label=GetByLabel('UI/Agency/JoinChat'), hint=GetByLabel('UI/Agency/JoinChatChannel', contentTypeName=self.contentGroup.GetName()))

    def SelectCard(self, card):
        self._OnCardSelected(card)

    def SelectFirstCard(self):
        if not self.cards:
            return
        lastSelectedID = self.contentGroup.lastSelectedID
        selectCard = None
        if lastSelectedID:
            for card in self.cards:
                if card.contentPiece.GetCardID() == lastSelectedID:
                    selectCard = card
                    break

        self.selectedCard = None
        self.SelectCard(selectCard or self.cards[0])

    def OnCardSelected(self, selectedCard):
        pass

    def _OnCardSelected(self, selectedCard):
        if not selectedCard or selectedCard == self.selectedCard:
            return
        if selectedCard:
            sm.ScatterEvent('OnAgencyContentCardClicked', contentGroupID=self.contentGroupID, contentItemID=selectedCard.contentPiece.GetItemID(), contentTypeID=selectedCard.contentPiece.GetContentTypeID())
        self.selectedCard = selectedCard
        self.contentGroup.lastSelectedID = self.selectedCard.contentPiece.GetCardID() if self.selectedCard else None
        self.OnCardSelected(selectedCard)

    def ConnectToCardSelectSignal(self):
        for card in self.cards:
            card.onCardSelectedSignal.connect(self._OnCardSelected)

    def _UpdateCardSelectedState(self, selectedCard):
        for card in self.cards:
            if card == selectedCard:
                card.Select()
            else:
                card.Deselect()

    def OnUpButton(self):
        if not self.cards:
            return
        idx = self.cards.index(self.selectedCard) - 1
        if idx >= 0:
            card = self.cards[idx]
            self.SelectCard(card)

    def OnDownButton(self):
        if not self.cards:
            return
        idx = self.cards.index(self.selectedCard) + 1
        if idx < len(self.cards):
            card = self.cards[idx]
            self.SelectCard(card)
