#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\redeem\oldRedeemPanel.py
import logging
import math
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.util.bunch import Bunch
from eve.client.script.ui.control import eveIcon, eveLabel
from eveexceptions.exceptionEater import ExceptionEater
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipHeaderDescriptionWrapper
import uthread
from carbonui.primitives.transform import Transform
import eve.client.script.ui.shared.redeem.redeemUiConst as redeemColors
from eve.client.script.ui.view.aurumstore.vgsUiPrimitives import LazyUrlSprite
from carbonui.primitives.container import Container
import carbonui.const as uiconst
import localization
import blue
from eve.client.script.ui.util.uiComponents import Component, ButtonEffect
import trinity
from localization.formatters import FormatTimeIntervalShortWritten, TIME_CATEGORY_DAY, TIME_CATEGORY_MINUTE
import evetypes
from carbonui.uicore import uicore
REDEEM_BUTTON_HEIGHT = 30
DRAG_TEXT_CONTAINER_HEIGHT = 28
LABEL_CONTAINER_HEIGHT = 45
DEFAULT_TOKEN_SIZE = 64
REDEEM_TOKEN_TOP_PADDING = 4
REDEEM_ITEM_POP_IN_TIME = 0.2
REDEEM_ITEM_HOVER_EFFECT_TIME = 0.1
log = logging.getLogger(__name__)

