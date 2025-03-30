#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\redeem\newRedeemPanel.py
from math import pi
import homestation.client
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst
from carbonui.control.scroll import MAIN_CONTAINER_PADDING
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.uicore import uicore
from eve.client.script.ui.control.eveLabel import EveCaptionMedium
from eve.client.script.ui.shared.redeem.redeemItem import GetRedeemItemHeightWithoutDescription
from eve.client.script.ui.shared.redeem.redeemItemsContainer import RedeemItemsContainer, ControlContainer, Controller
from eve.client.script.ui.shared.redeem.redeemUiConst import REDEEM_BUTTON_BACKGROUND_COLOR, REDEEM_BUTTON_BORDER_COLOR, REDEEM_BUTTON_FILL_COLOR, REDEEM_PANEL_BACKGROUND_COLOR, TEXT_COLOR
from localization import GetByLabel

def GetOneRowHeightWithoutDescription():
    return GetRedeemItemHeightWithoutDescription() + MAIN_CONTAINER_PADDING * 2


REDEEM_BUTTON_HEIGHT = 35
REDEEM_ITEMS_PADDING_TOP = 4
REDEEM_ITEMS_PADDING_BOTTOM = 2
REDEEM_ITEMS_HEIGHT = GetOneRowHeightWithoutDescription() + REDEEM_ITEMS_PADDING_TOP + REDEEM_ITEMS_PADDING_BOTTOM
DEFAULT_ANIMATION_DURATION = 0.2

