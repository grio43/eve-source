#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentGroupCards\horizontalContentGroupCard.py
from carbonui import TextColor, uiconst, fontconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.agencyNew.ui import agencyUIConst
from eve.client.script.ui.shared.agencyNew.ui.contentGroupCards import contentGroupCardConstants
from eve.client.script.ui.shared.agencyNew.ui.contentGroupCards.baseContentGroupCard import BaseContentGroupCard
HEADER_CONT_TOP = 16
BASE_DESCRIPTION_WIDTH = 145

class HorizontalContentGroupCard(BaseContentGroupCard):
    default_name = 'HorizontalContentGroupCard'
    default_width = contentGroupCardConstants.HORIZONTAL_CARD_WIDTH
    default_height = contentGroupCardConstants.HORIZONTAL_CARD_HEIGHT
    descriptionWidth = BASE_DESCRIPTION_WIDTH

    def ApplyAttributes(self, attributes):
        self.descriptionWidth = attributes.get('descriptionWidth', self.descriptionWidth * fontconst.fontSizeFactor)
        super(HorizontalContentGroupCard, self).ApplyAttributes(attributes)

    def Disable(self, *args):
        super(HorizontalContentGroupCard, self).Disable(*args)
        self.groupUnavailableContainer.SetAlign(uiconst.CENTERRIGHT)
        self.groupUnavailableContainer.top = 3
        self.groupUnavailableContainer.left = 10

    def ConstructHeader(self):
        self.headerCont = ContainerAutoSize(name='headerCont', parent=self.contNoTransform, align=uiconst.TOPLEFT, padLeft=1, left=-1, top=HEADER_CONT_TOP, minHeight=40)
        self.headerCont.originalLeft = self.headerCont.left
        self.ConstructLabelCont(maxWidth=contentGroupCardConstants.HORIZONTAL_CARD_WIDTH * 0.55)

    def ConstructDescriptionCont(self):
        description = self.contentGroup.GetDescription()
        self.descriptionCont = Container(name='descriptionCont', parent=self.contNoTransform, align=uiconst.TORIGHT, width=self.descriptionWidth, padTop=12, padRight=3)
        self.descriptionLabel = EveLabelMedium(name='descriptionLabel', parent=self.descriptionCont, align=uiconst.CENTER, text='<center>%s</center>' % description, maxWidth=self.descriptionWidth)
        self.descriptionBG = Frame(name='descriptionBackground', texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png', cornerSize=9, parent=self.mainCont, align=uiconst.TORIGHT, width=self.descriptionWidth, color=agencyUIConst.COLOR_BG_DARK, padding=1, padTop=12)
        if not description:
            self.descriptionCont.Hide()
            self.descriptionBG.Hide()

    def OnMouseEnter(self, *args):
        if not self.isEnabled:
            return
        super(HorizontalContentGroupCard, self).OnMouseEnter(*args)
        animations.MorphScalar(self.descriptionLabel, 'left', self.descriptionLabel.left, self.GetScaleOffsetX() - 5, duration=0.1, curveType=uiconst.ANIM_LINEAR)
        animations.FadeTo(self.descriptionLabel, self.descriptionLabel.opacity, TextColor.HIGHLIGHT.opacity, duration=0.1)

    def OnMouseExit(self, *args):
        if not self.isEnabled:
            return
        super(HorizontalContentGroupCard, self).OnMouseExit(*args)
        animations.MorphScalar(self.descriptionLabel, 'left', self.descriptionLabel.left, 0, duration=0.2, curveType=uiconst.ANIM_LINEAR)
        animations.FadeTo(self.descriptionLabel, self.descriptionLabel.opacity, TextColor.NORMAL.opacity, duration=0.2)
