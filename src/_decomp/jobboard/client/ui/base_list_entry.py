#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\ui\base_list_entry.py
import math
import carbonui
import eveui
from carbonui import Align, uiconst, PickState
from carbonui.primitives.container import Container
from eve.client.script.ui import eveThemeColor, eveColor
from jobboard.client.ui.solar_system_chip import SolarSystemChip
from jobboard.client.ui.util import get_career_path_bg, get_career_path_by_career
GLOW_IDLE = 0.5
GLOW_HOVER = 1.0
GLOW_MOUSE_DOWN = 2.0
OPACITY_IDLE = 0.1
OPACITY_HOVER = 0.2
OPACITY_MOUSEDOWN = 0.4
FLAIR_SIZE = 300

class ListEntry(Container):
    default_state = eveui.State.disabled
    default_align = eveui.Align.to_top
    default_padTop = 4
    default_padBottom = 4
    default_height = 46
    default_width = 300
    default_clipChildren = True
    isDragObject = True
    LEFT_LINE_COLOR = eveColor.PLATINUM_GREY
    HOVER_FRAME_COLOR = eveColor.PLATINUM_GREY
    BG_FRAME_COLOR = eveColor.SILVER_GREY

    def __init__(self, *args, **kwargs):
        super(ListEntry, self).__init__(*args, **kwargs)
        self._layout()

    def _layout(self):
        self._construct_base_layout()
        self._construct_left_layout()
        self._construct_left_side()
        self._construct_underlay()

    def _construct_base_layout(self):
        self._left_line = eveui.Line(name='leftLine', parent=self, align=Align.TOLEFT, color=self.LEFT_LINE_COLOR, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, opacity=0.6, glowBrightness=0.5)
        self._left_line.rgb = self.left_line_rgb
        self.content = Container(name='content', parent=self)
        self.flair_cont = Container(name='flairCont', parent=self, pickState=PickState.OFF, clipChildren=True)

    def _construct_left_layout(self):
        self.left_container = eveui.Container(name='left_container', parent=self.content, align=Align.TOALL, padLeft=16, padRight=16, clipChildren=True)

    def _construct_left_side(self):
        pass

    def _construct_left_content(self, parent):
        pass

    def _construct_underlay(self):
        eveui.Frame(bgParent=self, texturePath='res:/UI/Texture/classes/Opportunities/card_mask.png', cornerSize=16, color=(0, 0, 0, 0.9))
        self._bg_flair = eveui.Sprite(name='bgFlair', parent=self.flair_cont, texturePath=self._get_flair_texture(), color=self.BG_FRAME_COLOR, align=Align.TOPLEFT, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.0, opacity=0.7, pos=self._get_flair_pos())
        self._bg_flair.rgb = self.bg_flair_rgb
        self._hover_frame = eveui.Frame(parent=self, texturePath='res:/UI/Texture/classes/Opportunities/card_mask.png', cornerSize=16, color=self.HOVER_FRAME_COLOR, opacity=OPACITY_IDLE)
        self._hover_frame.rgb = self.hover_frame_rgb

    def _get_flair_texture(self):
        return 'res:/UI/Texture/Shared/CareerPaths/unclassified_flair.png'

    def _get_flair_pos(self):
        return (-FLAIR_SIZE / 2 + 25,
         -FLAIR_SIZE / 2 + 25,
         FLAIR_SIZE,
         FLAIR_SIZE)

    @property
    def left_line_rgb(self):
        return self.LEFT_LINE_COLOR[:3]

    @property
    def hover_frame_rgb(self):
        return self.HOVER_FRAME_COLOR[:3]

    @property
    def bg_flair_rgb(self):
        return self.BG_FRAME_COLOR[:3]