class RedeemPanel(ContainerAutoSize):
    default_align = uiconst.TOBOTTOM_NOPUSH
    default_state = uiconst.UI_NORMAL
    default_tokenSize = DEFAULT_TOKEN_SIZE
    default_dragEnabled = True
    default_instructionText = None
    default_name = 'RedeemPanel'
    isDropLocation = False

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        account = sm.GetService('vgsService').GetStore().GetAccount()
        account.SubscribeToRedeemingTokensUpdatedEvent(self.OnRedeemingTokensUpdated)
        self.expandCallback = attributes.get('expandCallback', None)
        self.collapseCallback = attributes.get('collapseCallback', None)
        self.dragEnabled = attributes.get('dragEnabled', self.default_dragEnabled)
        self.instructionText = attributes.get('instructionText', self.default_instructionText)
        self.buttonOnClick = attributes.get('buttonClick', self.ChangeCollapsedState)
        self.listenToRedeemQueueUpdatedEvents = True
        self.allTokens = {}
        self._isCollapsed = True
        self.redeemButton = RedeemButton(parent=self, name='redeemButton', align=uiconst.TOTOP, height=REDEEM_BUTTON_HEIGHT, state=uiconst.UI_NORMAL, OnClick=self.buttonOnClick, borderColor=attributes.get('redeemButtonBorderColor', redeemColors.REDEEM_BUTTON_BORDER_COLOR), backgroundColor=attributes.get('redeemButtonBackgroundColor', redeemColors.REDEEM_BUTTON_BACKGROUND_COLOR), fillColor=attributes.get('redeemButtonFillColor', redeemColors.REDEEM_BUTTON_FILL_COLOR), textColor=attributes.get('textColor', redeemColors.TEXT_COLOR))
        self.redeemContainer = RedeemContainer(parent=self, name='panelContent', align=uiconst.TOTOP, tokenSize=attributes.get('tokenSize', self.default_tokenSize), dragEnabled=self.dragEnabled, instructionText=self.instructionText)
        Fill(bgParent=self, color=attributes.get('redeemPanelBackgroundColor', redeemColors.REDEEM_PANEL_BACKGROUND_COLOR))
        self.height = self.redeemButton.height
        self.top = -self.height
        self.display = False
        self.CollapsePanel(False)

    def Close(self):
        with ExceptionEater('Could not unsubscribe from RedeemingQueueUpdated event'):
            account = sm.GetService('vgsService').GetStore().GetAccount()
            account.UnsubscribeFromRedeemingTokensUpdatedEvent(self.OnRedeemingTokensUpdated)
        ContainerAutoSize.Close(self)

    def SetListenToRedeemQueueUpdatedEvents(self, listenToRedeemQueueUpdatedEvents):
        self.listenToRedeemQueueUpdatedEvents = listenToRedeemQueueUpdatedEvents

    def GetHeight(self):
        if not self.display:
            return 0
        elif self.isCollapsed:
            return self.GetButtonHeight()
        else:
            return self.GetButtonHeight() + self.GetPanelHeight()

    def GetPanelHeight(self):
        return self.redeemContainer.expandedHeight

    def GetButtonHeight(self):
        return self.redeemButton.height

    def ChangeCollapsedState(self):
        if self.isCollapsed:
            if self.expandCallback:
                self.expandCallback()
            else:
                self.ExpandPanel()
        elif self.collapseCallback:
            self.collapseCallback()
        else:
            self.CollapsePanel()

    def ExpandPanel(self, animate = True, showNewItems = True, duration = REDEEM_ITEM_POP_IN_TIME, timeOffset = 0.0):
        self.UpdateDisplay(timeOffset=0.0)
        self.redeemButton.Expand(animate, duration=duration, timeOffset=timeOffset)
        self.redeemContainer.Expand(animate, showNewItems=showNewItems, duration=duration, timeOffset=timeOffset)
        self._isCollapsed = False

    def CollapsePanel(self, animate = True, duration = REDEEM_ITEM_POP_IN_TIME, timeOffset = 0.0, callback = None):
        self.redeemButton.Collapse(animate, duration=duration, timeOffset=timeOffset)
        self.redeemContainer.Collapse(animate, duration=duration, timeOffset=timeOffset, callback=callback)
        self._isCollapsed = True

    def IsCollapsed(self):
        return self.isCollapsed

    def OnRedeemingTokensUpdated(self):
        if self.listenToRedeemQueueUpdatedEvents:
            self.redeemContainer.OnRedeemingTokensUpdated()
            if self.redeemContainer.HasRedeemItems():
                self.ShowPanel()
            else:
                self.HidePanel()

    def RedeemItems(self, redeemedItems):
        self.redeemContainer.TokensRedeemed(redeemedItems)

    def ShowPanel(self, animate = True, duration = 0.3, timeOffset = 0.0):
        if self.IsHidden() and animate:
            self.CollapsePanel(animate=False)
            self.Show()
            uicore.animations.MorphScalar(self, 'top', startVal=self.top, endVal=0, duration=duration, timeOffset=timeOffset)
        if not animate:
            self.top = 0
            self.Show()

    def HidePanel(self, animate = True, duration = 0.3, timeOffset = 0.0):
        if not self.IsHidden() and animate:
            if not self.isCollapsed:
                self.redeemContainer.Collapse(animate)
                timeOffset = max(timeOffset, REDEEM_ITEM_POP_IN_TIME)
            uicore.animations.MorphScalar(self, 'top', startVal=self.top, endVal=-self.height, duration=duration, timeOffset=timeOffset, callback=self.Hide)
        if not animate:
            self.top = -self.height
            self.Hide()

    def UpdateDisplay(self, animate = True, duration = 0.3, timeOffset = 0.0):
        self.redeemContainer.UpdateTokens()
        if self.redeemContainer.HasRedeemItems() and self.IsHidden():
            self.ShowPanel(animate=animate, duration=duration, timeOffset=timeOffset)
        elif not self.redeemContainer.HasRedeemItems() and not self.IsHidden():
            self.HidePanel(animate=animate, duration=duration, timeOffset=timeOffset)

    def HasRedeemItems(self):
        return self.redeemContainer.HasRedeemItems()

    def AddRedeemContainerContent(self, redeemContainer):
        newTokens = {key:token for key, token in self.redeemContainer.allTokens.iteritems() if token.IsNew()}
        oldTokens = {key:token for key, token in self.redeemContainer.allTokens.iteritems() if not token.IsNew()}
        self.redeemContainer.ScrollToEnd()
        partialOpacity = 0.35
        fullOpacity = 1.0
        for tokenKey, token in oldTokens.iteritems():
            uicore.animations.FadeTo(token, startVal=fullOpacity, endVal=partialOpacity, duration=0.5)

        for tokenKey, destinationToken in newTokens.iteritems():
            sourceToken = redeemContainer.PopToken(destinationToken.redeemTokenData)
            if sourceToken:
                sourceToken.AnimateOut(callback=destinationToken.Blink, timeOffset=0.6)

        for tokenKey, token in oldTokens.iteritems():
            uicore.animations.FadeTo(token, startVal=partialOpacity, endVal=fullOpacity, duration=0.5, timeOffset=1.0 + 4 * REDEEM_ITEM_POP_IN_TIME)


