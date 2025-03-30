#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\info_panel_progress_bar.py
import eveui
from eve.client.script.ui import eveColor
from eve.client.script.ui.shared.infoPanels.const.infoPanelTextureConst import PROGRESS_FILL_TEXTURE_PATH

class InfoPanelProgressBar(eveui.Container):
    default_name = 'InfoPanelProgressBar'
    default_state = eveui.State.normal
    default_align = eveui.Align.to_top
    default_height = 28
    default_clipChildren = True

    def __init__(self, progress = None, **kwargs):
        super(InfoPanelProgressBar, self).__init__(**kwargs)
        self._layout()
        if progress is not None:
            self.set_progress(progress, snap_to_value=True)

    def set_progress(self, progress, snap_to_value = False, on_complete = None):
        if not progress:
            self.progress_fill.state = eveui.State.hidden
            return
        self.progress_fill.state = eveui.State.disabled
        if snap_to_value:
            self.progress_fill.width = progress
            if on_complete:
                on_complete()
        else:
            eveui.animate(self.progress_fill, 'width', end_value=progress, duration=1, on_complete=on_complete)

    def OnMouseEnter(self, *args):
        eveui.fade(self._progress_bg_container, end_value=0.7, duration=0.1)

    def OnMouseExit(self, *args):
        eveui.fade(self._progress_bg_container, end_value=0.35, duration=0.2)

    def _layout(self):
        self.content_container = eveui.Container(parent=self, align=eveui.Align.to_all, padding=(6, 6, 12, 6), clipChildren=True)
        self._progress_fill_parent = fill_container = eveui.Container(name='fillContainer', parent=self, align=eveui.Align.to_all, clipChildren=True)
        self.progress_fill = eveui.StretchSpriteHorizontal(parent=fill_container, state=eveui.State.hidden, align=eveui.Align.to_left_prop, texturePath=PROGRESS_FILL_TEXTURE_PATH, color=eveColor.CRYO_BLUE, leftEdgeSize=2, rightEdgeSize=10, padLeft=-2, padRight=-10, width=0, opacity=0.5)
        self._progress_bg_container = eveui.Fill(parent=self, state=eveui.State.disabled, align=eveui.Align.to_all, color=(0, 0, 0), opacity=0.35)
