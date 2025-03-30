#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentGroupCards\baseContentGroupCard.py
import carbonui.fontconst
import trinity
from carbonui import TextColor, uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelLargeBold, EveHeaderMedium, Label
from eve.client.script.ui.shared.agencyNew import agencySignals, agencyEventLog
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentGroups.contentGroupConst import contentGroupsEnabledInWormholes, NEW_FEATURE_CONTENT_GROUP_OFFSET
from eve.client.script.ui.shared.agencyNew.ui import agencyUIConst
from eve.client.script.ui.shared.agencyNew.ui.contentGroupCards import contentGroupCardConstants
from eve.common.script.sys.idCheckers import IsKnownSpaceSystem, IsAbyssalSpaceSystem
from eve.common.script.sys.idCheckers import IsVoidSpaceSystem
from localization import GetByLabel
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst

class BaseContentGroupCard(Container):
    default_name = 'BaseContentGroupCard'
    default_state = uiconst.UI_NORMAL
    default_opacity = 0.0
    scaleDistance = 20
    bgScalingCenter = (0.0, 0.5)
    maskTexture = 'res:/UI/Texture/classes/Agency/navMask.png'
    baselineBackgroundScaleX = 1.0
    baselineBackgroundScaleY = 1.0

    def ApplyAttributes(self, attributes):
        super(BaseContentGroupCard, self).ApplyAttributes(attributes)
        self.contentGroup = attributes.contentGroup
        self.contentGroupID = attributes.contentGroupID
        self.index = attributes.index
        self.uniqueUiName = pConst.GetUniqueAgencyCardName(self.contentGroupID)
        self.isEnabled = True
        self.cardTitle = None
        self.titleFrame = None
        self.textureSecondaryPath = attributes.get('texturePath') or self.contentGroup.GetBackgroundTexture()
        self.ConstructBaseLayout()
        self.ConstructLayout()
        if self.ShouldDisable():
            self.Disable()

    def ShouldDisable(self):
        if not self.contentGroup.IsEnabled():
            return True
        if not IsKnownSpaceSystem(session.solarsystemid2):
            contentGroupID = self.contentGroup.GetID()
            if contentGroupID >= NEW_FEATURE_CONTENT_GROUP_OFFSET:
                return False
            if contentGroupID not in contentGroupsEnabledInWormholes:
                return True
        return False

    def Disable(self, *args):
        self.isEnabled = False
        self.strokeFrame.SetRGBA(*agencyUIConst.CONTENT_GROUP_CARD_DISABLED_COLOR)
        self.cardTitle.SetTextColor(agencyUIConst.CONTENT_GROUP_CARD_TITLE_DISABLED_COLOR)
        self.titleFrame.SetRGBA(*agencyUIConst.CONTENT_GROUP_CARD_TITLE_DISABLED_COLOR)
        self.backgroundSprite.SetAlpha(0.3)
        self.groupUnavailableContainer.SetState(uiconst.UI_DISABLED)

    def ConstructBaseLayout(self):
        self.contNoTransform = Container(name='contNoTransform', parent=self)
        self.transform = Transform(parent=self, align=uiconst.TOALL, scalingCenter=(0.5, 0.5))
        self.ConstructMainContainer()
        self.ConstructHeader()
        self.ConstructBackground()
        self.ConstructDescriptionCont()
        self.ConstructNewContentLabel()
        self.ConstructGroupUnavailableContainer()

    def ConstructMainContainer(self):
        self.mainCont = Container(name='mainCont', parent=self.transform)

    def ConstructGroupUnavailableContainer(self):
        self.groupUnavailableContainer = ContainerAutoSize(name='groupUnavailableContainer', parent=self.mainCont, align=uiconst.CENTER, minHeight=35, top=-10, state=uiconst.UI_HIDDEN, alignMode=uiconst.CENTER)
        Frame(bgParent=self.groupUnavailableContainer, color=agencyUIConst.CONTENT_GROUP_CARD_DISABLED_COLOR, texturePath='res:/UI/Texture/Shared/DarkStyle/panel2Corner_Stroke.png', cornerSize=9)
        Sprite(name='tilingDecoSlantTop', parent=self.groupUnavailableContainer, align=uiconst.TOTOP, tileX=True, height=3, texturePath='res:/UI/Texture/Shared/DarkStyle/decoSlant_TileR.png', opacity=0.4, padRight=5, padLeft=5, top=2, left=2, color=agencyUIConst.CONTENT_GROUP_CARD_DISABLED_COLOR)
        Sprite(name='tilingDecoSlantBot', parent=self.groupUnavailableContainer, align=uiconst.TOBOTTOM, tileX=True, height=3, texturePath='res:/UI/Texture/Shared/DarkStyle/decoSlant_TileR.png', opacity=0.4, padLeft=2, padRight=5, top=2, color=agencyUIConst.CONTENT_GROUP_CARD_DISABLED_COLOR)
        Sprite(name='warningIcon', parent=self.groupUnavailableContainer, align=uiconst.CENTERLEFT, width=22, height=22, left=5, texturePath='res:/UI/Texture/classes/agency/iconExclamation.png', color=agencyUIConst.CONTENT_GROUP_CARD_DISABLED_COLOR, state=uiconst.UI_DISABLED)
        Frame(bgParent=self.groupUnavailableContainer, color=(0, 0, 0, 1), texturePath='res:/UI/Texture/Shared/DarkStyle/panel2Corner_Solid.png', cornerSize=9)
        text = GetByLabel('UI/Agency/currentlyUnavailable')
        if not (IsKnownSpaceSystem(session.solarsystemid2) or IsAbyssalSpaceSystem(session.solarsystemid2) or IsVoidSpaceSystem(session.solarsystemid2)):
            text = GetByLabel('UI/Agency/UnavailableInWormholes')
        EveHeaderMedium(parent=self.groupUnavailableContainer, align=uiconst.CENTER, maxWidth=160, color=agencyUIConst.CONTENT_GROUP_CARD_DISABLED_LABEL_COLOR, text=text, padding=(40, 8, 20, 8))

    def ConstructNewContentLabel(self):
        self.newContentLabelContainer = ContainerAutoSize(name='newContentLabelContainer', parent=self.mainCont, align=uiconst.TOPLEFT, alignMode=uiconst.CENTERLEFT, top=13, left=1, maxWidth=150, clipChildren=True, opacity=0.0)
        Sprite(name='cornerSprite', parent=self.newContentLabelContainer, align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Shared/DarkStyle/cornerTriSmall.png', pos=(1, 1, 5, 5), color=TextColor.NORMAL, state=uiconst.UI_DISABLED)
        StretchSpriteHorizontal(name='newContentStretchSprite', bgParent=self.newContentLabelContainer, texturePath='res:/UI/Texture/classes/agency/newContentFrame.png', rightEdgeSize=30, color=eveColor.CRYO_BLUE)
        self.newContentLabel = EveLabelLargeBold(name='newContentLabel', parent=self.newContentLabelContainer, align=uiconst.CENTERLEFT, text=GetByLabel('UI/Agency/newContent'), color=TextColor.NORMAL, left=10, padRight=30)
        self.CheckShowNewContentLabel()

    def CheckShowNewContentLabel(self):
        if self.contentGroup.IsNewContentAvailable() or self.contentGroup.IsChildNewContentAvailable():
            self.newContentLabel.Show()
            animations.BlinkIn(self.newContentLabelContainer, timeOffset=0.45)
        else:
            self.newContentLabel.Hide()

    def ConstructLayout(self):
        pass

    def ConstructHeader(self):
        pass

    def ConstructDescriptionCont(self):
        pass

    def ConstructBackground(self):
        self.bgContainer = Container(name='bgContainer', align=uiconst.TOALL, state=uiconst.UI_DISABLED, parent=self.transform)
        self.ConstructBackgroundTextured()

    def ConstructBackgroundTextured(self):
        StretchSpriteHorizontal(name='navButtonTopSprite', parent=self.bgContainer, texturePath='res:/UI/Texture/classes/Agency/navButtonTop.png', align=uiconst.TOTOP_NOPUSH, height=8, rightEdgeSize=10, leftEdgeSize=10, padding=(1, 1, 1, 1))
        self.strokeFrame = Frame(name='strokeFrame', parent=self.bgContainer, texturePath='res:/UI/Texture/Shared/DarkStyle/panel2Corner_Stroke.png', opacity=0.1, cornerSize=9)
        self.backgroundSprite = Frame(name='bgSprite', parent=self.bgContainer, align=uiconst.TOALL, textureSecondaryPath=self.textureSecondaryPath, texturePath=self.maskTexture, spriteEffect=trinity.TR2_SFX_MODULATE, cornerSize=10)
        if self.backgroundSprite.textureSecondary:
            self.backgroundSprite.textureSecondary.scale = (self.baselineBackgroundScaleX, self.baselineBackgroundScaleY)
            self.backgroundSprite.textureSecondary.scalingCenter = self.bgScalingCenter
            self.backgroundSprite.textureSecondary.useTransform = True

    def AnimEnter(self, offsetValue):
        timeOffset = 0.05 * offsetValue
        duration = 0.3
        animations.Tr2DScaleTo(self.transform, (0.9, 0.9), (1.0, 1.0), duration=duration, timeOffset=timeOffset)
        animations.FadeIn(self, duration=2 * duration, timeOffset=timeOffset)

    def OnClick(self, *args):
        if self.contentGroup.IsEnabled():
            if self.contentGroup.IsExternalGroup():
                self.contentGroup.CallExternalFunc()
            else:
                agencySignals.on_content_group_selected(self.contentGroup.GetID())
            agencyEventLog.LogEventGroupCardClicked(self.contentGroup)

    def OnMouseEnter(self, *args):
        if not self.isEnabled:
            return
        super(BaseContentGroupCard, self).OnMouseEnter(*args)
        animations.MorphScalar(self.headerCont, 'left', self.headerCont.left, -self.GetScaleOffsetX(), duration=0.1, curveType=uiconst.ANIM_LINEAR)
        animations.SpColorMorphTo(self.cardTitle, endColor=TextColor.HIGHLIGHT, duration=0.1)
        animations.FadeTo(self.strokeFrame, self.strokeFrame.opacity, 0.2, duration=0.1)
        endVal = (self.baselineBackgroundScaleX * 0.9, self.baselineBackgroundScaleY * 0.9)
        animations.MorphVector2(self.backgroundSprite.textureSecondary, 'scale', self.backgroundSprite.textureSecondary.scale, endVal, duration=3.0, curveType=uiconst.ANIM_LINEAR)
        scale = self._GetScaleFactor()
        animations.Tr2DScaleTo(self.transform, self.transform.scale, (scale, scale), duration=0.1, curveType=uiconst.ANIM_LINEAR)

    def OnMouseExit(self, *args):
        if not self.isEnabled or not self.backgroundSprite.textureSecondary:
            return
        super(BaseContentGroupCard, self).OnMouseExit(*args)
        newLeft = getattr(self.headerCont, 'originalLeft', 0)
        animations.MorphScalar(self.headerCont, 'left', self.headerCont.left, newLeft, duration=0.2, curveType=uiconst.ANIM_LINEAR)
        animations.SpColorMorphTo(self.cardTitle, endColor=TextColor.NORMAL, duration=0.1)
        animations.FadeTo(self.strokeFrame, self.strokeFrame.opacity, 0.1, duration=0.1)
        endVal = (self.baselineBackgroundScaleX * 1.0, self.baselineBackgroundScaleY * 1.0)
        animations.MorphVector2(self.backgroundSprite.textureSecondary, 'scale', self.backgroundSprite.textureSecondary.scale, endVal, duration=0.2, curveType=uiconst.ANIM_LINEAR)
        animations.Tr2DScaleTo(self.transform, self.transform.scale, (1.0, 1.0), duration=0.2, curveType=uiconst.ANIM_LINEAR)

    def _GetScaleFactor(self):
        x = self.width
        scale = (x + self.scaleDistance) / float(x)
        return scale

    def GetScaleOffsetX(self):
        return int(self.width * (self._GetScaleFactor() - 1.0) / 2.0)

    def GetScaleOffsetY(self):
        return int(self.height * (self._GetScaleFactor() - 1.0) / 2.0)

    def GetHint(self):
        if not self.contentGroup.IsEnabled():
            return self.contentGroup.GetDisabledHint()

    def ConstructLabelCont(self, maxWidth = contentGroupCardConstants.VERTICAL_CARD_WIDTH):
        labelCont = ContainerAutoSize(name='labelCont', parent=self.headerCont, align=uiconst.CENTERLEFT, top=-5, left=1, minHeight=50, alignMode=uiconst.TOPLEFT)
        self.titleFrame = Frame(name='topContFrame', bgParent=labelCont, texturePath='res:/UI/Texture/classes/Agency/navButtonTitleBar.png', cornerSize=26, color=eveColor.CRYO_BLUE, opacity=0.9)
        titleCont = ContainerAutoSize(name='titleCont', parent=labelCont, align=uiconst.TOPLEFT, top=22, padding=(15, 4, 10, 4), alignMode=uiconst.TOPLEFT)
        if self.contentGroup.IsExternalGroup() and not self.contentGroup.OpensWithinAgency():
            self.titleFrame.padRight -= 18
            maxWidth -= 18
            s = Sprite(name='externalContent', parent=labelCont, align=uiconst.TOPRIGHT, texturePath='res:/UI/Texture/classes/agency/iconExternalContent.png', pos=(0,
             titleCont.top + 3,
             24,
             24), color=TextColor.NORMAL, state=uiconst.UI_NORMAL, hint=GetByLabel('UI/Agency/ExternalContentHint'))
            s.OnClick = self.OnClick
        self.cardTitle = Label(parent=titleCont, align=uiconst.TOPLEFT, text=self.contentGroup.GetName(), fontsize=17, fontStyle=carbonui.fontconst.STYLE_HEADER, color=TextColor.NORMAL, maxWidth=maxWidth - 35, padRight=15)