class RedeemPanelNew(Container):
    isDropLocation = False

    def ApplyAttributes(self, attributes):
        super(RedeemPanelNew, self).ApplyAttributes(attributes)
        self._ReadAttributes(attributes)
        self.isCollapsed = True
        self.display = False
        self._ConstructRedeemButton()
        self._ConstructRedeemItems()
        self._ConstructCenterSection()
        self.UpdateSizes()
        self.UpdateVisibility()

    def _ReadAttributes(self, attributes):
        self.redeemData = attributes.redeemData
        self.buttonOnClick = attributes.get('buttonClick', self.ChangeCollapsedState)
        self.onVisibilityChanged = attributes.get('onVisibilityChanged', None)
        self.onCollapsibilityChanged = attributes.get('onCollapsibilityChanged', None)
        self.animationDuration = attributes.get('animationDuration', DEFAULT_ANIMATION_DURATION)
        self.instructionText = attributes.get('instructionText', None)
        self.textColor = attributes.get('textColor', TEXT_COLOR)
        self.buttonBorderColor = attributes.get('redeemButtonBorderColor', REDEEM_BUTTON_BORDER_COLOR)
        self.buttonBackgroundColor = attributes.get('redeemButtonBackgroundColor', REDEEM_BUTTON_BACKGROUND_COLOR)
        self.buttonFillColor = attributes.get('redeemButtonFillColor', REDEEM_BUTTON_FILL_COLOR)
        self.panelBackgroundColor = attributes.get('redeemPanelBackgroundColor', REDEEM_PANEL_BACKGROUND_COLOR)
        self.controller = Controller(redeem_data=self.redeemData, redeem_service=sm.GetService('redeem'), home_station_service=homestation.Service.instance())

    def _ConstructRedeemButton(self):
        self.redeemButton = RedeemButton(name='RedeemPanel_Button', parent=self, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, height=REDEEM_BUTTON_HEIGHT, OnClick=self.buttonOnClick, borderColor=self.buttonBorderColor, backgroundColor=self.buttonBackgroundColor, fillColor=self.buttonFillColor, textColor=self.textColor, animationDuration=self.animationDuration, controller=self.controller)

    def _ConstructRedeemItems(self):
        self.redeemContainer = RedeemItemsContainer(name='RedeemPanel_ItemsContainer', parent=self, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, height=REDEEM_ITEMS_HEIGHT, redeemData=self.redeemData, controller=self.controller, areItemsDraggable=True, showHeaderCount=False, showDeliveryInfo=False, showFooter=False, onContentUpdateCallback=self.OnContentUpdated, sidePadding=8, topPadding=REDEEM_ITEMS_PADDING_TOP, bottomPadding=REDEEM_ITEMS_PADDING_BOTTOM)

    def _ConstructCenterSection(self):
        Fill(name='RedeemPanel_CenterSection', bgParent=self, color=self.panelBackgroundColor, opacity=0.8)

    def IsCollapsed(self):
        return self.isCollapsed

    def OnContentUpdated(self):
        if self.destroyed:
            return
        self.UpdateVisibility()
        self.UpdateSizes()

    def UpdateVisibility(self):
        areTokensAvailable = self.redeemContainer.HasTokens()
        isRedeemContainerVisible = self.redeemContainer.IsVisible()
        if isRedeemContainerVisible and not areTokensAvailable:
            self.HidePanel()
            return True
        if not isRedeemContainerVisible and areTokensAvailable:
            self.ShowPanel()
            return True
        return False

    def UpdateSizes(self):
        self.height = self.GetCollapsedHeight() if self.IsCollapsed() else self.GetExpandedHeight()

    def GetExpandedHeight(self):
        return self.redeemButton.height + self.redeemContainer.height

    def GetCollapsedHeight(self):
        return self.redeemButton.height

    def ChangeCollapsedState(self):
        if self.isCollapsed:
            self.ExpandPanel()
        else:
            self.CollapsePanel()
        if self.onCollapsibilityChanged:
            self.onCollapsibilityChanged()

    def ShowPanel(self, animate = True):
        if self.IsHidden() and animate:
            self.CollapsePanel(animate=False)
            self.top = -self.height
            self.Show()
            startTop = self.top
            endTop = 0
            uicore.animations.MorphScalar(self, 'top', startTop, endTop, self.animationDuration)
        else:
            self.top = 0
            self.Show()

    def HidePanel(self, animate = True):
        if not self.IsHidden() and animate:
            timeOffset = 0.0
            if not self.isCollapsed:
                self._Collapse(animate)
                timeOffset = self.animationDuration
            startTop = self.top
            endTop = -self.GetCollapsedHeight()
            animation = uicore.animations.MorphScalar
            animation(self, 'top', startTop, endTop, self.animationDuration, timeOffset=timeOffset, callback=self.Hide)
        else:
            self.top = -self.height
            self.Hide()

    def ExpandPanel(self, animate = True):
        self.redeemButton.Expand(animate)
        startHeight = self.height
        endHeight = self.GetExpandedHeight()
        if animate:
            uicore.animations.MorphScalar(self, 'height', startHeight, endHeight, self.animationDuration)
        else:
            self.height = endHeight
        self.isCollapsed = False

    def CollapsePanel(self, animate = True):
        self.redeemButton.Collapse(animate)
        self._Collapse(animate)
        self.isCollapsed = True

    def _Collapse(self, animate):
        startHeight = self.height
        endHeight = self.GetCollapsedHeight()
        if animate:
            uicore.animations.MorphScalar(self, 'height', startHeight, endHeight, self.animationDuration)
        else:
            self.height = endHeight

    def Hide(self):
        wasHidden = self.IsHidden()
        super(RedeemPanelNew, self).Hide()
        if not wasHidden and self.onVisibilityChanged:
            self.onVisibilityChanged()

    def Show(self):
        wasHidden = self.IsHidden()
        super(RedeemPanelNew, self).Show()
        if wasHidden and self.onVisibilityChanged:
            self.onVisibilityChanged()

    def FadeOut(self):
        if self.IsHidden():
            return
        startVal = self.opacity
        endVal = 0.0
        uicore.animations.MorphScalar(self, 'opacity', startVal, endVal, duration=self.animationDuration)


