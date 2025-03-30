#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentCards\baseContentCard.py
import math
import uthread2
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import TextColor, uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
from carbonui.uianimations import animations
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelLarge
from eve.client.script.ui.shared.agencyNew import agencyEventLog
from eve.client.script.ui.shared.agencyNew.ui import agencyUIConst
from eve.client.script.ui.shared.agencyNew.ui.controls.agencySolarSystemMapIcon import AgencySolarSystemMapIcon
from localization import GetByLabel
from signals import signal
OPACITY_HOVER = 0.2
OPACITY_SELECTED = 0.15
OPACITY_IDLE = 0.1

class BaseContentCard(ContainerAutoSize):
    default_name = 'BaseContentCard'
    contentType = None
    default_state = uiconst.UI_NORMAL
    hasTimer = False
    isDragObject = True
    default_scalingCenter = (0.5, 0.5)
    default_opacity = 0.0
    default_minHeight = agencyUIConst.CONTENTCARD_HEIGHT
    default_width = agencyUIConst.CONTENTCARD_WIDTH
    default_alignMode = uiconst.TOTOP
    __notifyevents__ = ['OnDestinationSet']

    def ApplyAttributes(self, attributes):
        super(BaseContentCard, self).ApplyAttributes(attributes)
        self.onCardSelectedSignal = signal.Signal(signalName='onCardSelectedSignal')
        self.isSelected = False
        self.contentPiece = attributes.contentPiece
        self.contentGroupID = attributes.contentGroupID
        self.ConstructBaseLayout()
        self.ConstructIcon()
        self.ConstructContent()
        if self.contentPiece.isNew:
            self.ConstructNewContentIcon()
        uthread2.StartTasklet(self.Update)
        sm.RegisterNotify(self)

    def ConstructBaseLayout(self):
        self.ConstructBackground()
        self.ConstructIconContainer()
        self.ConstructActivityBadge()
        self.ConstructMainContainer()
        self.ConstructBottomCont()

    def Update(self):
        self.UpdateCardText()

    def ConstructContent(self):
        self.ConstructTitleLabel()
        self.ConstructSubtitleLabel()
        self.ConstructBottomLabel()

    def ConstructIconContainer(self):
        self.leftCont = Container(name='iconCont', parent=self, align=uiconst.TOLEFT, width=84)
        self.iconCont = Container(name='iconCont', parent=self.leftCont, align=uiconst.CENTER, pos=(0, 0, 76, 76))

    def ConstructActivityBadge(self):
        activityBadgeTexturePath = self._GetActivityBadgeTexturePath()
        self.activityBadge = Sprite(name='activityBadge', parent=self.iconCont, align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED, width=37, height=37, texturePath=activityBadgeTexturePath)

    def _GetActivityBadgeTexturePath(self):
        activityBadgeTexturePath = agencyUIConst.ACTIVITY_BADGES_BY_CONTENT_GROUP.get(self.contentGroupID, '')
        return activityBadgeTexturePath

    def ConstructMainContainer(self):
        self.mainCont = ContainerAutoSize(name='mainCont', parent=self, align=uiconst.TOTOP, padding=(4, 6, 6, 0), clipChildren=True, alignMode=uiconst.TOTOP, minHeight=40)

    def OnDestinationSet(self, destID):
        self.UpdateCardText()

    def ConstructBackground(self):
        self.backgroundContainer = Container(name='backgroundContainer', bgParent=self, opacity=agencyUIConst.OPACITY_SLANTS)
        self.cornerTriangle = Sprite(name='cornerTriSmall', parent=self, align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/Shared/DarkStyle/cornerTriSmall.png', width=5, height=5, opacity=0.3)
        StretchSpriteHorizontal(name='contentCardTop', parent=self.backgroundContainer, align=uiconst.TOTOP_NOPUSH, texturePath='res:/UI/Texture/classes/Agency/contentCardTop.png', height=11, leftEdgeSize=9)
        StretchSpriteHorizontal(name='contentCardBot', parent=self.backgroundContainer, align=uiconst.TOBOTTOM_NOPUSH, texturePath='res:/UI/Texture/classes/Agency/contentCardTop.png', height=11, rotation=math.pi, leftEdgeSize=9)
        self.selectedFill = Frame(name='selected', bgParent=self, texturePath='res:/UI/Texture/Shared/DarkStyle/panel2Corner_Solid.png', color=Color.WHITE, opacity=0.0, cornerSize=9)
        self.hoverFill = Frame(name='selected', bgParent=self, texturePath='res:/UI/Texture/Shared/DarkStyle/panel2Corner_Solid.png', color=Color.WHITE, opacity=0.0, cornerSize=9)
        Frame(name='bgFill', bgParent=self, texturePath='res:/UI/Texture/Shared/DarkStyle/panel2Corner_Solid.png', color=Color.BLACK, opacity=0.3, cornerSize=9)

    def Select(self):
        self.isSelected = True
        animations.FadeTo(self.selectedFill, self.selectedFill.opacity, OPACITY_SELECTED, duration=0.4)
        animations.FadeTo(self.cornerTriangle, self.cornerTriangle.opacity, 1.0, duration=0.4)

    def Deselect(self):
        self.isSelected = False
        animations.FadeTo(self.selectedFill, self.selectedFill.opacity, 0.0, duration=0.4)
        animations.FadeTo(self.cornerTriangle, self.cornerTriangle.opacity, 0.3, duration=0.4)

    def ConstructIcon(self):
        AgencySolarSystemMapIcon(parent=self.iconCont, contentPiece=self.contentPiece)
        self.ConstructBackgroundTexture()

    def ConstructBackgroundTexture(self):
        texturePath = self._GetBgTexturePath()
        Sprite(name='bgSprite', texturePath=texturePath, bgParent=self, idx=0)

    def _GetBgTexturePath(self):
        typeID = self.contentPiece.GetSunTypeID()
        return agencyUIConst.SUN_BG_BY_TYPEID.get(typeID, None)

    def ConstructNewContentIcon(self):
        self.newContentIcon = Sprite(name='NewContentIcon', parent=self.iconCont, align=uiconst.TOPLEFT, height=32, width=32, state=uiconst.UI_NORMAL, texturePath='res:/UI/Texture/Classes/agency/Icons/NEW32.png', hint=GetByLabel('UI/Agency/NewContentHint'))

    def ConstructBottomLabel(self):
        self.bottomLabel = EveLabelMedium(parent=self.bottomCont, name='bottomLabel', align=uiconst.TOTOP, padding=4)

    def ConstructBottomCont(self):
        self.bottomCont = ContainerAutoSize(name='bottomCont', parent=self, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, minHeight=20, padding=(4, 6, 6, 6))
        Frame(bgParent=self.bottomCont, texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png', cornerSize=9, color=agencyUIConst.COLOR_BG)

    def ConstructSubtitleLabel(self):
        self.subtitleLabel = EveLabelMedium(name='cardTextLabel', parent=self.mainCont, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, color=TextColor.SECONDARY)
        self.subtitleLabel.OnClick = self.OnClick
        self.subtitleLabel.GetMenu = self.GetMenu

    def ConstructTitleLabel(self):
        self.titleLabel = EveLabelLarge(name='cardTitleLabel', parent=self.mainCont, align=uiconst.TOTOP, maxLines=1, color=TextColor.NORMAL, state=uiconst.UI_NORMAL)
        self.titleLabel.OnClick = self.OnClick
        self.titleLabel.GetMenu = self.GetMenu

    def UpdateCardText(self):
        self.titleLabel.SetText(self.contentPiece.GetTitle())
        self.subtitleLabel.SetText(self.contentPiece.GetCardText())

    def GetMenu(self):
        return self.contentPiece.GetMenu() or []

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_ENTRY_HOVER)
        animations.FadeTo(self.hoverFill, self.hoverFill.opacity, OPACITY_HOVER, duration=0.1)

    def OnMouseExit(self, *args):
        animations.FadeTo(self.hoverFill, self.hoverFill.opacity, 0.0, duration=0.2)

    def AnimEnter(self, offsetIdx = 0):
        timeOffset = 0.05 * offsetIdx
        duration = 0.3
        animations.Tr2DScaleTo(self, (0.9, 0.9), (1.0, 1.0), duration=duration, timeOffset=timeOffset)
        animations.FadeIn(self, duration=2 * duration, timeOffset=timeOffset)

    def OnClick(self, *args):
        PlaySound('agency_window5_play')
        PlaySound(uiconst.SOUND_ENTRY_SELECT)
        self.onCardSelectedSignal(self)
        agencyEventLog.LogEventCardClicked(self.contentPiece)

    def GetDragData(self):
        return self.contentPiece.GetDragData()
