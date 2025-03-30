#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentGroupCards\verticalContentGroupCard.py
import blue
import eveformat
import uthread
from baseContentGroupCard import BaseContentGroupCard
from carbonui import TextColor, uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.uianimations import animations
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import EveHeaderLarge, EveLabelMedium, EveLabelLarge
from eve.client.script.ui.shared.agencyNew.ui import agencyUIConst
from eve.client.script.ui.shared.agencyNew.ui.contentGroupCards import contentGroupCardConstants
HEADER_CONT_TOP = 35

class VerticalContentGroupCard(BaseContentGroupCard):
    default_name = 'VerticalContentGroupCard'
    default_align = uiconst.TOTOP
    default_width = contentGroupCardConstants.VERTICAL_CARD_WIDTH
    default_height = contentGroupCardConstants.VERTICAL_CARD_HEIGHT
    descriptionHeight = contentGroupCardConstants.VERTICAL_CARD_FOOTER_CONTAINER_HEIGHT

    def ConstructLayout(self):
        super(VerticalContentGroupCard, self).ConstructLayout()
        self.CheckConstructExpiryLabel()

    def ConstructBackgroundTextured(self):
        super(VerticalContentGroupCard, self).ConstructBackgroundTextured()
        EveLabelLarge(name='indexLabel', parent=self.bgContainer, align=uiconst.TOPRIGHT, top=-20, text=self.GetFormattedIndex(), color=Color.GRAY, opacity=0.2)

    def GetFormattedIndex(self):
        if self.index is not None:
            return format(self.index + 1, '02')

    def ConstructHeader(self):
        self.headerCont = Container(name='headerContainer', parent=self.contNoTransform, align=uiconst.TOTOP, height=55, top=HEADER_CONT_TOP)
        self.ConstructLabelCont(self.width)

    def CheckConstructExpiryLabel(self):
        if self.contentGroup.IsEnabled() and self.contentGroup.GetTimeRemaining():
            self.expiryLabel = EveHeaderLarge(name='expiryLabel', parent=self, align=uiconst.CENTERTOP, top=-35)
            uthread.new(self.UpdateExpiryLabelThread)

    def UpdateExpiryLabelThread(self):
        while not self.destroyed:
            self.expiryLabel.SetText(self.contentGroup.GetExpiryTimeText())
            blue.synchro.SleepWallclock(100)

    def ConstructDescriptionCont(self):
        self.descriptionCont = ContainerAutoSize(name='descriptionCont', parent=self.contNoTransform, align=uiconst.TOBOTTOM, minHeight=self.descriptionHeight, padding=(1, 1, 1, 1), state=uiconst.UI_DISABLED)
        self.descriptionLabel = EveLabelMedium(name='descriptionLabel', parent=self.descriptionCont, align=uiconst.CENTER, width=self.width - 30, text=eveformat.center(self.contentGroup.GetDescription()), color=TextColor.NORMAL, state=uiconst.UI_DISABLED, padding=(0, 4, 0, 16))
        self.descriptionCont.SetSizeAutomatically()
        self.descriptionBG = Frame(name='descriptionBackground', parent=self.mainCont, align=uiconst.TOBOTTOM, height=self.descriptionCont.height, padding=1, texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png', cornerSize=9, color=agencyUIConst.COLOR_BG_DARK, state=uiconst.UI_DISABLED)

    def OnMouseEnter(self, *args):
        if self.destroyed or not self.isEnabled:
            return
        super(VerticalContentGroupCard, self).OnMouseEnter(*args)
        animations.MorphScalar(self.descriptionLabel, 'top', self.descriptionLabel.top, self.GetScaleOffsetY(), duration=0.1, curveType=uiconst.ANIM_LINEAR)
        animations.FadeTo(self.descriptionLabel, self.descriptionLabel.opacity, TextColor.HIGHLIGHT.opacity, duration=0.1)

    def OnMouseExit(self, *args):
        if not self.isEnabled:
            return
        super(VerticalContentGroupCard, self).OnMouseExit(*args)
        animations.MorphScalar(self.descriptionLabel, 'top', self.descriptionLabel.top, 0, duration=0.2, curveType=uiconst.ANIM_LINEAR)
        animations.FadeTo(self.descriptionLabel, self.descriptionLabel.opacity, TextColor.NORMAL.opacity, duration=0.2)
