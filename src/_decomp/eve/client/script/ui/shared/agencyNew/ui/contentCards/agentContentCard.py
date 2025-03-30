#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentCards\agentContentCard.py
import math
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.client.script.ui.shared.agencyNew.ui.agencyUIConst import ICONSIZE_CONTENTCARD
from eve.client.script.ui.shared.agencyNew.ui.contentCards.baseContentCard import BaseContentCard
from eve.client.script.ui.shared.agencyNew.ui.controls.standingThresholdCont import StandingThresholdCont
import trinity
from eve.client.script.ui.shared.cloneGrade.omegaCloneOverlayIcon import OmegaCloneOverlayIcon
from localization import GetByLabel

class AgentContentCard(BaseContentCard):
    default_name = 'AgentContentCard'

    def ConstructContent(self):
        super(AgentContentCard, self).ConstructContent()
        self.ConstructStandingThresholdCont()
        AgentLevelIcon(parent=self, align=uiconst.TOPRIGHT, contentPiece=self.contentPiece, left=5, top=1)
        self.titleLabel.padRight = 24

    def ConstructStandingThresholdCont(self):
        StandingThresholdCont(parent=self.bottomCont, align=uiconst.BOTTOMRIGHT, contentPiece=self.contentPiece, idx=0)

    def ConstructIcon(self):
        icon = Sprite(name='icon', parent=self.iconCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, pos=(0,
         0,
         ICONSIZE_CONTENTCARD,
         ICONSIZE_CONTENTCARD), spriteEffect=trinity.TR2_SFX_MASK, textureSecondaryPath='res:/UI/Texture/classes/Agency/contentCardMask.png')
        agentID = self.contentPiece.GetAgentID()
        sm.GetService('photo').GetPortrait(agentID, 128, icon)
        if self.contentPiece.GetAgentLevel() >= 4:
            OmegaCloneOverlayIcon(parent=self.iconCont, align=uiconst.TOALL, state=uiconst.UI_DISABLED, idx=0)

    def UpdateCardText(self):
        self.titleLabel.SetText(self.contentPiece.GetAgentName())
        locationText = self.contentPiece.GetSolarSystemAndSecurityAndNumJumpsText()
        self.subtitleLabel.SetText(locationText)
        self.bottomLabel.SetText(self.contentPiece.GetAgentCorpName())

    def _GetActivityBadgeTexturePath(self):
        return self.contentPiece.GetActivityBadgeTexturePath()

    def ConstructActivityBadge(self):
        super(AgentContentCard, self).ConstructActivityBadge()
        if self.contentPiece.IsLocatorAgent():
            cont = Container(parent=self.iconCont, align=uiconst.BOTTOMLEFT, pos=(0, 0, 16, 16), state=uiconst.UI_NORMAL, hint=GetByLabel('UI/Agents/Locator/LocationServices'))
            self.activityBadge = Sprite(name='activityBadge', parent=cont, align=uiconst.BOTTOMLEFT, state=uiconst.UI_DISABLED, width=37, height=37, rotation=math.pi, texturePath='res:/UI/Texture/classes/agency/ActivityBadges/badge_agentsLocator.png')

    def OnDblClick(self):
        self.contentPiece.ExecuteStartConversation()


class AgentLevelIcon(Container):
    default_width = 22
    default_height = 32
    default_bgTexturePath = 'res:/UI/Texture/classes/agency/agentLevelFrame.png'
    default_hint = GetByLabel('UI/AgentFinder/AgentLevel')
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(AgentLevelIcon, self).ApplyAttributes(attributes)
        self.contentPiece = attributes.contentPiece
        EveLabelLarge(parent=self, align=uiconst.CENTERTOP, text=self.contentPiece.GetAgentLevel(), top=2)
