#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\aurumstore\vgsOffer.py
import blue
import industry
import itertools
import logging
import math
import signals
import uthread
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER
from carbonui import const as uiconst
from carbonui.fontconst import STYLE_HEADER
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.shared.preview import PreviewContainer
from eve.client.script.ui.shared.vgs.priceTag import PriceTagMedium
from eve.client.script.ui.util.uiComponents import Component, ButtonEffect, RadioButtonEffect, ToggleButtonEffect
from eve.client.script.ui.view.aurumstore.shared.offerpricing import iter_currencies
from eve.client.script.ui.view.aurumstore import vgsUiConst
from eve.client.script.ui.view.aurumstore.shared.const import STORE_PREVIEW_OVERLAY_HEIGHT
from eve.client.script.ui.view.aurumstore.vgsUiPrimitives import LazyUrlSprite, VgsLabelRibbon, VgsLabelRibbonLarge
from eve.common.lib import appConst
from eve.common.script.sys.eveCfg import IsApparel, IsBlueprint, IsPreviewable
logger = logging.getLogger(__name__)

class Ribbon(Container):
    ID_SALE = 'Sale'
    ID_NEW = 'New'
    ID_HOT = 'Hot'
    ID_BUNDLE = 'Bundle'
    ID_FREE = 'Free'
    SORTING = [ID_FREE,
     ID_SALE,
     ID_NEW,
     ID_HOT,
     ID_BUNDLE]
    default_name = 'Ribbon'
    default_state = uiconst.UI_DISABLED
    default_align = uiconst.TOPLEFT

    def __init__(self, text, texture_path, is_big = False, *args, **kwargs):
        super(Ribbon, self).__init__(*args, **kwargs)
        self.text = text
        self.texture_path = texture_path
        self.is_big = is_big
        self.construct_layout()

    def construct_layout(self):
        if self.is_big:
            self.left = vgsUiConst.OFFER_INFO_PADDING_BIG
            label = VgsLabelRibbonLarge(parent=self, align=uiconst.CENTER, text=self.text, padding=(-20, 10, 0, 0), color=Color.WHITE)
        else:
            label = VgsLabelRibbon(parent=self, align=uiconst.CENTER, text=self.text, padding=(-10, 19, 0, 0), color=Color.WHITE)
        self.bgSprite = Frame(parent=self, texturePath=self.texture_path, align=uiconst.TOPLEFT, height=50, cornerSize=20, uiScaleVertices=True)
        self.width = label.textwidth + 70
        self.height = label.textheight + 2
        self.bgSprite.width = self.width


def CreateFill(parent, _):
    return Fill(name='highlight', bgParent=parent.imageLayer, color=vgsUiConst.OFFER_BACKGROUND_COLOR, idx=0)


@Component(ButtonEffect(bgElementFunc=CreateFill, idx=0, opacityIdle=0.0, opacityHover=0.5, opacityMouseDown=0.85, audioOnEntry='store_hover'))

