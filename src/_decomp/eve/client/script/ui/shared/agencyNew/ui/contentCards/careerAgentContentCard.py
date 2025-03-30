#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentCards\careerAgentContentCard.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.shared.agencyNew.ui.agencyUIConst import ICONSIZE_CONTENTCARD
from eve.client.script.ui.shared.agencyNew.ui.contentCards.baseContentCard import BaseContentCard
import trinity

class CareerAgentContentCard(BaseContentCard):
    default_name = 'CareerAgentContentCard'

    def ConstructContent(self):
        super(CareerAgentContentCard, self).ConstructContent()
        self.name = '{}_{}'.format(self.default_name, self.contentPiece.GetDivisionID())
        self.ConstructCareerIcon()

    def ConstructIcon(self):
        icon = Sprite(name='icon', parent=self.iconCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, pos=(0,
         0,
         ICONSIZE_CONTENTCARD,
         ICONSIZE_CONTENTCARD), spriteEffect=trinity.TR2_SFX_MASK, textureSecondaryPath='res:/UI/Texture/classes/Agency/contentCardMask.png')
        agentID = self.contentPiece.GetAgentID()
        sm.GetService('photo').GetPortrait(agentID, 128, icon)

    def GetIconTexturePath(self):
        return None

    def _GetActivityBadgeTexturePath(self):
        return None

    def UpdateCardText(self):
        self.titleLabel.SetText(self.contentPiece.GetDivisionName())
        systenNameText = self.contentPiece.GetSolarSystemAndSecurityAndNumJumpsText()
        agentNameText = self.contentPiece.GetAgentName()
        self.subtitleLabel.SetText(agentNameText + '\n' + systenNameText)
        self.bottomLabel.SetText(self.contentPiece.GetAgentCorpName())

    def ConstructCareerIcon(self):
        iconCont = Container(parent=self.mainCont, align=uiconst.TORIGHT, width=32, idx=0)
        texturePath = self.contentPiece.GetCareerTexturePath()
        Sprite(name='careerIcon', parent=iconCont, align=uiconst.TOPRIGHT, pos=(-2, 0, 32, 32), texturePath=texturePath, opacity=0.7)
