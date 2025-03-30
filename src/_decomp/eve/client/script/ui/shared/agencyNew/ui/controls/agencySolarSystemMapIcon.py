#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\controls\agencySolarSystemMapIcon.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.shared.agencyNew.ui import agencyUIConst
from eve.client.script.ui.shared.maps.solarSystemMapIcon import SolarSystemMapIcon

class AgencySolarSystemMapIcon(Container):
    default_name = 'AgencySolarSystemMapIcon'

    def ApplyAttributes(self, attributes):
        super(AgencySolarSystemMapIcon, self).ApplyAttributes(attributes)
        self.contentPiece = attributes.contentPiece
        ssmap = SolarSystemMapIcon(parent=self)
        ssmap.Draw(self.contentPiece.GetDestinationSolarSystemID(), 76)
        Sprite(name='bgSprite', bgParent=self, align=uiconst.TOALL, texturePath='res:/UI/Texture/classes/Agency/contentCardMask.png', color=agencyUIConst.COLOR_BG)
