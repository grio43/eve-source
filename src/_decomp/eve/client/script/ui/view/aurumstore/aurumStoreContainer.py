#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\aurumstore\aurumStoreContainer.py
import collections
import logging
import math
import carbonui.const as uiconst
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.primitives.gridcontainer import GridContainer
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from eve.client.script.ui.shared.redeem.redeemPanel import GetOldRedeemPanel
from eve.client.script.ui.shared.vgs.currency import OFFER_CURRENCY_SORT_ORDER
from eve.common.lib.vgsConst import CATEGORYTAG_GEM
from eve.client.script.ui.plex.textures import PLEX_32_SOLID_YELLOW
from eve.client.script.ui.util.focusUtil import postponeUntilFocus
from eve.client.script.ui.util.uiComponents import RunThreadOnce
from eve.client.script.ui.view.aurumstore.vgsOffer import Ribbon
from eve.client.script.ui.view.aurumstore.vgsOfferFilterBar import VgsOfferFilterBar
from eve.client.script.ui.view.aurumstore.vgsOfferGrid import OfferGrid
from eve.client.script.ui.view.aurumstore.vgsOfferScrollContainer import OfferScrollContainer
from eve.client.script.ui.view.aurumstore.vgsUiConst import BACKGROUND_COLOR, CONTENT_PADDING, MAX_CONTENT_WIDTH, REDEEM_BUTTON_BACKGROUND_COLOR, REDEEM_BUTTON_FILL_COLOR
from eve.client.script.ui.view.aurumstore.vgsUiPrimitives import AurLabelHeader, CategoryButton, CATEGORY_COLOR, ExitButton, GemLabelHeader, LogoHomeButton, SubCategoryButton, TAG_COLOR, VgsFilterCombo
from eve.client.script.ui.view.viewStateConst import ViewState
from fastcheckout.client.purchasepanels.purchaseButton import PurchaseButton
from fastcheckout.const import FROM_NES_HEADER
from localization import GetByLabel
from localization.util import Sort
logger = logging.getLogger(__name__)
HEADER_HEIGHT = 100
HEADER_PADDING = 2
CATEGORIES_HEIGHT = 36
AD_HEIGHT = 256
CAPTION_HEIGHT = 34
CAPTION_OFFSET = 30
SEARCH_BOX_WIDTH = 300
CONTENT_SLIP_UNDER_AREA_OPACITY = 0.8
BG_WIDTH = 2117
BG_HEIGHT = 1200
BUY_CURRENCY_BUTTON_WIDTH = 106
BUY_CURRENCY_BUTTON_HEIGHT = 30
BUY_CURRENCY_BUTTON_LEFT = 6
BUY_CURRENCY_BUTTON_FONTSIZE = 18
BUY_CURRENCY_FONTSIZE = 27
BUY_CURRENCY_ICONSIZE = 32
BUY_CURRENCY_TEXT_MARGIN = 10
BUY_CURRENCY_ICON_MARGIN = 8
SORT_PRICE_ASCENDING = 1
SORT_PRICE_DESCENDING = 2
SORT_NAME_ASCENDING = 3
SORT_NAME_DESCENDING = 4
DEFAULT_SORT_SELECTION = SORT_NAME_ASCENDING
PAGE_HOME = 1
PAGE_CATEGORY = 2
PAGE_SUBCATEGORY = 3
PAGE_SEARCH = 4
ROOT_CATEGORY_SHIP_SKINS = 1
ROOT_CATEGORY_APPAREL = 3
ROOT_CATEGORY_SERVICES = 21
THREAD_KEY_LOAD_PAGE = 'VGS.LoadPage'
KEY_OFFER = 'offer'
KEY_OFFERS = 'offers'
KEY_HAS_QUANTITY = 'hasQuantity'
KEY_QUANTITY = 'quantity'
ProductOffer = collections.namedtuple('ProductOffer', ['url',
 'title',
 'image',
 'cost'])
SubCategory = collections.namedtuple('SubCategory', ['id', 'title'])

