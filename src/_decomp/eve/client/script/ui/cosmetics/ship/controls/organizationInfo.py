#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\controls\organizationInfo.py
import evelink.client
from carbonui import Align, TextColor, TextDetail, TextHeader, uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveIcon import GetLogoIcon
from localization import GetByLabel

class OrganizationInfo(Container):
    default_display = False
    default_width = 300
    default_height = 64

    def __init__(self, organization_id, *args, **kwargs):
        super(OrganizationInfo, self).__init__(*args, **kwargs)
        self._organization_id = organization_id
        self._compact_mode = False
        self.icon = None
        self.construct_layout()

    def construct_layout(self):
        self.icon_container = Container(name='icon_container', parent=self, align=Align.TOLEFT, pos=(0, 0, 64, 64))
        self.icon = GetLogoIcon(name='icon', parent=self.icon_container, align=Align.TOALL, state=uiconst.UI_NORMAL, itemID=self.organization_id)
        self.icon.OnClick = self.on_icon_click
        self.text_container = ContainerAutoSize(name='text_container', parent=self, align=Align.CENTERLEFT, width=228, left=72, padTop=16)
        self.description_label = TextDetail(name='description_label', parent=self.text_container, align=Align.TOTOP, text=self.description_text, color=TextColor.SECONDARY, top=-16)
        self.name_label = TextHeader(name='name_label', parent=self.text_container, align=Align.TOTOP, state=uiconst.UI_NORMAL, text=evelink.client.owner_link(self.organization_id), maxLines=3, autoFadeSides=16, bold=True)

    def on_icon_click(self, *args):
        sm.GetService('info').ShowInfo(typeID=cfg.eveowners.Get(self.organization_id).typeID, itemID=self.organization_id)

    def update_compact_mode(self):
        self.text_container.display = not self.compact_mode
        self.width = 64 if self.compact_mode else self.default_width
        if self.compact_mode:
            self.icon.SetHint(u'%s\n%s' % (self.description_text, cfg.eveowners.Get(self.organization_id).name))
        else:
            self.icon.SetHint(None)

    @property
    def description_text(self):
        return GetByLabel('UI/Personalization/ShipSkins/SKINR/TargetedAt')

    @property
    def organization_id(self):
        return self._organization_id

    @property
    def compact_mode(self):
        return self._compact_mode

    @compact_mode.setter
    def compact_mode(self, value):
        if self._compact_mode == value:
            return
        self._compact_mode = value
        self.update_compact_mode()
