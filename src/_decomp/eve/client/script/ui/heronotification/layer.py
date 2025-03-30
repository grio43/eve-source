#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\heronotification\layer.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.uicore import uicore

class HeroNotificationLayer(Container):

    def __init__(self, opacity = 1.0):
        super(HeroNotificationLayer, self).__init__(parent=uicore.layer.mloading, align=uiconst.TOALL, opacity=opacity)

    def create_hero_notification_container(self):
        return Container(parent=self, align=uiconst.TOALL)

    def cleanup(self):
        self.Flush()