def SortByPrice(offers, ascending):

    def get_sort_order_for_price(offer):
        prices = []
        for pricing in offer.offerPricings:
            sort_order = OFFER_CURRENCY_SORT_ORDER.get(pricing.currency, 0)
            prices.append((sort_order, pricing.price))

        return max(prices)

    return sorted(offers, key=get_sort_order_for_price, reverse=not ascending)


def SortByName(offers, ascending):
    numericGroupData, nameGroupData = GetOffersGroupData(offers)
    sortedNumericGroupData = sorted(numericGroupData.keys())
    sortedNameGroupData = sorted(nameGroupData.keys())
    allSortedOffers = []
    for groupName in sortedNumericGroupData:
        offerData = []
        for offer in numericGroupData[groupName][KEY_OFFERS]:
            isBundle = len(offer.productQuantities) > 1
            for entry in offer.productQuantities.values():
                offerData.append({KEY_OFFER: offer,
                 KEY_QUANTITY: 1 if isBundle else entry.quantity})
                break

        sortedOfferData = sorted(offerData, key=lambda o: o[KEY_QUANTITY])
        for data in sortedOfferData:
            allSortedOffers.append(data[KEY_OFFER])

    for groupName in sortedNameGroupData:
        sortedOfferData = sorted(nameGroupData[groupName][KEY_OFFERS], key=lambda o: o.name)
        for data in sortedOfferData:
            allSortedOffers.append(data)

    if not ascending:
        allSortedOffers.reverse()
    return allSortedOffers


def GetOffersGroupData(offers):
    PRODUCT_IDS = [2113,
     4513,
     2459,
     1600,
     3307]
    numericGroupData = {}
    nameGroupData = {}
    for offer in offers:
        offerName = offer.name
        hasQuantity = False
        for productID in offer.productQuantities.keys():
            if productID in PRODUCT_IDS:
                offerName = str(PRODUCT_IDS.index(productID))
                hasQuantity = True
            break

        if hasQuantity:
            if offerName in numericGroupData:
                numericGroupData.get(offerName)[KEY_OFFERS].append(offer)
            else:
                numericGroupData[offerName] = {KEY_OFFERS: [offer],
                 KEY_HAS_QUANTITY: hasQuantity}
        elif offerName in nameGroupData:
            nameGroupData.get(offerName)[KEY_OFFERS].append(offer)
        else:
            nameGroupData[offerName] = {KEY_OFFERS: [offer],
             KEY_HAS_QUANTITY: hasQuantity}

    return (numericGroupData, nameGroupData)


def GetSortOrder():
    return settings.user.ui.Get('VgsOfferSortOrder', DEFAULT_SORT_SELECTION)


def SortOffers(offers):
    offerOrder = GetSortOrder()
    sortedOffers = offers
    if offerOrder == SORT_PRICE_DESCENDING:
        sortedOffers = SortByPrice(offers, False)
    elif offerOrder == SORT_PRICE_ASCENDING:
        sortedOffers = SortByPrice(offers, True)
    elif offerOrder == SORT_NAME_DESCENDING:
        sortedOffers = SortByName(offers, False)
    elif offerOrder == SORT_NAME_ASCENDING:
        sortedOffers = SortByName(offers, True)
    return sortedOffers


class Tag:

    def __init__(self, tagId, name):
        self.id = tagId
        self.name = name


