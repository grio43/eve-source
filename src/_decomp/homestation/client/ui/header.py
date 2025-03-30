#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\homestation\client\ui\header.py
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control import eveLabel, infoIcon
from homestation.client.ui.const import Padding

class Header(ContainerAutoSize):

    def __init__(self, text, hint = None, **kwargs):
        super(Header, self).__init__(**kwargs)
        header = eveLabel.EveLabelLargeBold(parent=self, align=uiconst.TOPLEFT, text=text)
        if hint:
            icon = infoIcon.MoreInfoIcon(parent=self, align=uiconst.TOPLEFT, hint=hint)

            def update_info_icon_position():
                icon.left = header.width + Padding.normal
                icon.top = (header.height - icon.height) / 2

            header.OnSizeChanged = update_info_icon_position