class VgsOffer(Container):
    default_name = 'Offer'
    default_align = uiconst.TOPLEFT
    default_clipChildren = False
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.offer = attributes.offer
        self.name = 'offer_{}'.format(self.offer.id)
        if self.offer:
            self.CreateInfoBox(attributes.upperText, attributes.upperSize or vgsUiConst.VGS_FONTSIZE_OFFER)
        self.imageLayer = Transform(name='imageLayer', parent=self, align=uiconst.TOALL, scalingCenter=(0.5, 0.5), bgColor=vgsUiConst.OFFER_BACKGROUND_COLOR)
        if self.offer and self.offer.label:
            Ribbon(parent=self, align=uiconst.TOPLEFT, text=self.offer.label.description, texture_path=self.offer.label.url, state=uiconst.UI_DISABLED, idx=0, padding=(-10, -10, 0, 0))
        if self.offer:
            self.lazySprite = LazyUrlSprite(parent=self.imageLayer, align=uiconst.TOALL, imageUrl=self.offer.imageUrl)
        GradientSprite(name='OfferGradient', align=uiconst.TOALL, bgParent=self.imageLayer, rgbData=((1.0, vgsUiConst.OFFER_RADIAL_SHADOW),), alphaData=((0.0, 0.0), (1.0, 1.0)), radial=True, idx=0)

    def OnClick(self):
        if self.offer:
            sm.GetService('vgsService').ShowOffer(self.offer.id)

    def CreateInfoBox(self, upperText, upperSize):
        textLayer = Container(name='TextLayer', parent=self, align=uiconst.TOALL)
        infoBox = ContainerAutoSize(name='InfoBox', parent=textLayer, align=uiconst.TOBOTTOM, height=vgsUiConst.OFFER_INFO_BOX_HEIGHT, state=uiconst.UI_DISABLED, bgColor=vgsUiConst.OFFER_TEXT_BOX_COLOR)
        Label(parent=infoBox, align=uiconst.TOTOP, text=upperText, fontsize=upperSize, padding=(vgsUiConst.OFFER_INFO_PADDING,
         2,
         vgsUiConst.OFFER_INFO_PADDING,
         -2), fontStyle=STYLE_HEADER, uppercase=True, lineSpacing=-0.15, color=Color.WHITE)
        priceCont = Container(parent=infoBox, align=uiconst.TOTOP, height=len(self.offer.offerPricings) * 24, padding=(8, 2, 8, 2))
        for currency, price, basePrice in iter_currencies(self.offer):
            PriceTagMedium(parent=priceCont, align=uiconst.TOTOP, currency=currency, price=price, basePrice=basePrice)

    def OnMouseEnter(self, *args):
        uicore.animations.Tr2DScaleTo(self.imageLayer, startScale=self.imageLayer.scale, endScale=(1.02, 1.02), duration=0.2)

    def OnMouseExit(self, *args):
        uicore.animations.Tr2DScaleTo(self.imageLayer, self.imageLayer.scale, endScale=(1.0, 1.0), duration=0.2)

    def GetMenu(self, *args):
        if session.role & ROLE_PROGRAMMER:
            return [('offerid: %s' % self.offer.id, lambda : blue.pyos.SetClipboardData(str(self.offer.id)))]


