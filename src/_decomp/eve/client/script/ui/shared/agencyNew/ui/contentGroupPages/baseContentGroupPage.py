#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentGroupPages\baseContentGroupPage.py
import math
import mathext
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.control.moreIcon import DescriptionIcon
from eve.client.script.ui.shared.agencyNew.ui.contentGroupCards import contentGroupCardProvider, contentGroupCardConstants
from eve.client.script.ui.shared.agencyNew.ui.contentGroupCards.contentGroupCardConstants import VERTICAL_CARD_BOTTOM_CONTAINER_HEIGHT, MAX_VISIBLE_VERTICAL_CARDS, VERTICAL_CARD_WIDTH, EDGE_GRADIENT_WIDTH, EDGE_GRADIENT_HEIGHT, CLIPPING_PARENT_HEIGHT
from eve.client.script.ui.shared.agencyNew.ui.contentGroupPages.contentScroller import ContentScroller
from eve.client.script.ui.control.simpleTextTooltip import SimpleTextTooltip
from eveexceptions import ExceptionEater
from localization import GetByLabel

class BaseContentGroupPage(ContainerAutoSize):
    default_name = 'BaseContentGroupPage'
    contentGroupID = contentGroupConst.contentGroupHome
    default_align = uiconst.CENTER
    default_alignMode = uiconst.CENTERTOP
    mainContHeight = CLIPPING_PARENT_HEIGHT
    extraSlotWidth = 130
    clippingParentTop = 27

    def ApplyAttributes(self, attributes):
        super(BaseContentGroupPage, self).ApplyAttributes(attributes)
        self.contentGroup = attributes.contentGroup
        self.cards = []
        self.contentScroller = None
        self.ConstructLayout()
        self.ConstructContentGroupCards()
        self.AnimateAllCards()

    def AnimateAllCards(self):
        for i, child in enumerate(self.cards):
            child.AnimEnter(self.GetOffsetValue(i))

    def ConstructContentGroupCards(self):
        availableChildren = [ child for child in self.contentGroup.children if child.IsVisible() ]
        numAvailableChildren = len(availableChildren)
        self.mainCont.columns = numAvailableChildren
        for index, childContentGroup in enumerate(availableChildren):
            self._ConstructContentGroupCard(childContentGroup, index)

        if numAvailableChildren > MAX_VISIBLE_VERTICAL_CARDS:
            self.AdjustForScrolling(numAvailableChildren)

    def ConstructLayout(self):
        self.ConstructMainContainer()

    def ConstructMainContainer(self):
        padding = 20
        self.clippingParent = ContainerAutoSize(name='clippingParent', parent=self, align=uiconst.CENTERTOP, height=self.mainContHeight, maxWidth=MAX_VISIBLE_VERTICAL_CARDS * (VERTICAL_CARD_WIDTH + padding), clipChildren=True)
        self.mainCont = LayoutGrid(parent=self.clippingParent, align=uiconst.TOLEFT, cellSpacing=(0, 50), cellPadding=(padding / 2, 20), top=self.clippingParentTop)
        self.scrollIndicator = Fill(parent=self, frameConst=uiconst.FRAME_BORDER1_CORNER9, pos=(0, -6, 0, 6), align=uiconst.BOTTOMLEFT, opacity=0.05)
        self.scrollIndicator.baseOpacity = 0.05
        self.scrollIndicator.display = False

    def GetOffsetValue(self, idx):
        numChildren = len(self.cards)
        return math.fabs((numChildren - 1) / 2.0 - idx)

    def _ConstructContentGroupCard(self, contentGroup, index):
        cardContainer = ContentGroupCardContainer(parent=self.mainCont, contentGroup=contentGroup, index=index)
        self.cards.append(cardContainer)

    def AdjustForScrolling(self, numAvailableChildren):
        padding = 23
        numFullCards = MAX_VISIBLE_VERTICAL_CARDS - 1
        self.clippingParent.maxWidth = numFullCards * (VERTICAL_CARD_WIDTH + padding) + self.extraSlotWidth
        self.clippingParent.alignMode = uiconst.CENTERLEFT
        self.clippingParent.minHeight = EDGE_GRADIENT_HEIGHT
        self.mainCont.cellPadding = (padding / 2, self.mainCont.cellPadding[1])
        self.mainCont.align = uiconst.CENTERLEFT
        self.mainCont.top = 10
        self.mainCont.state = uiconst.UI_NORMAL
        self.contentScroller = ContentScroller(self.contentGroup.contentGroupID, self.mainCont, numAvailableCards=numAvailableChildren, numVisibleCards=numFullCards, slotSize=VERTICAL_CARD_WIDTH + padding, extraSlotWidth=self.extraSlotWidth, scrollIndicator=self.scrollIndicator)
        self.contentScroller.onUpdate.connect(self.UpdateFade)
        for each in [self.mainCont] + [ x.card for x in self.cards ]:
            each.OnMouseDown = (self.contentScroller.OnMouseDown, each)
            each.OnMouseUp = self.contentScroller.OnMouseUp
            each.OnMouseWheel = self.contentScroller.OnMouseWheel

        self.ConstructGradients()

    def ConstructGradients(self):
        if not getattr(self, 'leftFadeCont', None) or self.leftFadeCont.destroyed:
            self.leftFadeCont = Container(name='leftFadeCont', parent=self.clippingParent, align=uiconst.TOLEFT_NOPUSH, width=EDGE_GRADIENT_WIDTH, clipChildren=True, idx=0)
            self.leftFade = Sprite(name='scrollGradientLeft', parent=self.leftFadeCont, align=uiconst.CENTERLEFT, pos=(0,
             0,
             EDGE_GRADIENT_WIDTH,
             EDGE_GRADIENT_HEIGHT), rotation=mathext.pi, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/agency/scrollGradient3.png', idx=0, color=(0, 0, 0, 1))
            self.leftFade.display = False
        if not getattr(self, 'rightFadeCont', None) or self.rightFadeCont.destroyed:
            self.rightFadeCont = Container(name='rightFadeCont', parent=self.clippingParent, align=uiconst.TORIGHT_NOPUSH, width=EDGE_GRADIENT_WIDTH, clipChildren=True, idx=0)
            self.rightFade = Sprite(name='scrollGradientRight', parent=self.rightFadeCont, align=uiconst.CENTERRIGHT, pos=(0,
             0,
             EDGE_GRADIENT_WIDTH,
             EDGE_GRADIENT_HEIGHT), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/agency/scrollGradient3.png', idx=0, color=(0, 0, 0, 1))
            self.rightFade.display = False

    def UpdateFade(self, newLeft, firstIdx, lastIdx, cardWidth):
        animations.StopAnimation(self.mainCont, 'left')
        self.mainCont.left = newLeft
        currentLeftOffSet = self.clippingParent.absoluteLeft - self.mainCont.absoluteLeft
        correction = int(currentLeftOffSet + newLeft)
        showLeft = showRight = False
        for cardContainer in self.cards:
            if cardContainer.card.index == firstIdx:
                cardLeft = cardContainer.absoluteLeft
                fromEdge = self.clippingParent.absoluteLeft - cardLeft - correction
                showLeft = fromEdge > -10
                diff = cardWidth - fromEdge
                self.leftFadeCont.width = diff - 10 if diff < EDGE_GRADIENT_WIDTH else EDGE_GRADIENT_WIDTH
            if cardContainer.card.index == lastIdx:
                cardRight = cardContainer.absoluteRight
                fromEdge = cardRight - self.clippingParent.absoluteRight + correction
                diff = cardWidth - fromEdge
                self.rightFadeCont.width = diff - 10 if diff < EDGE_GRADIENT_WIDTH else EDGE_GRADIENT_WIDTH
                showRight = fromEdge > -10

        self.leftFade.display = showLeft
        self.rightFade.display = showRight

    def Close(self):
        with ExceptionEater('Killing contentScroller'):
            if self.contentScroller:
                self.contentScroller.onUpdate.disconnect(self.UpdateFade)
                self.contentScroller.Cleanup()
        ContainerAutoSize.Close(self)


class ContentGroupCardContainer(ContainerAutoSize):
    default_name = 'ContentGroupCardContainer'
    default_align = uiconst.CENTERTOP
    default_width = contentGroupCardConstants.VERTICAL_CARD_WIDTH

    def ApplyAttributes(self, attributes):
        super(ContentGroupCardContainer, self).ApplyAttributes(attributes)
        self.contentGroup = attributes.contentGroup
        self.index = attributes.index
        self.ConstructLayout()

    def ConstructLayout(self):
        self.ConstructContentGroupCard()
        self.ConstructContentGroupInfoContainer()
        self.ConstructDescriptionIcon()
        if self.contentGroup.IsGroupContent():
            self.ConstructGroupContentIcon()

    def ConstructGroupContentIcon(self):
        Sprite(name='groupContentSprite', parent=self.contentGroupInfoContainer, align=uiconst.CENTERLEFT, texturePath='res:/UI/Texture/classes/agency/iconGroupActivity.png', width=32, height=32, left=32, hint=GetByLabel('UI/Agency/Tooltips/NavigationCards/GroupContentHint'))

    def ConstructContentGroupInfoContainer(self):
        self.contentGroupInfoContainer = Container(name='contentGroupInfoContainer', parent=self, align=uiconst.TOTOP, height=VERTICAL_CARD_BOTTOM_CONTAINER_HEIGHT)

    def ConstructDescriptionIcon(self):
        self.descriptionIcon = DescriptionIcon(parent=self.contentGroupInfoContainer, align=uiconst.CENTERLEFT, tooltipPanelClassInfo=SimpleTextTooltip(text=self.contentGroup.GetContentGroupHint()))

    def ConstructContentGroupCard(self):
        contentGroupID = self.contentGroup.contentGroupID
        contentGroupCardClass = contentGroupCardProvider.GetContentGroupCardCls(contentGroupID)
        self.card = contentGroupCardClass(name='%sNavigationCard' % self.contentGroup.GetInternalName().replace(' ', ''), parent=self, contentGroup=self.contentGroup, contentGroupID=contentGroupID, index=self.index)

    def AnimEnter(self, offsetValue):
        self.card.AnimEnter(offsetValue)
        self.descriptionIcon.AnimEnter(offsetValue)
