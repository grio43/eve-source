#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\loginRewards\rewardToggleButtonGroupButton.py
import uthread2
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
from carbonui.primitives.stretchspritevertical import StretchSpriteVertical
from carbonui.uicore import uicore
from eve.client.script.ui.control.eveLabel import EveLabelMedium, CaptionLabel, EveLabelLarge, EveLabelLargeBold
from eve.client.script.ui.shared.loginRewards.rewardUiConst import BLUE_TEXT_COLOR, GREEN_CHECKMARK
from localization import GetByLabel
import blue
DESELECTED_TAB_OFFSET = 6
OPACITY_LABEL_IDLE = 0.8
OPACITY_LABEL_HOVER = 1.0
OPACITY_LABEL_MOUSEDOWN = 1.2

class ToggleButtonGroupButtonHeader(Container):
    OPACITY_SELECTED = 1.0
    OPACITY_HOVER = 0.125
    TEXT_TOPMARGIN = 4
    default_bgColor = (0, 0, 0, 1)
    default_padRight = 1
    default_align = uiconst.TOLEFT_PROP
    default_state = uiconst.UI_NORMAL
    default_iconSize = 32
    default_colorSelected = None
    default_iconOpacity = 1.0
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        self.btnID = attributes.Get('btnID', None)
        self.btnIdx = attributes.Get('btnIdx', 0)
        self.totalBtnNum = attributes.Get('totalBtnNum') or 0
        self.panel = attributes.Get('panel', None)
        self.textureInfo = attributes.textureInfo
        label = attributes.Get('label', None)
        self.hint = attributes.Get('hint', None)
        btnWidth = attributes.Get('btnWidth', None)
        self.isSelected = False
        self.isDisabled = attributes.Get('isDisabled', False)
        self.labelClipperGrid = LayoutGrid(parent=self, align=uiconst.CENTER, columns=1, name='labelClipperGrid', cellSpacing=(0, 4))
        text = '<center>%s</center>' % label if btnWidth else label
        self.label = CaptionLabel(name='captionLabel', align=uiconst.CENTER, parent=self.labelClipperGrid, text=text, letterspace=-1, fontsize=34, width=btnWidth)
        self.labelShadow = CaptionLabel(name='captionLabel', align=uiconst.CENTER, parent=self.label.parent, text=text, letterspace=-1, fontsize=34, pos=(1,
         1,
         btnWidth,
         0), color=(0, 0, 0, 1))
        self.AddExtras(attributes)
        self.btnDeco = Container(name='btnDeco', parent=self, align=uiconst.TOALL, clipChildren=True)
        self.ConstructSelectedBG()
        opacity = getattr(self.textureInfo, 'textureOpacity', 1.0)
        self.bgSprite = Sprite(name='bgSprite', parent=self.btnDeco, opacity=opacity, align=getattr(self.textureInfo, 'textureAlign', uiconst.CENTERTOP), state=uiconst.UI_DISABLED, texturePath=self.textureInfo.texturePath, pos=(0,
         0,
         self.textureInfo.textureWidth,
         self.textureInfo.textureHeight))
        uthread2.start_tasklet(self._AdjustBgResolution, self.textureInfo.textureWidth, self.textureInfo.textureHeight)

    def OnButtonAdded(self):
        pass

    def _AdjustBgResolution(self, w, h):
        try:
            for x in xrange(3):
                textureWidth = self.bgSprite.renderObject.texturePrimary.atlasTexture.width
                textureHeight = self.bgSprite.renderObject.texturePrimary.atlasTexture.height
                if textureWidth and textureHeight:
                    if w != textureWidth:
                        self.textureInfo.textureWidth = textureWidth
                        self.bgSprite.width = self.textureInfo.textureWidth
                    if h != textureHeight:
                        self.textureInfo.textureHeight = textureHeight
                        self.bgSprite.height = self.textureInfo.textureHeight
                    break
                blue.synchro.Sleep(100)

        except StandardError as e:
            pass

    def AddExtras(self, attributes):
        pass

    def ConstructSelectedBG(self):
        self.selectedBG = Container(name='selectedBG', parent=self.btnDeco)
        self.headerFrame = Frame(parent=self.selectedBG, opacity=1.0, frameConst=('res:/UI/Texture/classes/LoginCampaign/imageTab_selectedStroke.png', 4, 0))
        self.headerFrame.fullOpacity = self.headerFrame.opacity
        self.selectedBar = StretchSpriteHorizontal(name='selectedBar', parent=self.selectedBG, align=uiconst.CENTERTOP, texturePath='res:/UI/Texture/classes/LoginCampaign/windowselection_bar.png', top=1, height=6, width=120, rightEdgeSize=7, leftEdgeSize=7, opacity=0.5)
        self.shadowBarLeft = StretchSpriteVertical(name='shadowBarLeft', parent=self.selectedBG, align=uiconst.TOLEFT_NOPUSH, texturePath='res:/UI/Texture/classes/LoginCampaign/imageTab_gradient.png', width=-3, left=3, rightEdgeSize=7, leftEdgeSize=7, opacity=1.0, color=(0, 0, 0, 1))
        self.shadowBarRight = StretchSpriteVertical(name='shadowBarRight', parent=self.selectedBG, align=uiconst.TORIGHT_NOPUSH, texturePath='res:/UI/Texture/classes/LoginCampaign/imageTab_gradient.png', width=3, rightEdgeSize=7, leftEdgeSize=7, opacity=1.0, color=(0, 0, 0, 1))
        self.selectedBar.fullOpacity = self.selectedBar.opacity
        self.unselectedLine = Frame(parent=self.selectedBG, opacity=1.0, frameConst=('res:/UI/Texture/classes/LoginCampaign/imageTab_unselectedStroke.png', 4, 0))

    def SetDisabled(self):
        self.isDisabled = True
        if self.label:
            self.label.opacity = 0.1
            self.labelShadow.opacity = 0.1

    def SetEnabled(self):
        self.isDisabled = False

    def _ShouldSkipMouseFeedback(self):
        return self.isSelected or self.isDisabled or self.totalBtnNum == 1

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        if self._ShouldSkipMouseFeedback():
            return
        uicore.animations.FadeTo(self.headerFrame, self.headerFrame.opacity, self.headerFrame.fullOpacity - 0.1, duration=uiconst.TIME_ENTRY)
        uicore.animations.FadeTo(self.label, self.label.opacity, OPACITY_LABEL_HOVER, duration=uiconst.TIME_ENTRY)

    def OnMouseExit(self, *args):
        if self._ShouldSkipMouseFeedback():
            return
        uicore.animations.FadeTo(self.headerFrame, self.headerFrame.opacity, 0.0, duration=uiconst.TIME_EXIT)
        uicore.animations.FadeTo(self.label, self.label.opacity, OPACITY_LABEL_IDLE, duration=uiconst.TIME_EXIT)

    def OnMouseDown(self, *args):
        if self._ShouldSkipMouseFeedback():
            return
        uicore.animations.FadeTo(self.headerFrame, self.headerFrame.opacity, self.headerFrame.fullOpacity + 0.2, duration=0.1)

    def OnMouseUp(self, *args):
        if self._ShouldSkipMouseFeedback():
            return

    def SetSelected(self, animate = True):
        self.isSelected = True
        self.headerFrame.StopAnimations()
        self.selectedBar.StopAnimations()
        self.headerFrame.opacity = self.headerFrame.fullOpacity
        self.selectedBar.opacity = self.selectedBar.fullOpacity
        self.unselectedLine.opacity = 0.0
        if self.label:
            self.label.opacity = OPACITY_LABEL_HOVER
        self.btnDeco.padTop = 0

    def SetDeselected(self, animate = True):
        self.isSelected = False
        if self.label:
            self.label.opacity = 1.0
        if self.isDisabled:
            return
        self.unselectedLine.opacity = 1.0
        self.headerFrame.opacity = 0.0
        self.selectedBar.opacity = 0.0

    def ChangePositionBasedTextures(self, selectedBtnIdx):
        self.shadowBarLeft.display = False
        self.shadowBarRight.display = False
        if selectedBtnIdx == self.btnIdx - 1:
            self.shadowBarLeft.display = True
        elif selectedBtnIdx == self.btnIdx + 1:
            self.shadowBarRight.display = True

    def IsSelected(self):
        return self.isSelected

    def OnClick(self, *args):
        if not self.isDisabled and not self.IsSelected():
            self.controller.Select(self, playSound=True)

    def HideOrShowBg(self, displayValue):
        self.bgSprite.display = displayValue