class RedeemButton(Transform):
    default_name = 'RedeemButton'

    def ApplyAttributes(self, attributes):
        Transform.ApplyAttributes(self, attributes)
        borderColor = attributes.get('borderColor', redeemColors.REDEEM_BUTTON_BORDER_COLOR)
        backgroundColor = attributes.get('backgroundColor', redeemColors.REDEEM_BUTTON_BACKGROUND_COLOR)
        fillColor = attributes.get('fillColor', redeemColors.REDEEM_BUTTON_FILL_COLOR)
        textColor = attributes.get('textColor', redeemColors.TEXT_COLOR)
        Line(parent=self, color=borderColor, align=uiconst.TOTOP, weight=1)
        Fill(bgParent=self, color=backgroundColor)
        borderFillColor = fillColor[:3]
        self.borderFill = GradientSprite(bgParent=self, rgbData=[(0, borderFillColor), (0.5, borderFillColor), (1.0, borderFillColor)], alphaData=[(0.3, 0.1), (0.5, 0.4), (0.7, 0.1)], idx=0, state=uiconst.UI_DISABLED)
        self.onClick = attributes.get('OnClick', None)
        self.captionCont = Container(parent=self, name='captionCont', align=uiconst.CENTERTOP)
        self.expanderIcon = Sprite(parent=self.captionCont, texturePath='res:/UI/Texture/Icons/105_32_5.png', align=uiconst.CENTERRIGHT, pos=(0, 0, 32, 32), state=uiconst.UI_DISABLED, color=textColor)
        self.availableLabel = eveLabel.EveCaptionMedium(parent=self.captionCont, align=uiconst.CENTERLEFT, text=localization.GetByLabel('UI/RedeemWindow/RedeemableItems'), state=uiconst.UI_DISABLED, color=textColor, bold=False)
        self.availableLabel.letterspace = 1
        self.captionCont.width = self.availableLabel.textwidth + 10 + self.expanderIcon.width
        self.captionCont.height = max(self.availableLabel.textheight + 10, self.expanderIcon.height)
        self.height = self.captionCont.height
        push = sm.GetService('window').GetCameraLeftOffset(self.captionCont.width, align=uiconst.CENTERTOP, left=0)
        self.captionCont.left = push

    def Expand(self, animate = True, duration = REDEEM_ITEM_POP_IN_TIME, timeOffset = 0.0):
        self.Animate(0, animate, duration, timeOffset)

    def Collapse(self, animate = True, duration = REDEEM_ITEM_POP_IN_TIME, timeOffset = 0.0):
        self.Animate(math.pi, animate, duration, timeOffset)

    def Animate(self, endVal, animate, duration, timeOffset = 0.0):
        if animate:
            uicore.animations.MorphScalar(self.expanderIcon, 'rotation', startVal=self.expanderIcon.rotation, endVal=endVal, duration=duration, timeOffset=timeOffset)
        else:
            self.expanderIcon.rotation = endVal

    def DefaultOnClick(self):
        pass

    def OnClick(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        if self.onClick:
            self.onClick()

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)


