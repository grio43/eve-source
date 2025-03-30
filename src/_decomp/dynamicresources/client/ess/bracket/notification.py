#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\ess\bracket\notification.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.util.color import Color
from eve.client.script.ui.control import eveLabel
COLOR_WARN = '#FFF47C20'
COLOR_ALERT = '#FFEF3D3C'
COLOR_SUCCESS = '#FF56B947'
ICON_WARN = ('res:/ui/Texture/classes/ess/alertIcons/Warning_icon.png', 23, 20)
ICON_ALERT = ('res:/ui/Texture/classes/ess/alertIcons/Alert_icon.png', 30, 30)
ICON_SUCCESS = ('res:/ui/Texture/classes/ess/alertIcons/Success_icon.png', 18, 14)
_TEXT_BACKGROUND_OPACITY = 0.8

class TransitionNotification(ContainerAutoSize):

    def __init__(self, parent, align, text, iconHexColor, icon):
        super(TransitionNotification, self).__init__(parent=parent, align=align, alignMode=uiconst.TOPLEFT)
        iconColor = Color.HextoRGBA(iconHexColor)
        self.notificationText = NotificationText(self, uiconst.TOPLEFT, text, opacity=0.0, left=40, bgColor=Color.WHITE)
        self.iconCont = Container(parent=self, align=uiconst.TOLEFT, width=35, bgColor=iconColor)
        iconPath = icon[0]
        iconWidth = icon[1]
        iconHeight = icon[2]
        iconSprite = Sprite(parent=self.iconCont, texturePath=iconPath, width=iconWidth, height=iconHeight, align=uiconst.CENTER, top=-1)
        iconSprite.scalingCenter = (0.5, 0.5)

    def show(self, sleep = False):
        animations.BlinkIn(self, duration=0.1, sleep=sleep, callback=lambda : self.notificationText.show(sleep=sleep))

    def hide(self, close = False, sleep = False):
        self.iconCont.Hide()
        self.notificationText.hide(close=close, sleep=sleep)
        if close:
            self.Close()


class NotificationText(ContainerAutoSize):

    def __init__(self, parent, align, text, opacity = 1.0, **kwargs):
        super(NotificationText, self).__init__(parent=parent, align=align, opacity=opacity, **kwargs)
        self._label = eveLabel.EveHeaderLarge(parent=ContainerAutoSize(parent=self, top=8, left=16, padding=(0, 0, 16, 8)), align=uiconst.TOPLEFT, text=text, color=Color.BLACK)

    def show(self, sleep = False):
        self._label.GetAbsolute()
        self.DisableAutoSize()
        animations.FadeIn(self, duration=0.2, endVal=_TEXT_BACKGROUND_OPACITY, sleep=sleep)

    def hide(self, close = False, sleep = False):
        callback = None if not close else self.Close
        animations.FadeOut(self, duration=0.3, callback=callback, sleep=sleep)