class RewardToggleButtonGroupButtonHeader(ToggleButtonGroupButtonHeader):

    def AddExtras(self, attributes):
        topText = attributes.Get('topText', None)
        text = attributes.Get('subLabel', None)
        btnWidth = attributes.Get('btnWidth', None)
        if text:
            row = self.labelClipperGrid.AddRow()
            extraInfo = ContainerAutoSize(parent=row, align=uiconst.CENTER, top=2, maxWidth=btnWidth)
            w, h = EveLabelMedium.MeasureTextSize(text=text)
            labelWidth = None
            if btnWidth and w > btnWidth:
                labelWidth = btnWidth
                text = '<center>%s</center>' % text
            EveLabelLarge(parent=extraInfo, align=uiconst.CENTER, text=text, width=labelWidth)
            Sprite(name='headerGradient', bgParent=extraInfo, texturePath='res:/UI/Texture/classes/LoginCampaign/header_textGradient.png', opacity=0.5, padding=(-40, -6, -40, -6), color=(0, 0, 0, 1))
            self.labelClipperGrid.top = 10
        if topText:
            topCont = ContainerAutoSize(parent=self, align=uiconst.CENTERTOP, top=20, maxWidth=btnWidth)
            w, h = EveLabelMedium.MeasureTextSize(text=topText)
            labelWidth = None
            if btnWidth and w > btnWidth:
                labelWidth = btnWidth
                topText = '<center>%s</center>' % topText
            EveLabelLargeBold(parent=topCont, align=uiconst.CENTER, text=topText, width=labelWidth)

    def ConstructSelectedBG(self):
        ToggleButtonGroupButtonHeader.ConstructSelectedBG(self)

    def UpdateUnseenCont(self, hasUnseenRewards):
        if hasUnseenRewards and not self.isSelected:
            self.selectedBar.color = GREEN_CHECKMARK
        else:
            self.selectedBar.color = (1.0, 1.0, 1.0, 1.0)

    def OnMouseEnter(self, *args):
        if self._ShouldSkipMouseFeedback():
            return
        ToggleButtonGroupButtonHeader.OnMouseEnter(self, *args)

    def OnMouseExit(self, *args):
        if self._ShouldSkipMouseFeedback():
            return
        ToggleButtonGroupButtonHeader.OnMouseExit(self, *args)

    def OnMouseDown(self, *args):
        if self._ShouldSkipMouseFeedback():
            return
        ToggleButtonGroupButtonHeader.OnMouseDown(self, *args)