class RedeemContainer(Container):
    default_name = 'RedeemContainer'
    default_dragEnabled = True
    default_instructionText = None
    default_tokenSize = DEFAULT_TOKEN_SIZE
    default_minimizeTokens = False

    def ApplyAttributes(self, attributes):
        self.tokens = {}
        self.allTokens = {}
        Container.ApplyAttributes(self, attributes)
        self.clipChildren = True
        self.redeemSvc = sm.GetService('redeem')
        self.tokenSize = attributes.get('tokenSize', self.default_tokenSize)
        self.dragEnabled = attributes.get('dragEnabled', self.default_dragEnabled)
        self.instructionText = attributes.get('instructionText', self.default_instructionText)
        self.containerWidth = attributes.get('containerWidth', 0)
        self.textColor = attributes.get('textColor', redeemColors.TEXT_COLOR)
        self.minimizeTokens = attributes.get('minimizeTokens', self.default_minimizeTokens)
        self.expandedHeight = self.GetTokenHeight() + self.GetInstructionHeight()
        c = Container(parent=self, name='tokenContainerParent', height=self.expandedHeight, align=uiconst.TOTOP)
        self.tokenContainer = ScrollContainer(parent=c, name='tokenScrollContainer', height=self.GetTokenHeight(), align=uiconst.CENTERTOP)
        if self.instructionText:
            self.bottomContent = Container(parent=c, name='bottomBorder', align=uiconst.TOBOTTOM, height=DRAG_TEXT_CONTAINER_HEIGHT)
            self.instructionLabel = eveLabel.EveLabelMedium(parent=self.bottomContent, name='instructionLabel', align=uiconst.CENTER, padLeft=4, padTop=3, text=self.instructionText, color=self.textColor, opacity=0.8, state=uiconst.UI_NORMAL)
            push = sm.GetService('window').GetCameraLeftOffset(self.instructionLabel.width, align=uiconst.CENTER, left=0)
            self.instructionLabel.left = push

    def ScrollToEnd(self):
        self.tokenContainer.ScrollToHorizontal(1.0)

    def _OnResize(self, *args):
        self.SetTokenContainerWidth()

    def GetTokenHeight(self):
        tokenHeight = self.tokenSize + REDEEM_TOKEN_TOP_PADDING
        if not self.minimizeTokens:
            tokenHeight += LABEL_CONTAINER_HEIGHT
        return tokenHeight

    def GetInstructionHeight(self):
        if self.instructionText:
            return DRAG_TEXT_CONTAINER_HEIGHT
        return 0

    def UpdateTokens(self):
        self.tokens = self.GetTokens()
        self.LoadTokens()

    def CreateRedeemToken(self, token):
        desc = self.redeemSvc.GetTokenDescription(token) or self.redeemSvc.GetTokenLabel(token)
        redeemTokenData = RedeemTokenObject(typeID=token.typeID, quantity=token.quantity, expireDateTime=token.expireDateTime, stationID=token.stationID, tokenID=token.tokenID, massTokenID=token.massTokenID, blueprintRuns=token.blueprintRuns)
        t = RedeemableToken(parent=self.tokenContainer, redeemTokenData=redeemTokenData, desc=desc, dragEnabled=self.dragEnabled, tokenSize=self.tokenSize, closeCallback=self.SetTokenContainerWidth, minimized=self.minimizeTokens)
        return t

    def GetSortedRedeemTokens(self):
        expiringTokens = [ (tokenKey, token) for tokenKey, token in self.tokens.iteritems() if token.expireDateTime ]
        expiringTokens = sorted(expiringTokens, key=lambda x: x[1].expireDateTime)
        nonExpiringTokens = [ (tokenKey, token) for tokenKey, token in self.tokens.iteritems() if not token.expireDateTime ]
        nonExpiringTokens = sorted(nonExpiringTokens, key=lambda x: x[1].tokenID)
        sortedTokens = expiringTokens + nonExpiringTokens
        return sortedTokens

    def LoadTokens(self):
        updatedTokens = self.GetSortedRedeemTokens()
        tokensToRemove = [ tokenKey for tokenKey in self.allTokens.keys() if tokenKey not in self.tokens ]
        for tokenKey in tokensToRemove:
            token = self.allTokens.pop(tokenKey, None)
            if token:
                token.Close()

        for tokenKey, token in updatedTokens:
            if tokenKey not in self.allTokens:
                self.allTokens[tokenKey] = self.CreateRedeemToken(token)

        self.SetTokenContainerWidth()

    def TokensRedeemed(self, redeemedItems):
        for tokenKey in redeemedItems:
            t = self.allTokens.pop(tokenKey, None)
            if t:
                t.AnimateOut(callback=t.Close)
            self.tokens.pop(tokenKey)

    def PopToken(self, token):
        return self.allTokens.pop(self.ExtractTokenKey(token), None)

    def ExtractTokenKey(self, token):
        return (token.tokenID, token.massTokenID)

    def GetTokens(self):
        return {self.ExtractTokenKey(token):token for token in self.redeemSvc.GetRedeemTokens()}

    def HasRedeemItems(self):
        return len(self.tokens) > 0

    def OnRedeemingTokensUpdated(self):
        oldTokenKeys = self.tokens.keys()
        self.UpdateTokens()
        for tokenKey in self.tokens.keys():
            if tokenKey not in oldTokenKeys:
                self.allTokens[tokenKey].SetIsNew(True)

    def SetTokenContainerWidth(self):
        width = sum((t.width + t.padLeft + t.padRight for t in self.allTokens.itervalues()))
        parentWidth = self.parent.GetAbsoluteRight() - self.parent.GetAbsoluteLeft()
        minWidth = parentWidth if self.containerWidth == 0 else self.containerWidth
        self.tokenContainer.width = min(minWidth, width)
        if self.tokenContainer.width != minWidth:
            push = sm.GetService('window').GetCameraLeftOffset(self.tokenContainer.width, align=uiconst.CENTER, left=0)
            self.tokenContainer.left = push

    def Expand(self, animate, showNewItems = True, duration = REDEEM_ITEM_POP_IN_TIME, timeOffset = 0.0):
        heightValue = self.expandedHeight
        if animate:
            uicore.animations.MorphScalar(self, 'height', startVal=self.height, endVal=heightValue, duration=duration, timeOffset=timeOffset)
            for token in self.allTokens.itervalues():
                if showNewItems or not token.IsNew():
                    token.AnimateIn(animate=False)

            if self.instructionText:
                uicore.animations.FadeIn(self.instructionLabel, duration=duration, timeOffset=timeOffset + duration)
        else:
            self.height = heightValue
            if self.instructionText:
                self.instructionLabel.opacity = 1.0

    def Collapse(self, animate, duration = REDEEM_ITEM_POP_IN_TIME, timeOffset = 0.0, callback = None):
        heightValue = 0
        if animate:
            uicore.animations.MorphScalar(self, 'height', startVal=self.height, endVal=heightValue, duration=duration, callback=callback)
            for token in self.allTokens.itervalues():
                token.AnimateOut(animate=True, timeOffset=timeOffset + duration)

        else:
            self.height = heightValue
        if self.instructionText:
            self.instructionLabel.opacity = 0


