#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\studio\circularButtonIcon.py
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveThemeColor

class CircularButtonIcon(ButtonIcon):
    default_iconSize = 16

    def ConstructBackground(self):
        super(CircularButtonIcon, self).ConstructBackground()
        self.bg_circle = Sprite(bgParent=self, texturePath='res:/UI/Texture/Classes/cosmetics/Ship/circle_frame_32.png', opacity=0.2, color=eveThemeColor.THEME_FOCUSDARK)
        Sprite(bgParent=self, texturePath='res:/UI/Texture/circle_full.png', color=eveThemeColor.THEME_TINT, opacity=0.35, padding=4)

    def UpdateSelectedColor(self):
        super(CircularButtonIcon, self).UpdateSelectedColor()
        if self.isSelected:
            self.bg_circle.rgba = eveThemeColor.THEME_ACCENT
        else:
            self.bg_circle.rgba = eveThemeColor.THEME_FOCUSDARK
            self.bg_circle.opacity = 0.2


class CircularMenuButtonIcon(CircularButtonIcon):
    default_width = 32
    default_height = 32
    default_iconSize = 16
    expandOnLeft = True

    def GetMenuPosition(self, element):
        return (self.absoluteLeft + 2, self.absoluteBottom)