class BaseJobListEntry(ListEntry):
    default_state = eveui.State.normal
    LEFT_LINE_COLOR = eveThemeColor.THEME_FOCUS
    HOVER_FRAME_COLOR = eveThemeColor.THEME_FOCUS
    BG_FRAME_COLOR = eveThemeColor.THEME_FOCUSDARK

    def __init__(self, controller, show_feature = False, show_solar_system = True, *args, **kwargs):
        kwargs['name'] = u'entry_{}'.format(controller.job_id)
        self.job = controller
        self._show_feature = show_feature
        self._show_solar_system = show_solar_system
        self._solar_system_chip = None
        super(BaseJobListEntry, self).__init__(*args, **kwargs)
        self._update_state()
        self._register()

    def Close(self):
        self._unregister()
        super(BaseJobListEntry, self).Close()

    def _register(self):
        self.job.on_job_updated.connect(self._on_job_updated)

    def _unregister(self):
        self.job.on_job_updated.disconnect(self._on_job_updated)

    def _on_job_updated(self):
        self.Flush()
        self._layout()
        self._update_state()

    def _update_state(self):
        self._update_left_line_color()

    def _update_left_line_color(self):
        state_info = self.job.get_state_info()
        if not state_info:
            self._left_line.rgb = self.left_line_rgb
            return
        self._left_line.rgb = state_info['color'][:3]

    @property
    def left_line_rgb(self):
        return eveThemeColor.THEME_FOCUS[:3]

    @property
    def hover_frame_rgb(self):
        return eveThemeColor.THEME_FOCUS[:3]

    @property
    def bg_flair_rgb(self):
        return eveThemeColor.THEME_FOCUSDARK[:3]

    def _layout(self):
        self._construct_base_layout()
        self._construct_right_wrapper(parent=self.content)
        self._construct_left_layout()
        self._construct_left_side()
        self._construct_right_layout()
        self._construct_right_side()
        self._construct_underlay()

    def _construct_right_wrapper(self, parent):
        self._right_wrapper = eveui.Container(name='right_wrapper', parent=parent, align=Align.TORIGHT_PROP, width=self.get_right_wrapper_ratio())

    def get_right_wrapper_ratio(self):
        return 0.36

    def _construct_right_layout(self):
        self.right_container = eveui.Container(name='right_container', parent=self._right_wrapper, align=Align.TOALL, padLeft=16, padRight=16)

    def _construct_right_side(self):
        pass

    def _construct_underlay(self):
        super(BaseJobListEntry, self)._construct_underlay()
        self._right_frame = eveui.Frame(bgParent=self._right_wrapper, texturePath='res:/UI/Texture/classes/Opportunities/list_entry_mask.png', cornerSize=16, color=eveColor.WHITE, opacity=0.05)

    def _construct_title_icons(self, container):
        if not self._show_feature:
            return
        content_tag = self.job.feature_tag
        container = eveui.Container(name='title_icons_container', parent=container, align=Align.TOLEFT, padRight=8, width=16, height=16, pickState=PickState.ON, hint=content_tag.title)
        eveui.Sprite(parent=container, texturePath=content_tag.icon, align=Align.CENTER, width=16, height=16, color=carbonui.TextColor.SECONDARY, pickState=PickState.OFF)
        container.OnClick = self.OnClick

    def _construct_solar_system_chip(self):
        if not self._show_solar_system:
            return
        solar_system_id = self.job.solar_system_id
        if solar_system_id:
            container = eveui.ContainerAutoSize(name='solar_system_chip_container', parent=self.left_container, align=Align.TORIGHT)
            self._solar_system_chip = SolarSystemChip(parent=container, state=eveui.State.disabled, align=Align.CENTERRIGHT, solar_system_id=solar_system_id, compact=True, align_content=Align.TOLEFT)

    def _get_flair_texture(self):
        return get_career_path_bg(self.job.career_id)

    def OnClick(self, *args):
        eveui.Sound.button_click.play()
        self.job.on_click()

    def OnMouseEnter(self, *args):
        eveui.Sound.entry_hover.play()
        eveui.fade_in(self._hover_frame, end_value=OPACITY_HOVER, duration=0.2)
        eveui.animate(self._left_line, 'glowBrightness', GLOW_HOVER, duration=0.2)
        eveui.animate(self._bg_flair, 'glowBrightness', 0.3, duration=0.2)
        eveui.animate(self._bg_flair, 'rotation', end_value=self._bg_flair.rotation + 2 * math.pi, duration=80.0, curve_type=eveui.CurveType.linear)

    def OnMouseExit(self, *args):
        eveui.fade(self._hover_frame, end_value=OPACITY_IDLE, duration=0.2)
        eveui.animate(self._left_line, 'glowBrightness', GLOW_IDLE, duration=0.2)
        eveui.animate(self._bg_flair, 'glowBrightness', 0.0, duration=0.2)
        eveui.animate(self._bg_flair, 'rotation', end_value=self._bg_flair.rotation + 0.025, duration=0.2)

    def OnMouseDown(self, *args):
        eveui.fade(self._hover_frame, end_value=OPACITY_MOUSEDOWN, duration=0.2)
        eveui.animate(self._left_line, 'glowBrightness', GLOW_MOUSE_DOWN, duration=0.2)

    def OnMouseUp(self, *args):
        eveui.fade(self._hover_frame, end_value=OPACITY_IDLE, duration=0.2)
        eveui.animate(self._left_line, 'glowBrightness', GLOW_IDLE, duration=0.2)

    def OnColorThemeChanged(self):
        super(ListEntry, self).OnColorThemeChanged()
        self._left_line.rgb = self.left_line_rgb
        self._hover_frame.rgb = self.hover_frame_rgb
        self._bg_flair.rgb = self.bg_flair_rgb

    def GetDragData(self):
        return self.job.get_drag_data()

    def GetMenu(self):
        return self.job.get_menu()


class ListEntryWithText(ListEntry):

    def __init__(self, icon, text = '', career_id = None, *args, **kwargs):
        self._icon = icon
        self._text = text
        self._career_id = career_id
        super(ListEntryWithText, self).__init__(*args, **kwargs)

    def _construct_left_side(self):
        self._construct_icon()
        self._construct_text()

    def _construct_icon(self):
        icon_container = eveui.Container(parent=self.left_container, align=Align.TOLEFT, padRight=8, width=16, height=16)
        eveui.Sprite(parent=icon_container, texturePath=self._icon, align=Align.CENTER, width=16, height=16, color=carbonui.TextColor.SECONDARY, pickState=PickState.OFF)

    def _construct_text(self):
        text_container = eveui.Container(name='text_container', parent=self.left_container, align=Align.TOALL, clipChildren=True)
        self._text_label = carbonui.TextBody(parent=text_container, align=Align.CENTERLEFT, maxLines=1, text=self._text, bold=True, autoFadeSides=16)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self._text_label.text = value

    def _get_flair_texture(self):
        return get_career_path_by_career(self._career_id)