class StaticRedeemContainer(RedeemContainer):

    def ApplyAttributes(self, attributes):
        RedeemContainer.ApplyAttributes(self, attributes)
        offerQuantity = attributes.offerQuantity
        tokenObjects = [ RedeemTokenObject(typeID=token.typeId, quantity=token.quantity * offerQuantity, imageUrl=token.imageUrl, name=token.name) for token in attributes.redeemTokens ]
        self.staticRedeemTokens = {self.ExtractTokenKey(token):token for token in tokenObjects}
        self.UpdateTokens()
        self.Expand(animate=False)

    def CreateRedeemToken(self, token):
        t = RedeemableToken(parent=self.tokenContainer, redeemTokenData=token, desc='', dragEnabled=self.dragEnabled, tokenSize=self.tokenSize, minimized=True)
        t.AnimateIn(animate=False)
        return t

    def ExtractTokenKey(self, token):
        return (token.typeID, token.quantity)

    def GetTokens(self):
        return self.staticRedeemTokens


class RedeemTokenObject(object):

    def __init__(self, typeID = -1, quantity = 0, expireDateTime = 0, stationID = 0, tokenID = 0, massTokenID = 0, blueprintRuns = 0, imageUrl = None, name = None):
        self.typeID = typeID
        self.quantity = quantity
        self.expireDateTime = expireDateTime
        self.stationID = stationID
        self.tokenID = tokenID
        self.massTokenID = massTokenID
        self.blueprintRuns = blueprintRuns
        self.typeName = name
        self.portionSize = 1
        self.imageUrl = imageUrl
        if typeID > 0 and evetypes.Exists(typeID):
            self.typeName = evetypes.GetName(typeID)
            self.portionSize = evetypes.GetPortionSize(typeID)

    def __repr__(self):
        return 'RedeemToken %s' % [self.typeID,
         self.quantity,
         self.expireDateTime,
         self.stationID,
         self.tokenID,
         self.massTokenID,
         self.typeName,
         self.portionSize,
         self.imageUrl]


