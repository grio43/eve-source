#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\addressBook\buddyOnlineIndicator.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveColor
from localization import GetByLabel
STATUS_ICON_SIZE = 12
TEXTUREPATH_BLOCKED = 'res:/UI/Texture/Classes/Contacts/blockedWhite.png'
TEXTUREPATH_ONLINESTATUS = 'res:/UI/Texture/Classes/Contacts/onlineIcon.png'
COLOR_ONLINE = eveColor.SUCCESS_GREEN
COLOR_OFFLINE = eveColor.DANGER_RED
COLOR_BLOCKED = eveColor.WHITE

class BuddyOnlineIndicator(Container):
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(BuddyOnlineIndicator, self).ApplyAttributes(attributes)
        self.icon = Sprite(parent=self, align=uiconst.CENTER, pos=(0,
         0,
         STATUS_ICON_SIZE,
         STATUS_ICON_SIZE), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Contacts/onlineIcon.png', outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.25, idx=0)

    def SetOnline(self):
        self.Show()
        self.icon.SetRGBA(*COLOR_ONLINE)
        self.icon.SetTexturePath(TEXTUREPATH_ONLINESTATUS)
        self.hint = GetByLabel('UI/Common/Online')

    def SetOffline(self):
        self.Show()
        self.icon.SetRGBA(*COLOR_OFFLINE)
        self.icon.SetTexturePath(TEXTUREPATH_ONLINESTATUS)
        self.hint = GetByLabel('UI/Common/Offline')

    def SetBlocked(self):
        self.Show()
        self.icon.SetTexturePath(TEXTUREPATH_BLOCKED)

    def SetNotBlocked(self):
        self.Show()
        self.icon.SetTexturePath(TEXTUREPATH_ONLINESTATUS)
