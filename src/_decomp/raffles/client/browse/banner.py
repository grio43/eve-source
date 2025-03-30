#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\browse\banner.py
from eve.client.script.ui.control.eveIcon import LogoIcon
import eveui
from raffles.client.localization import Text
from raffles.client.widget.vertical_center_container import VerticalCenteredContainer
from raffles.common.const import PKN_CORP_ID

class Banner(eveui.Container):
    default_name = 'Banner'
    default_align = eveui.Align.to_top
    default_height = 100
    default_padLeft = 38
    default_padRight = 38

    def __init__(self, **kwargs):
        super(Banner, self).__init__(**kwargs)
        self._layout()

    def _layout(self):
        text_cont = VerticalCenteredContainer(name='text_cont', parent=self, align=eveui.Align.to_left_prop, width=0.6)
        eveui.EveCaptionMedium(name='title', parent=text_cont, align=eveui.Align.to_top, text=Text.browse_banner_title())
        eveui.EveLabelLarge(name='subtitle', parent=text_cont, align=eveui.Align.to_top, top=4, text=Text.browse_banner_description())
        logo_cont = eveui.Container(name='logo_cont', parent=self, align=eveui.Align.to_all)
        LogoIcon(parent=logo_cont, align=eveui.Align.center_top, state=eveui.State.disabled, size=128, top=-32, itemID=PKN_CORP_ID)
        eveui.EveLabelLarge(parent=logo_cont, align=eveui.Align.center_top, top=68, text=Text.tagline())