class RedeemButton(Transform):
    default_name = 'RedeemButton'

    def ApplyAttributes(self, attributes):
        Transform.ApplyAttributes(self, attributes)
        borderColor = attributes.get('borderColor', REDEEM_BUTTON_BORDER_COLOR)
        backgroundColor = attributes.get('backgroundColor', REDEEM_BUTTON_BACKGROUND_COLOR)
        fillColor = attributes.get('fillColor', REDEEM_BUTTON_FILL_COLOR)
        textColor = attributes.get('textColor', TEXT_COLOR)
        self.animationDuration = attributes.get('animationDuration', DEFAULT_ANIMATION_DURATION)
        controller = attributes.controller
        Line(parent=self, color=borderColor, align=uiconst.TOTOP, weight=1)
        Fill(bgParent=self, color=backgroundColor)
        borderFillColor = fillColor[:3]
        self.borderFill = GradientSprite(bgParent=self, rgbData=[(0, borderFillColor), (0.5, borderFillColor), (1.0, borderFillColor)], alphaData=[(0.3, 0.1), (0.5, 0.4), (0.7, 0.1)], idx=0, state=uiconst.UI_DISABLED)
        self.onClick = attributes.get('OnClick', None)
        self.captionCont = Container(parent=self, name='captionCont', align=uiconst.CENTERTOP)
        self.expanderIcon = Sprite(parent=self.captionCont, texturePath='res:/UI/Texture/Icons/105_32_5.png', align=uiconst.CENTERRIGHT, pos=(0, 0, 32, 32), state=uiconst.UI_DISABLED, color=textColor)
        self.availableLabel = EveCaptionMedium(parent=self.captionCont, align=uiconst.CENTERLEFT, text=GetByLabel('UI/RedeemWindow/RedeemableItems'), state=uiconst.UI_DISABLED, color=textColor, bold=False)
        self.availableLabel.letterspace = 1
        self.captionCont.width = self.availableLabel.textwidth + 10 + self.expanderIcon.width
        self.captionCont.height = max(self.availableLabel.textheight + 10, self.expanderIcon.height)
        self.height = self.captionCont.height
        leftPadding = 20
        availableSpace = (uicore.desktop.width - self.captionCont.width - leftPadding) / 2
        self.controlCont = ControlContainer(parent=self, align=uiconst.CENTERRIGHT, controller=controller, left=leftPadding, availableSpace=availableSpace)
        push = sm.GetService('window').GetCameraLeftOffset(self.captionCont.width, align=uiconst.CENTERTOP, left=0)
        self.captionCont.left = push

    def Expand(self, animate = True):
        PlaySound(uiconst.SOUND_EXPAND)
        self.Animate(0, animate)
        self.ShowOrHideControls(1, animate)

    def Collapse(self, animate = True):
        PlaySound(uiconst.SOUND_COLLAPSE)
        self.Animate(pi, animate)
        self.ShowOrHideControls(0, animate)

    def Animate(self, endVal, animate):
        if animate:
            startVal = self.expanderIcon.rotation
            uicore.animations.MorphScalar(self.expanderIcon, 'rotation', startVal, endVal, self.animationDuration)
            uicore.animations.FadeOut(self.controlCont, duration=self.animationDuration)
        else:
            self.expanderIcon.rotation = endVal
            uicore.animations.FadeIn(self.controlCont, duration=self.animationDuration)

    def ShowOrHideControls(self, display, animate):
        if animate:
            if display:
                self.controlCont.Show()
                uicore.animations.FadeIn(self.controlCont, duration=self.animationDuration, callback=self.controlCont.Show)
            else:
                uicore.animations.FadeOut(self.controlCont, duration=self.animationDuration, callback=self.controlCont.Hide)
        else:
            self.controlCont.display = False

    def DefaultOnClick(self):
        pass

    def OnClick(self, *args):
        if self.onClick:
            self.onClick()

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
