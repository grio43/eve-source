#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\seasons\home_page_section.py
import eveui
import trinity
import carbonui
import localization
from carbonui import Align, PickState
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from eve.client.script.ui import eveColor
from jobboard.client import get_provider, ProviderType, job_board_signals
from seasons.client.util import OpenSeasonsWindow

class SeasonHomePageSection(Container):
    default_align = Align.TOTOP
    default_height = 242
    default_clipChildren = True
    default_display = False
    default_pickState = False

    def __init__(self, *args, **kwargs):
        super(SeasonHomePageSection, self).__init__(*args, **kwargs)
        self._provider = get_provider(ProviderType.SEASONS)
        self._refresh()
        self._register()

    def Close(self):
        super(SeasonHomePageSection, self).Close()
        self._unregister()

    def _register(self):
        job_board_signals.on_job_provider_state_changed.connect(self._on_job_provider_state_changed)

    def _unregister(self):
        job_board_signals.on_job_provider_state_changed.disconnect(self._on_job_provider_state_changed)

    def _on_job_provider_state_changed(self, provider):
        if self._provider.PROVIDER_ID == provider.PROVIDER_ID:
            self._refresh()

    def _refresh(self):
        self.Flush()
        if self._provider.is_hidden:
            self.display = False
        else:
            SeasonAdvert(parent=self, align=Align.TOLEFT, header=localization.GetByMessageID(872379), subheader=self._provider.feature_tag.description)
            self.display = True


class SeasonAdvert(Container):
    default_state = carbonui.uiconst.UI_NORMAL
    default_width = 700
    default_height = 242

    def __init__(self, header, subheader, *args, **kwargs):
        super(SeasonAdvert, self).__init__(*args, **kwargs)
        self._consruct_text(header, subheader)
        self._construct_underlay()

    def _consruct_text(self, header, subheader):
        text_container = ContainerAutoSize(parent=self, align=Align.TOBOTTOM_NOPUSH, padding=(20, 20, 40, 20))
        carbonui.TextHeadline(parent=text_container, align=Align.TOTOP, maxLines=1, text=header, bold=True, color=carbonui.TextColor.HIGHLIGHT)
        if subheader:
            carbonui.TextBody(parent=text_container, align=Align.TOTOP, maxLines=2, text=subheader)

    def _construct_underlay(self):
        self._hover_frame = Frame(name='hover_frame', parent=self, texturePath='res:/UI/Texture/classes/Opportunities/advert_mask.png', cornerSize=16, color=eveColor.BLACK, opacity=0.25, pickState=PickState.OFF)
        self._bg_sprite = eveui.Sprite(name='bg_image', parent=self, align=Align.TOALL, texturePath='res:/UI/Texture/classes/Opportunities/advert_winter_nexus.png', textureSecondaryPath='res:/UI/Texture/classes/Opportunities/advert_mask.png', spriteEffect=trinity.TR2_SFX_MODULATE, pickState=PickState.OFF)

    def OnMouseEnter(self, *args):
        eveui.Sound.entry_hover.play()
        eveui.fade_in(self._hover_frame, end_value=0.05, duration=0.2)

    def OnMouseExit(self, *args):
        eveui.fade(self._hover_frame, end_value=0.25, duration=0.2)

    def OnClick(self, *args):
        OpenSeasonsWindow()
