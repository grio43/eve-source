#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\systemMenu\feature_preview\card.py
import eveui
import localization
import threadutils
from carbonui import ButtonVariant, fontconst, uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveColor
from eve.client.script.ui.control import eveLabel
from carbonui.control.button import Button
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel

class FeaturePreviewCard(Container):
    _display = False
    default_opacity = 0.0

    def __init__(self, experiment, **kwargs):
        self.experiment = experiment
        self._loading = False
        self._loaded = False
        self._content_wrap = None
        self._banner_wrap = None
        self._toggle_button = None
        self._restart_warning = None
        self._disable_message = None
        super(FeaturePreviewCard, self).__init__(**kwargs)

    def show(self):
        self.Show()
        self._load()
        duration = (1.0 - self.opacity) / 1.0 * 0.2
        eveui.fade_in(self, duration=duration)

    def hide(self):
        self.Hide()

    @threadutils.threaded
    def _load(self):
        if self._loaded or self._loading:
            return
        self._loading = True
        spinner = LoadingWheel(parent=self, align=uiconst.CENTER, opacity=0.0)
        eveui.fade_in(spinner, time_offset=0.5)
        self._content_wrap = ScrollContainer(parent=self, align=uiconst.TOALL, opacity=0.0, padding=(16, 0, 0, 0), scrollBarPadding=8)
        self._banner_wrap = Container(parent=self._content_wrap, align=uiconst.TOTOP, height=240, clipChildren=True)
        caption_cont = ContainerAutoSize(parent=self._banner_wrap, align=uiconst.TOBOTTOM, alignMode=uiconst.TOTOP, bgColor=(0.0, 0.0, 0.0, 0.75))
        self._toggle_button = Button(parent=ContainerAutoSize(parent=caption_cont, align=uiconst.TORIGHT, padding=16), align=uiconst.CENTER, label=self._get_toggle_button_label(), fixedheight=32, sidePadding=32, fontsize=fontconst.EVE_MEDIUM_FONTSIZE, variant=ButtonVariant.PRIMARY, func=self.experiment.toggle, args=())
        eveLabel.EveCaptionLarge(parent=ContainerAutoSize(parent=caption_cont, align=uiconst.TOTOP, padding=16), align=uiconst.TOTOP, text=self.experiment.title)
        Sprite(parent=self._banner_wrap, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, width=1000, height=240, texturePath=self.experiment.banner)
        eveLabel.EveLabelMedium(parent=self._content_wrap, align=uiconst.TOTOP, top=16, text=self.experiment.description)
        if self.experiment.links:
            eveLabel.EveLabelMedium(parent=ContainerAutoSize(parent=self._content_wrap, align=uiconst.TOTOP, top=16), align=uiconst.TOTOP, state=uiconst.UI_NORMAL, text='    '.join(self.experiment.links))
        prerequisites = self.experiment.check_prerequisites()
        if prerequisites:
            self._toggle_button.enabled = False
            self._show_prerequisites_info(prerequisites)
        if self.experiment.requires_restart:
            self._show_restart_warning()
        eveui.fade_out(spinner, duration=0.3, on_complete=spinner.Close)
        eveui.fade_in(self._content_wrap, duration=0.2)
        self._loading = False
        self._loaded = True
        self.experiment.on_toggle.connect(self._on_toggle)

    def _on_toggle(self):
        self._toggle_button.SetLabel(self._get_toggle_button_label())
        if self.experiment.requires_restart:
            self._show_restart_warning()
        else:
            self._hide_restart_warning()
        if not self.experiment.is_enabled and self.experiment.disable_message:
            if self._disable_message is None:
                self._disable_message = InfoBanner(parent=self._content_wrap, align=uiconst.TOTOP, title=localization.GetByLabel('UI/FeaturePreview/DisabledBannerHeader'), text=self.experiment.disable_message, index=self._banner_wrap.GetOrder() + 1)
            self._disable_message.show()
        elif self._disable_message is not None:
            self._disable_message.hide()
            self._disable_message = None

    def _get_toggle_button_label(self):
        if self.experiment.is_enabled:
            return localization.GetByLabel('UI/FeaturePreview/Disable')
        else:
            return localization.GetByLabel('UI/FeaturePreview/Enable')

    def _show_prerequisites_info(self, prerequisites):
        for prerequisite in prerequisites:
            InfoBanner(parent=self._content_wrap, align=uiconst.TOTOP, title=prerequisite.title, text=prerequisite.description, color=eveColor.SAND_YELLOW[:3], index=self._banner_wrap.GetOrder() + 1, hidden=False)

    def _show_restart_warning(self):
        if self._restart_warning is None:
            self._restart_warning = InfoBanner(parent=self._content_wrap, align=uiconst.TOTOP, title=localization.GetByLabel('UI/FeaturePreview/RestartRequiredBannerHeader'), text=localization.GetByLabel('UI/FeaturePreview/RestartRequiredBannerBody'), color=eveColor.SAND_YELLOW[:3], index=self._banner_wrap.GetOrder() + 1)
        self._restart_warning.show()

    def _hide_restart_warning(self):
        if self._restart_warning is not None:
            self._restart_warning.hide()
            self._restart_warning = None


class InfoBanner(ContainerAutoSize):

    def __init__(self, parent, align, text, title = None, hidden = True, index = None, color = None):
        if color is None:
            color = eveColor.PRIMARY_BLUE[:3]
        self._title = title
        self._text = text
        self._color = color
        super(InfoBanner, self).__init__(parent=parent, align=align, opacity=0.0 if hidden else 1.0, idx=index)
        self._layout()

    def _layout(self):
        content_wrap = ContainerAutoSize(parent=self, align=uiconst.TOTOP, padding=16)
        Fill(bgParent=self, color=self._color, opacity=0.3)
        if self._title:
            eveLabel.EveLabelLargeBold(parent=content_wrap, align=uiconst.TOTOP, text=self._title, opacity=0.8)
        eveLabel.EveLabelMedium(parent=content_wrap, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, text=self._text, opacity=0.8)

    def show(self):
        self.GetAbsolute()
        self.DisableAutoSize()
        eveui.fade_in(self, duration=0.2, time_offset=0.1)
        eveui.animate(self, 'height', start_value=0, end_value=self.height, duration=0.2, on_complete=self.EnableAutoSize)

    def hide(self):
        self.DisableAutoSize()
        eveui.fade_out(self, duration=0.2)
        eveui.animate(self, 'height', end_value=0, duration=0.2, time_offset=0.1, on_complete=self.Close)