class AurumStoreContainer(Container):
    default_name = 'AurumStoreContainer'
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        self.is_ready = False
        Container.ApplyAttributes(self, attributes)
        self.store = attributes.store
        self.tagsByCategoryId = {}
        self.selectedRootCategoryId = None
        self.selectedCategoryId = None
        self.selectedCurrency = None
        self.activeTagsByRootCategoryId = {}
        self.aurumStoreWindow = None
        self.page = None
        self.category = None
        self.subCategory = None
        self.subcategoryButtons = []
        self.fastCheckoutService = sm.GetService('fastCheckoutClientService')
        self.vgsService = sm.GetService('vgsService')
        self.viewStateService = sm.GetService('viewState')
        self.featuredOfferIDs = self.vgsService.GetFeaturedOffers()
        Fill(bgParent=self, color=(0.0, 0.0, 0.0, 1.0))
        self.CreateRedeemingPanelLayout()
        self.CreateBaseLayout()
        self.CreateHeaderLayout()
        self.CreateContentLayout()
        self.SetFilterOptions()
        self.currentAurBalance = 0
        self.currentGemBalance = 0
        self.is_ready = True
        self._OnResize()

    def _OnResize(self, *args):
        if not self.is_ready:
            return
        self.PositionBackgroundTexture()
        top, left, width, height = self.GetAbsolute()
        contentWidth = min(MAX_CONTENT_WIDTH, width)
        self.leftContainer.width = (width - contentWidth) / 2
        self.contentContainer.width = contentWidth
        self.rightContainer.width = width - self.leftContainer.width - contentWidth
        self.redeemingPanel.width = width
        self.SetSidebarContentMask()

    def CreateHeaderLayout(self):
        self._AddGems()
        self._AddPlex()
        LogoHomeButton(parent=self.headerContainer, align=uiconst.TOPLEFT, onClick=self.OnClickHomeButton)
        ExitButton(parent=self.headerContainer, align=uiconst.TOPRIGHT, onClick=lambda : self.exit_vgs(), top=4, left=10, hint=GetByLabel('UI/VirtualGoodsStore/ExitStore'))

    def _AddGems(self):
        gemsContainer = Container(name='GemsContainer', parent=self.headerContainer, align=uiconst.TOTOP, height=CAPTION_HEIGHT, top=CAPTION_OFFSET)
        gemsContainer.Hide()
        buttonContainer = ContainerAutoSize(name='BuyGemsButtonContainer', parent=gemsContainer, align=uiconst.TORIGHT, width=BUY_CURRENCY_BUTTON_WIDTH + BUY_CURRENCY_BUTTON_LEFT, left=BUY_CURRENCY_BUTTON_LEFT)
        self.buyGemBtn = PurchaseButton(name='NES_BuyGemsButton', parent=buttonContainer, align=uiconst.CENTERRIGHT, width=BUY_CURRENCY_BUTTON_WIDTH, height=BUY_CURRENCY_BUTTON_HEIGHT, text=GetByLabel('UI/VirtualGoodsStore/BuyGemOnline'), fontsize=BUY_CURRENCY_BUTTON_FONTSIZE, func=self._BuyGem)
        self.gemLabel = GemLabelHeader(name='Label', parent=gemsContainer, align=uiconst.TORIGHT, amount=100, padRight=BUY_CURRENCY_TEXT_MARGIN, shouldUseUnits=False, amountSize=BUY_CURRENCY_FONTSIZE)
        iconContainer = Container(name='BuyGemsIconContainer', parent=gemsContainer, align=uiconst.TORIGHT, width=BUY_CURRENCY_ICONSIZE, padRight=BUY_CURRENCY_ICON_MARGIN)
        Sprite(name='GemsIcon', parent=iconContainer, texturePath='res:/UI/Texture/Vgs/quantum_pricetag32.png', width=BUY_CURRENCY_ICONSIZE, height=BUY_CURRENCY_ICONSIZE, align=uiconst.CENTER)
        if self.fastCheckoutService.is_china_funnel():
            gemsContainer.Show()
            gemsContainer.top = 25

    def _AddPlex(self):
        plexContainer = Container(name='PlexContainer', parent=self.headerContainer, align=uiconst.TOTOP, height=CAPTION_HEIGHT, top=CAPTION_OFFSET)
        buttonContainer = ContainerAutoSize(name='BuyPlexButtonContainer', parent=plexContainer, align=uiconst.TORIGHT, width=BUY_CURRENCY_BUTTON_WIDTH + BUY_CURRENCY_BUTTON_LEFT, left=BUY_CURRENCY_BUTTON_LEFT)
        self.buyPlexBtn = PurchaseButton(name='NES_BuyPlexButton', parent=buttonContainer, align=uiconst.CENTERRIGHT, width=BUY_CURRENCY_BUTTON_WIDTH, height=BUY_CURRENCY_BUTTON_HEIGHT, text=GetByLabel('UI/VirtualGoodsStore/BuyAurOnline'), fontsize=BUY_CURRENCY_BUTTON_FONTSIZE, func=self._BuyPlex)
        self.aurLabel = AurLabelHeader(name=pConst.UNIQUE_NAME_NEW_EDEN_STORE_PLEX_AMOUNT, parent=plexContainer, align=uiconst.TORIGHT, amount=100, padRight=BUY_CURRENCY_TEXT_MARGIN, shouldUseUnits=False, amountSize=BUY_CURRENCY_FONTSIZE, uniqueUiName=pConst.UNIQUE_NAME_NEW_EDEN_STORE_PLEX_AMOUNT)
        iconContainer = Container(name='BuyPlexIconContainer', parent=plexContainer, align=uiconst.TORIGHT, width=BUY_CURRENCY_ICONSIZE)
        Sprite(name='PlexIcon', parent=iconContainer, texturePath=PLEX_32_SOLID_YELLOW, width=BUY_CURRENCY_ICONSIZE, height=BUY_CURRENCY_ICONSIZE, align=uiconst.CENTER)
        if self.fastCheckoutService.is_china_funnel():
            plexContainer.top = 2

    def exit_vgs(self):
        if self.aurumStoreWindow:
            self.aurumStoreWindow.CloseIfOpen()
        uicore.cmd.ToggleAurumStore()

    def _BuyPlex(self):
        uicore.cmd.CmdBuyPlex(logContext=FROM_NES_HEADER)

    def _BuyGem(self):
        self.SelectCategoryByCategoryTag(CATEGORYTAG_GEM)

    def SetSidebarContentMask(self):
        for container in (self.leftContainer, self.rightContainer):
            container.Flush()
            GradientSprite(name='OfferSlipGradient', align=uiconst.TOTOP, parent=container, rgbData=((0.0, BACKGROUND_COLOR[:3]),), alphaData=((0.0, CONTENT_SLIP_UNDER_AREA_OPACITY), (0.5, 1.0), (1.0, 1.0)), height=self.topContainer.height + self.filterContainer.height + HEADER_PADDING, rotation=math.pi / 2)

    def CreateBaseLayout(self):
        self.wholeWidthContainer = Container(parent=self, name='WholeWindowContainer', align=uiconst.TOALL)
        self.CreateBackgroundTexture()
        self.leftContainer = Container(parent=self.wholeWidthContainer, name='LeftSideBar', align=uiconst.TOLEFT, opacity=0.0)
        self.rightContainer = Container(parent=self.wholeWidthContainer, name='RightSideBar', align=uiconst.TORIGHT, opacity=0.0)
        self.contentContainer = Container(parent=self.wholeWidthContainer, name='Content', align=uiconst.TOLEFT)
        self.topContainer = ContainerAutoSize(name='Top Container', parent=self.contentContainer, align=uiconst.TOTOP)
        Fill(name='SlipUnderLayer', bgParent=self.topContainer, color=BACKGROUND_COLOR)
        self.headerContainer = Container(parent=self.topContainer, name='Header', align=uiconst.TOTOP, bgColor=(0.0, 0.0, 0.0, 1.0), height=HEADER_HEIGHT, clipChildren=True)
        self.categoryContainer = Container(parent=self.topContainer, name='Categories', align=uiconst.TOTOP, height=CATEGORIES_HEIGHT, padTop=HEADER_PADDING, state=uiconst.UI_PICKCHILDREN)
        self.subCategoryContainer = Container(name='SubCategories', parent=self.topContainer, align=uiconst.TOTOP, padTop=HEADER_PADDING, bgColor=TAG_COLOR, state=uiconst.UI_PICKCHILDREN, clipChildren=True)
        self.subCategoryButtonContainer = FlowContainer(name='SubCategoryButtons', parent=self.subCategoryContainer, centerContent=True, align=uiconst.TOTOP, contentSpacing=(1, 0), state=uiconst.UI_PICKCHILDREN)
        self.filterContainer = Container(name='Filter', parent=self.contentContainer, align=uiconst.TOTOP, padTop=HEADER_PADDING, state=uiconst.UI_PICKCHILDREN, height=CATEGORIES_HEIGHT)

    def CreateBackgroundTexture(self):
        self.nesBackground = Sprite(parent=self, name='NESBackground', texturePath='res:/UI/Texture/Vgs/background.png', align=uiconst.CENTER, state=uiconst.UI_DISABLED)
        self.PositionBackgroundTexture()

    def PositionBackgroundTexture(self):
        clientHeight = uicore.desktop.height
        percentOfClientHeight = float(clientHeight) / BG_HEIGHT
        if clientHeight < BG_HEIGHT:
            newHeight = BG_HEIGHT
            newWidth = BG_WIDTH
        else:
            newHeight = clientHeight
            newWidth = int(percentOfClientHeight * BG_WIDTH)
        self.nesBackground.pos = (0,
         0,
         newWidth,
         newHeight)

    def CreateContentLayout(self):
        self.contentScroll = OfferScrollContainer(parent=self.contentContainer, align=uiconst.TOALL)
        self.grid = OfferGrid(parent=self.contentScroll, align=uiconst.TOTOP, contentSpacing=(CONTENT_PADDING, CONTENT_PADDING), padBottom=CONTENT_PADDING)
        self.contentScroll.RegisterContentLoader(self.grid)

    def CreateRedeemingPanelLayout(self):
        instructionText = '<url=localsvc:method=ShowRedeemUI>%s</url>' % (GetByLabel('UI/RedeemWindow/ClickToInitiateRedeeming'),)
        redeemPanelClass = GetOldRedeemPanel()
        self.redeemingPanel = redeemPanelClass(parent=self, align=uiconst.TOBOTTOM, dragEnabled=False, instructionText=instructionText, redeemButtonBackgroundColor=REDEEM_BUTTON_BACKGROUND_COLOR, redeemButtonFillColor=REDEEM_BUTTON_FILL_COLOR)
        self.redeemingPanel.UpdateDisplay()

    def _SelectCategory(self, categoryId):
        self.selectedRootCategoryId = categoryId
        for button in self.categoryButtons:
            if button.isActive and button.categoryId != categoryId:
                button.SetActive(False)
            elif button.categoryId == categoryId:
                button.SetActive(True)

    def _SelectSubCategory(self, subcategoryId):
        self.selectedCategoryId = subcategoryId
        for button in self.subcategoryButtons:
            if button.isActive and button.categoryId != subcategoryId:
                button.SetActive(False)
            elif button.categoryId == subcategoryId:
                button.SetActive(True)

    def OnClickCategory(self, categoryId):
        self.LoadCategoryPage(categoryId)

    @RunThreadOnce(THREAD_KEY_LOAD_PAGE)
    def LoadCategoryPage(self, categoryId):
        if self.page == PAGE_CATEGORY and self.selectedRootCategoryId == categoryId and self.selectedCategoryId is None:
            return
        logger.debug('Loading category page: %s', categoryId)
        self.page = PAGE_CATEGORY
        self._SelectCategory(categoryId)
        self.ConstructSubCategoryButtons(categoryId)
        self._SelectSubCategory(None)
        self.SetOffersAndTags(categoryId)
        self.category = categoryId
        self.subCategory = None
        self._NotifyStorePageLoaded()

    def GetSubCategories(self, categoryId):
        if categoryId is None:
            return
        categoriesById = self.store.GetCategories()
        category = categoriesById[categoryId]
        subcategories = [ categoriesById[subCatId] for subCatId in category.subcategories ]
        subcategories = Sort(subcategories, key=lambda c: c.name)
        return subcategories

    def OnClickSubCategory(self, subcategoryId):
        self.LoadSubCategoryPage(subcategoryId)

    def SelectCategory(self, categoryId):
        if categoryId in self.store.GetRootCategoryList():
            self.LoadCategoryPage(categoryId)
        else:
            self.LoadSubCategoryPage(categoryId)

    def SelectCategoryByCategoryTag(self, categoryTag):
        categoryId = self.store.GetCategoryIdByCategoryTag(categoryTag)
        self.SelectCategory(categoryId)

    @RunThreadOnce(THREAD_KEY_LOAD_PAGE)
    def LoadSubCategoryPage(self, subcategoryId):
        if self.page == PAGE_SUBCATEGORY and self.selectedCategoryId == subcategoryId:
            return
        logger.debug('Loading sub category page: %s', subcategoryId)
        self.page = PAGE_SUBCATEGORY
        self.selectedCategoryId = subcategoryId
        self.SetOffersAndTags(subcategoryId)
        rootCategoryId = self.store.GetCategories()[subcategoryId].parentId
        self._ConstructSubCategoryButtons(rootCategoryId)
        self._SelectCategory(rootCategoryId)
        self._SelectSubCategory(subcategoryId)
        self.subCategory = subcategoryId
        self._NotifyStorePageLoaded()

    def SetOffersAndTags(self, categoryId):
        tags = self.store.GetTagsByCategoryId(categoryId)
        self.SetFilterTags(tags)
        tagIds = self.filterBar.GetSelectedFilterTagIds()
        offers = self.store.GetFilteredOffers(categoryId, None, tagIds)
        self.SetOffers(offers)

    @RunThreadOnce(THREAD_KEY_LOAD_PAGE)
    def OnClickHomeButton(self):
        self.LoadLandingPage()

    def LoadLandingPage(self):
        logger.debug('LoadLandingPage')
        if self.page == PAGE_HOME:
            return
        logger.debug('Loading landing page')
        self.page = PAGE_HOME
        self._ConstructSubCategoryButtons(None)
        self._SelectCategory(None)
        self._SelectSubCategory(None)
        self.SetFilterTags([])
        offers = self.store.GetOffers().values()
        self.SetOffers(offers)
        self.category = None
        self.subCategory = None
        self._NotifyStorePageLoaded()

    def __find_button_label(self, button_list, category_id):
        for button in button_list:
            if button.categoryId == category_id:
                return button.name

    def _NotifyStorePageLoaded(self):
        page_name = None
        if self.page == 1:
            page_name = 'LogoHomeButton'
        elif self.page == 2:
            page_name = self.__find_button_label(self.categoryButtons, self.category)
        elif self.page == 3:
            page_name = self.__find_button_label(self.subcategoryButtons, self.subCategory)
        sm.ScatterEvent('OnNESPageLoaded', page_name)

    @postponeUntilFocus
    def SetAUR(self, amount, *args, **kwargs):
        logger.debug('SetAUR %s', amount)
        uicore.animations.MorphScalar(self, 'currentAurBalance', startVal=self.currentAurBalance, endVal=amount, curveType=uiconst.ANIM_SMOOTH, duration=1.5, callback=lambda : self.SetCurrentAurBalance(amount))

    def SetCurrentAurBalance(self, amount):
        self._currentAurBalance = amount
        if not self.destroyed:
            self.aurLabel.SetAmount(self._currentAurBalance)

    def GetCurrentAurBalance(self):
        return self._currentAurBalance

    currentAurBalance = property(GetCurrentAurBalance, SetCurrentAurBalance)

    @postponeUntilFocus
    def SetGEM(self, amount):
        logger.debug('SetGEM %s', amount)
        uicore.animations.MorphScalar(self, 'currentGemBalance', startVal=self.currentGemBalance, endVal=amount, curveType=uiconst.ANIM_SMOOTH, duration=1.5, callback=lambda : self.SetCurrentGemBalance(amount))

    def SetCurrentGemBalance(self, amount):
        self._currentGemBalance = amount
        if not self.destroyed:
            self.gemLabel.SetAmount(self._currentGemBalance)

    def GetCurrentGemBalance(self):
        return self._currentGemBalance

    currentGemBalance = property(GetCurrentGemBalance, SetCurrentGemBalance)

    def SetCategories(self, categories):
        logger.debug('SetCategories %s', categories)
        self.categoryContainer.Flush()
        searchContainer = Container(name='SearchBox', parent=self.categoryContainer, width=SEARCH_BOX_WIDTH, align=uiconst.TORIGHT)
        categoryButtonsContainer = GridContainer(name='ButtonGrid', parent=self.categoryContainer, align=uiconst.TOALL, columns=len(categories), lines=1)
        tagById = self.store.GetTags()
        self.categoryButtons = []
        for category in categories:
            button = CategoryButton(parent=categoryButtonsContainer, categoryId=category.id, label=category.name, align=uiconst.TOALL, onClick=self.OnClickCategory, padRight=1, name='CategoryButton_{}'.format(category.id))
            self.categoryButtons.append(button)
            tags = []
            for tagId in category.tagIds:
                tag = tagById.get(tagId)
                if tag:
                    tags.append(Tag(tag.id, tag.name))

            self.tagsByCategoryId[category.id] = tags

        iconContainer = Container(name='SearchIconContainer', parent=searchContainer, width=CATEGORIES_HEIGHT, align=uiconst.TOLEFT, bgColor=CATEGORY_COLOR)
        Sprite(parent=iconContainer, texturePath='res:/UI/Texture/Vgs/Search_icon.png', width=32, height=32, align=uiconst.CENTER)
        self.searchEdit = SingleLineEditText(parent=searchContainer, align=uiconst.TORIGHT, pos=(0,
         0,
         SEARCH_BOX_WIDTH - CATEGORIES_HEIGHT - 2,
         0), fontsize=16, padding=(1, 0, 0, 0), OnChange=self.LoadSearchPage, bgColor=TAG_COLOR)
        self.searchEdit.ShowClearButton(icon='res:/UI/Texture/Icons/73_16_45.png')
        self.searchEdit.SetHistoryVisibility(False)
        self.searchEdit.underlay.Hide()

    @RunThreadOnce(THREAD_KEY_LOAD_PAGE)
    def LoadSearchPage(self, searchString):
        if len(searchString) > 0:
            self.page = PAGE_SEARCH
            self._SelectSubCategory(None)
            self._SelectCategory(None)
            self._ConstructSubCategoryButtons(None)
            self.SetFilterTags([])
            self.viewStateService.GetView(ViewState.VirtualGoodsStore).Search(searchString)
        else:
            self.LoadLandingPage()

    @RunThreadOnce(THREAD_KEY_LOAD_PAGE)
    def LoadTypeIdPage(self, typeIds):
        self.page = PAGE_SEARCH
        self._SelectSubCategory(None)
        self._SelectCategory(None)
        self._ConstructSubCategoryButtons(None)
        self.SetFilterTags([])
        offers = self.store.SearchOffersByTypeIDs(typeIds)
        if len(offers) == 1:
            offer = offers[0]
            categoryId = self.store.GetSubCategoryId(offer.categories)
            self.vgsService.ShowOffer(offer.id, categoryId)
        else:
            self.SetOffers(offers)

    @RunThreadOnce('VGS.SetSubCategories')
    def ConstructSubCategoryButtons(self, categoryId):
        self._ConstructSubCategoryButtons(categoryId)

    def _ConstructSubCategoryButtons(self, categoryId):
        subcategories = self.GetSubCategories(categoryId)
        self.subCategoryButtonContainer.Flush()
        self.subcategoryButtons = []
        if subcategories is None:
            if self.subCategoryContainer.height > 0:
                uicore.animations.MorphScalar(self.subCategoryContainer, attrName='height', startVal=self.subCategoryContainer.height, endVal=0, duration=0.5, callback=self.SetSidebarContentMask)
        else:
            if int(self.subCategoryContainer.height) != CATEGORIES_HEIGHT:
                uicore.animations.MorphScalar(self.subCategoryContainer, attrName='height', startVal=self.subCategoryContainer.height, endVal=CATEGORIES_HEIGHT, duration=0.5, sleep=False, callback=self.SetSidebarContentMask)
            for subcategory in subcategories:
                button = SubCategoryButton(parent=self.subCategoryButtonContainer, label=subcategory.name, align=uiconst.NOALIGN, height=CATEGORIES_HEIGHT, categoryId=subcategory.id, onClick=self.OnClickSubCategory, name='SubCategoryButton_{}'.format(subcategory.id))
                self.subcategoryButtons.append(button)

    def SetOffers(self, offers):
        offersToDisplay = []
        featuredOffersToDisplay = []
        for offer in offers:
            if not offer.canPurchase:
                continue
            if offer.id in self.featuredOfferIDs:
                featuredOffersToDisplay.append(offer)
            else:
                offersToDisplay.append(offer)

        regularOffers = []
        specialOffers = {}
        for o in offersToDisplay:
            if o.label is not None:
                labelName = o.label.name
                if labelName not in Ribbon.SORTING:
                    logger.error('Unknown VGS offer label name %s for offer ID %d' % (labelName, o.id))
                    continue
                if labelName not in specialOffers:
                    specialOffers[labelName] = [o]
                else:
                    specialOffers[labelName].append(o)
            else:
                regularOffers.append(o)

        orderedOffers = []
        if featuredOffersToDisplay:
            orderedOffers.extend(SortOffers(featuredOffersToDisplay))
        for offerLabel in Ribbon.SORTING:
            if offerLabel in specialOffers:
                orderedOffers.extend(SortOffers(specialOffers[offerLabel]))

        orderedOffers.extend(SortOffers(regularOffers))
        self.grid.SetOffers(orderedOffers, show_skinr_banner=self.should_show_skinr_banner)

    def SetFilterOptions(self):
        self.filterContainer.Flush()
        Fill(name='SlipUnderLayer', bgParent=self.filterContainer, color=(0.25, 0.25, 0.25, 1.0), opacity=CONTENT_SLIP_UNDER_AREA_OPACITY, padTop=-HEADER_PADDING * 2)
        options = [(GetByLabel('UI/VirtualGoodsStore/Sorting/ByPriceAscending'), SORT_PRICE_ASCENDING),
         (GetByLabel('UI/VirtualGoodsStore/Sorting/ByPriceDescending'), SORT_PRICE_DESCENDING),
         (GetByLabel('UI/VirtualGoodsStore/Sorting/ByNameAscending'), SORT_NAME_ASCENDING),
         (GetByLabel('UI/VirtualGoodsStore/Sorting/ByNameDescending'), SORT_NAME_DESCENDING)]
        self.filterCombo = VgsFilterCombo(parent=self.filterContainer, align=uiconst.TORIGHT, options=options, callback=self.OnSortOrderChanged, select=GetSortOrder(), padding=(4, 2, 0, 4))
        self.filterBar = VgsOfferFilterBar(parent=self.filterContainer, onFilterChanged=self.OnFilterChanged)

    def SetFilterTags(self, tags):
        activeTags = self.activeTagsByRootCategoryId.get(self.GetSelectedRootCategoryId(), {})
        self.subCategoryContainer.state = uiconst.UI_PICKCHILDREN
        self.filterBar.SetTags(tags, activeTags)

    def OnSortOrderChanged(self, combo, key, value):
        settings.user.ui.Set('VgsOfferSortOrder', value)
        self.viewStateService.GetView(ViewState.VirtualGoodsStore)._LogFilterChange(value)
        self.SetOffers(self.grid.GetOffers())

    def OnFilterChanged(self):
        tagIds = self.filterBar.GetSelectedFilterTagIds()
        rootCategoryId = self.GetSelectedRootCategoryId()
        self.activeTagsByRootCategoryId[rootCategoryId] = tagIds
        filterCategory = self.selectedCategoryId or rootCategoryId
        filterCurrency = self.selectedCurrency
        offers = self.store.GetFilteredOffers(filterCategory, filterCurrency, tagIds)
        self.SetOffers(offers)

    def GetSelectedCategoryId(self):
        return self.selectedCategoryId

    def GetSelectedRootCategoryId(self):
        return self.selectedRootCategoryId

    def OnMouseWheel(self, dz, *args):
        self.contentScroll.OnMouseWheel(dz)

    def OnOfferPurchase(self, offerID):
        if not self.store.GetOffer(offerID).canPurchase:
            self.grid.RemoveOffer(offerID, show_skinr_banner=self.should_show_skinr_banner)

    def SetFeaturedOffers(self, offerIDs):
        self.featuredOfferIDs = offerIDs or []
        self.SetOffers(self.grid.GetOffers())

    @property
    def should_show_skinr_banner(self):
        if session.charid is None:
            return False
        elif self.page == PAGE_HOME:
            return True
        elif self.selectedRootCategoryId == ROOT_CATEGORY_SHIP_SKINS:
            return True
        else:
            return False