def GetRedeemableTokenBorder(parent, _):
    return parent.highlightOverlay


@Component(ButtonEffect(opacityIdle=0.0, opacityHover=1.0, bgElementFunc=GetRedeemableTokenBorder, audioOnEntry=uiconst.SOUND_ENTRY_HOVER))

class RedeemableToken(Transform):
    default_tokenSize = DEFAULT_TOKEN_SIZE
    default_align = uiconst.TOLEFT
    default_state = uiconst.UI_NORMAL
    default_itemPadding = 6
    default_scalingCenter = (0.5, 0.5)
    default_name = 'RedeemableToken'
    isDragObject = True
    isDropLocation = False

    def ApplyAttributes(self, attributes):
        Transform.ApplyAttributes(self, attributes)
        self.tokenSize = attributes.get('tokenSize', self.default_tokenSize)
        self.closeCallback = attributes.get('closeCallback', None)
        self.textColor = attributes.get('textColor', redeemColors.TEXT_COLOR)
        self.padLeft = attributes.get('itemPadding', self.default_itemPadding)
        self.padRight = attributes.get('itemPadding', self.default_itemPadding)
        self.minimized = attributes.get('minimized', False)
        self.redeemTokenData = attributes.redeemTokenData
        self.isDragObject = attributes.dragEnabled
        self.typeID = self.redeemTokenData.typeID
        self.imageUrl = self.redeemTokenData.imageUrl
        self.blueprintRuns = self.redeemTokenData.blueprintRuns
        quantity = self.redeemTokenData.quantity
        portionSize = self.redeemTokenData.portionSize
        totalQuantity = quantity * portionSize
        isBpCopy = False
        if self.blueprintRuns:
            isBpCopy = True
        self.desc = attributes.desc
        self.expireDateTime = self.redeemTokenData.expireDateTime
        self.width = self.tokenSize
        self.height = self.GetTokenHeight()
        self.itemCont = Container(parent=self, name='itemCont', align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, height=self.tokenSize, width=self.tokenSize, padTop=REDEEM_TOKEN_TOP_PADDING)
        self.iconCont = Container(parent=self.itemCont, name='iconCont', align=uiconst.TOTOP, state=uiconst.UI_DISABLED, width=self.tokenSize, height=self.tokenSize)
        if not self.minimized:
            self.CreateAdditionalInformation()
        self.highlightOverlay = Sprite(name='hilite', align=uiconst.TOALL, state=uiconst.UI_DISABLED, parent=self.iconCont, texturePath='res:/UI/Texture/classes/InvItem/bgHover.png', blendMode=trinity.TR2_SBM_ADD, opacity=0.0, idx=0)
        Sprite(bgParent=self.iconCont, name='background', texturePath='res:/UI/Texture/classes/InvItem/bgNormal.png')
        if self.typeID:
            self.icon = eveIcon.Icon(parent=self.iconCont, name='icon', align=uiconst.CENTER, state=uiconst.UI_DISABLED, typeID=self.typeID, size=self.tokenSize, isCopy=isBpCopy)
        elif self.imageUrl:
            self.icon = LazyUrlSprite(name='image', parent=self.iconCont, align=uiconst.CENTER, imageUrl=self.imageUrl, state=uiconst.UI_DISABLED, height=64, width=64)
        self.quantityContainer = Container(parent=self.iconCont, name='quantityContainer', idx=0, pos=(0, 53, 32, 11), align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED, bgColor=(0, 0, 0, 0.95))
        self.quantityLabel = eveLabel.Label(parent=self.quantityContainer, left=2, maxLines=1, fontsize=9, color=self.textColor, text=totalQuantity)
        self.isNew = False
        self.tooltipPanelClassInfo = TooltipHeaderDescriptionWrapper(header=self.redeemTokenData.typeName, description=self.GenerateHintText())
        self.scale = (0.0, 0.0)

    def GetTokenHeight(self):
        tokenHeight = self.tokenSize
        if not self.minimized:
            tokenHeight += LABEL_CONTAINER_HEIGHT
        return tokenHeight

    def GenerateHintText(self):
        texts = [ t for t in [self.desc, self.GetStationLocationName(), self.GetDetailedExpiryText()] if t != '' ]
        hintText = '<br>'.join(texts)
        return hintText

    def GetStationLocationName(self):
        if not self.redeemTokenData.stationID:
            return ''
        return localization.GetByLabel('UI/RedeemWindow/RedeemableTo', desc='', station=self.redeemTokenData.stationID)

    def GetExpiryText(self):
        if not self.expireDateTime:
            return ''
        now = blue.os.GetWallclockTime()
        timeLeft = self.expireDateTime - now
        if timeLeft < 0:
            return localization.GetByLabel('UI/Generic/Expired')
        return FormatTimeIntervalShortWritten(timeLeft, showFrom=TIME_CATEGORY_DAY, showTo=TIME_CATEGORY_MINUTE)

    def GetDetailedExpiryText(self):
        expireText = ''
        if self.expireDateTime:
            expireText = localization.GetByLabel('UI/ActivatePlex/Expires', expiryDate=self.expireDateTime)
        return expireText

    def CreateAdditionalInformation(self):
        labelContainer = Container(parent=self, name='labelContainer', align=uiconst.TOTOP, height=LABEL_CONTAINER_HEIGHT)
        self.itemLabel = eveLabel.EveLabelSmall(parent=labelContainer, name='itemLabel', align=uiconst.TOTOP, text='<center>' + self.redeemTokenData.typeName + '</center>', color=self.textColor, maxLines=2)
        if self.expireDateTime:
            self.expiryTimeLabel = eveLabel.EveLabelSmall(parent=labelContainer, name='expiryTimeLabel', align=uiconst.TOTOP, text='<center>' + self.GetExpiryText() + '</center>', color=self.textColor, opacity=0.5)
        if self.redeemTokenData.stationID:
            padding = 4
            self.lockedToStationIcon = Sprite(name='lockedToStationIcon', parent=self.iconCont, align=uiconst.BOTTOMLEFT, texturePath='res:/UI/Texture/Classes/RedeemPanel/pin-location.png', padLeft=padding, padBottom=padding, width=18 + padding, height=24 + padding)

    def GetDragData(self, *args):
        fakeNode = Bunch(typeID=self.typeID, tokenInfo=(self.redeemTokenData.tokenID, self.redeemTokenData.massTokenID))
        return [fakeNode]

    def PrepareDrag(self, dragContainer, dragSource):
        t = RedeemableToken(parent=dragContainer, redeemTokenData=self.redeemTokenData, desc=self.desc, tokenSize=self.tokenSize, align=uiconst.TOPLEFT, minimized=True)
        t.AnimateIn()
        return (0, 0)

    def KillDragContainer(self, dragContainer):
        uthread.new(self.KillDragContainer_thread, dragContainer)

    def KillDragContainer_thread(self, dragContainer):
        try:
            child = dragContainer.children[0]
            child.AnimateOut()
        finally:
            uicore.layer.dragging.Flush()

    def SetScale(self, scale):
        self.scale = scale

    def AnimateIn(self, animate = True, timeOffset = 0.0, callback = None):
        endScale = (1.0, 1.0)
        if animate:
            uicore.animations.Tr2DScaleTo(self, startScale=self.scale, endScale=endScale, duration=REDEEM_ITEM_POP_IN_TIME, timeOffset=timeOffset, callback=callback)
        else:
            self.scale = endScale

    def AnimateOut(self, animate = True, timeOffset = 0.0, callback = None):
        endScale = (0.0, 0.0)
        if animate:
            uicore.animations.Tr2DScaleTo(self, startScale=self.scale, endScale=endScale, duration=REDEEM_ITEM_POP_IN_TIME, timeOffset=timeOffset, callback=callback)
        else:
            self.scale = endScale
        self.isNew = False

    def Blink(self):
        self.AnimateIn(animate=True)
        uicore.animations.BlinkIn(self.icon, duration=REDEEM_ITEM_POP_IN_TIME, timeOffset=REDEEM_ITEM_POP_IN_TIME)

    def IsNew(self):
        return self.isNew

    def SetIsNew(self, isNew):
        self.isNew = isNew

    def Close(self):
        Transform.Close(self)
        if self.closeCallback is not None:
            self.closeCallback()