class VgsOfferPreview(Container):
    default_name = 'OfferPreview'
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_PICKCHILDREN
    default_clipChildren = True
    charID = industry.Property('_charID', 'on_charid')
    typeID = industry.Property('_typeID', 'on_typeid')

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.offer = attributes.offer
        self._charID = None
        self._typeID = None
        self.on_charid = signals.Signal(signalName='on_charid')
        self.on_typeid = signals.Signal(signalName='on_typeid')
        self.on_charid.connect(self.OnPickCharacter)
        self.on_typeid.connect(self.OnPickType)
        self.charButtons = []
        self._charButtonsDisplayed = False
        self.isPreviewOffer = False
        for product in self.offer.productQuantities.itervalues():
            if IsPreviewable(GetPreviewType(product.typeId)):
                self.typeID = product.typeId
                self.isPreviewOffer = True

        if not self.isPreviewOffer:
            self._openServiceOfferCard()
        elif not IsApparel(self.typeID):
            self._openSkinOfferCard()
        else:
            self._openApperalOfferCard()

    def _createOfferCard(self):
        textLayer = Container(name='TextLayer', parent=self)
        descriptionBox = ContainerAutoSize(parent=textLayer, align=uiconst.TOBOTTOM, bgColor=vgsUiConst.OFFER_TEXT_BOX_COLOR, clipChildren=True, name='DescriptionBox')
        descriptionText = Label(parent=descriptionBox, align=uiconst.TOTOP, text=self.offer.description, fontsize=vgsUiConst.VGS_FONTSIZE_SMALL, padding=vgsUiConst.STORE_OFFER_CARD_DESCRIPTION_PADDING, name='DescriptionText')
        titleBox = ContainerAutoSize(name='InfoBox', parent=textLayer, align=uiconst.TOBOTTOM, bgColor=vgsUiConst.OFFER_TEXT_BOX_COLOR)
        titleText = Label(parent=titleBox, align=uiconst.TOTOP, text=self.offer.name, fontsize=vgsUiConst.VGS_FONTSIZE_LARGE, padding=vgsUiConst.STORE_OFFER_CARD_TITLE_PADDING, fontStyle=STYLE_HEADER, uppercase=True, lineSpacing=-0.15, name='TitleText')
        textLayerScreenHeight = textLayer.GetAbsoluteSize()[1]
        descriptionScreenHeight = descriptionText.GetAbsoluteSize()[1]
        titleBoxScreenHeight = titleBox.GetAbsoluteSize()[1]
        titleTextScreenHeight = titleText.GetAbsoluteSize()[1]
        descriptionMaxHeight = textLayerScreenHeight - (titleBoxScreenHeight + titleTextScreenHeight) - STORE_PREVIEW_OVERLAY_HEIGHT
        if descriptionScreenHeight > 50:
            descriptionBox.maxHeight = 50
            self._makeCollapsable(parent=textLayer, target=descriptionBox, contentMaxHeight=descriptionMaxHeight, contentMinHeight=50)

    def _addLoading(self):
        self.loadingLayer = Container(parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        self.loadingWheel = LoadingWheel(parent=self.loadingLayer, align=uiconst.CENTER, state=uiconst.UI_DISABLED, opacity=0.0)
        self.cover = Sprite(parent=self.loadingLayer, align=uiconst.TOALL, texturePath='res:/UI/Texture/preview/asset_preview_background.png')

    def _addPreviewImageLayer(self):
        self.imageLayer = Transform(name='imageLayer', parent=self, align=uiconst.TOALL, scalingCenter=(0.5, 0.5), bgColor=vgsUiConst.OFFER_BACKGROUND_COLOR)
        self.previewContainer = PreviewContainer(parent=self.imageLayer, OnStartLoading=self.OnStartLoading, OnStopLoading=self.OnStopLoading)
        self.lazySprite = LazyUrlSprite(parent=self.imageLayer, align=uiconst.TOALL, imageUrl=self.offer.imageUrl, state=uiconst.UI_DISABLED)
        GradientSprite(name='OfferGradient', align=uiconst.TOALL, bgParent=self.imageLayer, rgbData=((1.0, vgsUiConst.OFFER_RADIAL_SHADOW),), alphaData=((0.0, 0.0), (1.0, 1.0)), radial=True, idx=0)

    def _addCharacterPicker(self):
        self.characterPickerLayer = ContainerAutoSize(parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_PICKCHILDREN, top=50 if self.offer.label else 10, left=10)
        self.CreateCharacterButtons()

    def _openServiceOfferCard(self):
        self._createOfferCard()
        self._addLoading()
        self.imageLayer = Transform(name='imageLayer', parent=self, align=uiconst.TOALL, scalingCenter=(0.5, 0.5), bgColor=vgsUiConst.OFFER_BACKGROUND_COLOR)
        self.lazySprite = LazyUrlSprite(parent=self.imageLayer, align=uiconst.TOALL, imageUrl=self.offer.imageUrl, state=uiconst.UI_DISABLED)
        GradientSprite(name='OfferGradient', align=uiconst.TOALL, bgParent=self.imageLayer, rgbData=((1.0, vgsUiConst.OFFER_RADIAL_SHADOW),), alphaData=((0.0, 0.0), (1.0, 1.0)), radial=True, idx=0)
        uicore.animations.SpMaskOut(self.cover, duration=0.4)

    def _openSkinOfferCard(self):
        self._createOfferCard()
        self._addLoading()
        self._addPreviewImageLayer()

    def _openApperalOfferCard(self):
        self._createOfferCard()
        self._addCharacterPicker()
        self._addLoading()
        self._addPreviewImageLayer()

    def _makeCollapsable(self, parent, target, contentMaxHeight, contentMinHeight):
        collapseBox = ContainerAutoSize(parent=parent, align=uiconst.TOBOTTOM_NOPUSH, top=-36, name='CollapseBox')
        CollapseButton(parent=collapseBox, align=uiconst.TOPRIGHT, target=target, contentMaxHeight=contentMaxHeight, contentCollapsedHeight=contentMinHeight, name='CollapseButton')

    def CreateCharacterButtons(self):
        characters = sm.GetService('cc').GetCharactersToSelect()
        charIDList = itertools.chain([None], map(lambda c: c.characterID, characters))
        for i, charID in enumerate(charIDList):
            button = CharacterButton(parent=self.characterPickerLayer, align=uiconst.RELATIVE, pos=(0,
             i * 43,
             38,
             38), charID=charID, onClick=lambda charID: setattr(self, 'charID', charID), isActive=charID == self.charID, opacity=0.0, state=uiconst.UI_DISABLED)
            self.on_charid.connect(button.OnCharID)
            self.on_typeid.connect(button.OnTypeID)
            self.charButtons.append(button)

    def ShowCharacterButtons(self):
        if self._charButtonsDisplayed:
            return
        for i, button in enumerate(self.charButtons):
            uicore.animations.MoveInFromLeft(button, amount=10, duration=0.2, timeOffset=i * 0.1)
            uicore.animations.FadeIn(button, duration=0.4, timeOffset=i * 0.1)
            button.state = uiconst.UI_NORMAL

        self._charButtonsDisplayed = True

    def HideCharacterButtons(self):
        if not self._charButtonsDisplayed:
            return
        for button in self.charButtons:
            uicore.animations.FadeOut(button, duration=0.2)
            button.state = uiconst.UI_DISABLED

        self._charButtonsDisplayed = False

    def OnPickCharacter(self, _):
        uthread.new(self.ShowPreview)

    def OnPickType(self, _):
        if IsPreviewable(self.typeID) and IsApparel(self.typeID) and not IsWearableBy(self.typeID, self.charID):
            self.charID = None
            return
        uthread.new(self.ShowPreview)

    def OnStartLoading(self, _):
        if not IsApparel(self.typeID):
            self.HideCharacterButtons()
        else:
            self.lazySprite.SetOpacity(0)
        if self.isPreviewOffer:
            uicore.animations.FadeIn(self.loadingWheel, duration=0.3, timeOffset=0.2)
            uicore.animations.SpMaskIn(self.cover, duration=0.5, sleep=True)
            self.previewContainer.Show()

    def OnStopLoading(self, preview, success):
        if IsApparel(self.typeID):
            self.ShowCharacterButtons()
        else:
            self.lazySprite.SetOpacity(1)
        if self.isPreviewOffer:
            uicore.animations.FadeOut(self.loadingWheel, duration=0.3)
            uicore.animations.SpMaskOut(self.cover, duration=0.5)

    def ShowPreview(self):
        typeID = GetPreviewType(self.typeID)
        if not IsPreviewable(typeID):
            return
        if IsApparel(self.typeID) and self.charID:
            self.previewContainer.PreviewCharacter(self.charID, apparel=[self.typeID])
        else:
            self.previewContainer.PreviewType(typeID, scenePath='res:/dx9/scene/fitting/fitting.red')
        if IsApparel(typeID):
            self.previewContainer.AnimEntry(-0.1 + math.pi, 0.0, 0.5 + math.pi, -0.2)
        else:
            self.previewContainer.AnimEntry(0.3 + math.pi, 0.2, 0.6 + math.pi, -0.3)

    def PrepareClose(self):
        uicore.animations.SpMaskIn(self.cover, duration=0.2, sleep=True)
        if self.isPreviewOffer:
            self.previewContainer.SetState(uiconst.UI_HIDDEN)


@Component(ToggleButtonEffect(bgElementFunc=lambda parent, _: parent.arrow, opacityIdle=0.5, opacityHover=0.8, opacityMouseDown=1.0, audioOnEntry='store_hover'))

class CollapseButton(Container):
    default_state = uiconst.UI_NORMAL
    default_width = 32
    default_height = 32

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.target = attributes.target
        self.contentMaxHeight = attributes.contentMaxHeight
        self.contentCollapsedHeight = attributes.contentCollapsedHeight
        self.arrow = Sprite(parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Icons/105_32_21.png', rotation=math.pi)

    def Expand(self):
        self.target.maxHeight = self.contentMaxHeight
        self.Animate(0, self.target.height, 0)

    def Collapse(self):
        self.target.maxHeight = self.contentCollapsedHeight
        self.Animate(self.target.height, 0, math.pi)

    def Animate(self, startHeight, endHeight, rotation):
        uicore.animations.MorphScalar(self.target, 'height', startVal=startHeight, endVal=endHeight, duration=0.4, curveType=uiconst.ANIM_OVERSHOT)
        uicore.animations.MorphScalar(self.arrow, 'rotation', startVal=self.arrow.rotation, endVal=rotation, duration=0.2)

    def OnClick(self, *args):
        if self.isActive:
            self.Collapse()
        else:
            self.Expand()


@Component(RadioButtonEffect(bgElementFunc=lambda parent, _: parent.highlight, idx=0, opacityIdle=0.0, opacityHover=0.5, opacityMouseDown=0.85, audioOnEntry='store_hover'))

class CharacterButton(Container):
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.charID = attributes.get('charID', None)
        self.onClick = attributes.onClick
        self.gender = None
        if self.charID:
            self.gender = cfg.eveowners.Get(self.charID).gender
        self.highlight = Fill(bgParent=self, color=(0.8, 0.8, 0.8, 1.0), padding=[-3,
         -3,
         -2,
         -2], fillCenter=True)
        self.portrait = Sprite(parent=self, name='portraitSprite', align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        if self.charID:
            sm.GetService('photo').GetPortrait(self.charID, 38, self.portrait)
        else:
            self.portrait.texturePath = 'res:/UI/Texture/Vgs/mannequin.png'

    def OnClick(self, *args):
        if not self.disabled:
            self.onClick(self.charID)

    def OnCharID(self, container):
        self.SetActive(container.charID == self.charID)

    def OnTypeID(self, container):
        if self.gender is None or not IsApparel(container.typeID):
            return
        gender = GetApparelGender(container.typeID)
        if gender is None or gender == self.gender:
            self.disabled = False
            uicore.animations.SpColorMorphTo(self.portrait, endColor=(1.0, 1.0, 1.0), duration=0.4)
        else:
            self.disabled = True
            uicore.animations.SpColorMorphTo(self.portrait, endColor=(0.4, 0.4, 0.4), duration=0.4)


GENDER_BY_APPAREL_GENDER = {1: appConst.MALE,
 2: None,
 3: appConst.FEMALE,
 4: 'Missing Gender'}

def GetApparelGender(typeID):
    apparelGender = None
    for resource in cfg.paperdollResources:
        if resource.typeID == typeID:
            if resource.resGender is None:
                apparelGender = None
            elif resource.resGender:
                apparelGender = appConst.MALE
            elif not resource.resGender:
                apparelGender = appConst.FEMALE

    return apparelGender


def IsWearableBy(typeID, charID):
    if not IsApparel(typeID):
        return False
    if charID is None:
        return True
    apparelGender = GetApparelGender(typeID)
    characterGender = cfg.eveowners.Get(charID).gender
    return apparelGender is None or apparelGender == characterGender


def GetPreviewType(typeID):
    if IsBlueprint(typeID):
        blueprint = sm.GetService('blueprintSvc').GetBlueprintType(typeID)
        return blueprint.productTypeID
    return typeID
