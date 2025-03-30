#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\controls\standingThresholdCont.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.shared.agencyNew.ui import agencyUIConst
from eve.client.script.ui.station.agents.agentUtil import GetAgentUnavailableReason

class StandingThresholdCont(Container):
    default_name = 'StandingThresholdCont'
    default_state = uiconst.UI_NORMAL
    default_width = 22
    default_height = 24

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.contentPiece = attributes.contentPiece
        self.icon = Sprite(name='icon', parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, pos=(0, 0, 16, 16), texturePath='res:/UI/Texture/Shared/checkboxHalfChecked.png', color=agencyUIConst.COLOR_UNAVAILABLE_HILIGHT)
        self.bgFill = Frame(name='oneCornerSolidFrame', bgParent=self, texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png', cornerSize=9, color=agencyUIConst.COLOR_UNAVAILABLE, opacity=0.5)
        self.UpdateStanding()

    def GetHint(self):
        return GetAgentUnavailableReason(self.contentPiece.GetAgentID())

    def UpdateStanding(self):
        if self.contentPiece.IsAvailable():
            self.Hide()
        else:
            self.Show()
