#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\ui\pages\details_page.py
import math
import carbonui
import eveicon
import eveui
import localization
import threadutils
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.util.various_unsorted import GetWindowAbove
from eve.client.script.ui import eveColor, eveThemeColor
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.control.infoIcon import InfoGlyphIcon
from jobboard.client import get_job_board_service, job_board_signals, get_primary_feature_tags
from jobboard.client.ui.card_section import RelatedJobCardSection
from jobboard.client.ui.chip import ContentTagChip
from jobboard.client.ui.solar_system_chip import SolarSystemChip
from jobboard.client.ui.tag_icon import TagIcon
from jobboard.client.ui.track_button import TrackJobButton
from jobboard.client.ui.util import get_career_path_bg
from jobboard.client.util import sort_content_tags

class DetailsPage(eveui.Container):
    default_align = eveui.Align.to_all

    def __init__(self, job_id, **kwargs):
        super(DetailsPage, self).__init__(**kwargs)
        self._job_id = job_id
        self._construct_content()

    def Close(self):
        super(DetailsPage, self).Close()
        self._unregister()

    def _register(self):
        job_board_signals.on_job_added.connect(self._on_job_added)

    def _unregister(self):
        job_board_signals.on_job_added.disconnect(self._on_job_added)

    @threadutils.threaded
    def _construct_content(self):
        loading_wheel = LoadingWheel(parent=self, align=eveui.Align.center, width=64, height=64, opacity=0)
        eveui.fade(loading_wheel, 0, 1, duration=2, time_offset=0)
        job = get_job_board_service().get_job(self._job_id)
        if job:
            self._construct_job(job)
        else:
            self._construct_no_job()
        loading_wheel.Close()
        self._register()

    def _on_job_added(self, job):
        if job.job_id == self._job_id:
            self.Flush()
            self._construct_job(job)

    @threadutils.threaded
    def _construct_job(self, job):
        job.construct_page(parent=self, name=u'page_{}'.format(job.job_id))

    def _construct_no_job(self):
        label = carbonui.TextHeader(parent=self, align=eveui.Align.center, text=localization.GetByLabel('UI/Opportunities/NotFound'), opacity=0)
        eveui.fade_in(label, time_offset=1)


class JobPage(eveui.Container):
    default_align = eveui.Align.to_all
    __notifyevents__ = ['OnSessionChanged']

    def __init__(self, job, show_related = True, **kwargs):
        super(JobPage, self).__init__(**kwargs)
        self.job = job
        self._show_related = show_related
        self.job.opened()
        self._header_wrapper = None
        self._header_container = None
        self._bg_flair = None
        self._related_gradient = None
        self._solar_system_chip = None
        self._is_dirty = False
        self._layout()
        self._update_state()
        self._register()

    def Close(self):
        super(JobPage, self).Close()
        self._unregister()

    def _register(self):
        sm.RegisterNotify(self)
        self.job.on_job_updated.connect(self._on_job_updated)
        job_board_signals.on_job_state_changed.connect(self._on_job_state_changed)
        job_board_signals.on_job_window_maximized.connect(self._on_window_maximized)

    def _unregister(self):
        sm.UnregisterNotify(self)
        if self.job:
            self.job.on_job_updated.disconnect(self._on_job_updated)
        job_board_signals.on_job_state_changed.disconnect(self._on_job_state_changed)
        job_board_signals.on_job_window_maximized.disconnect(self._on_window_maximized)

    def OnSessionChanged(self, is_remote, session, change):
        if 'solarsystemid2' in change:
            if self.IsVisible():
                self._reconstruct()
            else:
                self._is_dirty = True

    def _on_window_maximized(self):
        self._try_update()

    def _on_job_updated(self):
        self._is_dirty = True
        self._try_update()

    def _on_job_state_changed(self, job):
        if job == self.job:
            self._update_state()

    def _try_update(self):
        if not self._is_dirty:
            return
        if self.IsVisible():
            self._is_dirty = False
            self._update()

    def _update(self):
        self._reconstruct()

    def _reconstruct(self):
        self.Flush()
        self._layout()
        self._update_state()

    def _update_state(self):
        state_info = self.job.get_state_info()
        if not state_info:
            self._state_container.display = False
            return
        color = list(state_info['color'])
        color[3] = carbonui.TextColor.HIGHLIGHT.opacity
        bg_color = list(color)
        bg_color[3] = 0.2
        self._state_icon.texturePath = state_info['icon']
        self._state_icon.color = color
        self._state_text.text = state_info['text']
        self._state_text.color = color
        self._state_left_line.color = color
        self._state_container.bgFill.color = bg_color
        self._state_container.display = True

    @property
    def _window_content_padding(self):
        window_above = GetWindowAbove(self)
        if window_above:
            return window_above.content_padding[0]
        return 16

    def _layout(self):
        self._construct_state_container()
        self._construct_header_container()
        self._construct_header(self._header_container)
        self._content_container = eveui.ScrollContainer(name='content_container', parent=self, align=eveui.Align.to_all)
        self._body_container = eveui.ContainerAutoSize(name='body_container', parent=self._content_container, align=eveui.Align.to_top, alignMode=eveui.Align.to_top)
        self._construct_body(self._body_container)
        if self._show_related:
            self._related_container = eveui.ContainerAutoSize(name='related_container', parent=self._content_container, align=eveui.Align.to_top, alignMode=eveui.Align.to_top, padTop=24)
            self._construct_related_content(self._related_container)

    def _construct_header_container(self):
        self._header_wrapper = eveui.ContainerAutoSize(name='header_wrapper', parent=self, align=eveui.Align.to_top, bgColor=self._header_bg_color, padding=(-self._window_content_padding,
         0,
         -self._window_content_padding,
         12), clipChildren=True)
        self._header_container = eveui.ContainerAutoSize(name='header_container', parent=self._header_wrapper, state=eveui.State.normal, align=eveui.Align.to_top, alignMode=eveui.Align.to_top, bgColor=self._header_overlay_color)
        self._header_container.OnMouseEnter = self._header_mouse_enter
        self._header_container.OnMouseExit = self._header_mouse_exit
        self._header_container.GetMenu = self.job.get_menu

    def _set_header_color(self):
        self._header_wrapper.bgColor = self._header_bg_color

    @property
    def _header_bg_color(self):
        bg_color = list(eveThemeColor.THEME_FOCUSDARK)
        bg_color[3] = 0.1
        return bg_color

    @property
    def _header_overlay_color(self):
        return (0, 0, 0, 0)

    def _construct_state_container(self):
        self._state_container = eveui.ContainerAutoSize(name='state_container', parent=self, display=False, align=eveui.Align.to_top, alignMode=eveui.Align.center_left, padding=(-self._window_content_padding,
         0,
         -self._window_content_padding,
         0), clipChildren=True, bgColor=(0, 0, 0, 0))
        self._state_icon = eveui.Sprite(name='icon', parent=self._state_container, align=eveui.Align.center_left, width=16, height=16, left=16, outputMode=carbonui.uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.3)
        self._state_text = carbonui.TextBody(parent=self._state_container, align=eveui.Align.center_left, left=40, padding=8)
        self._state_left_line = eveui.Line(name='state_left_line', parent=self._state_container, align=eveui.Align.to_left, outputMode=carbonui.uiconst.OUTPUT_COLOR_AND_GLOW, opacity=0.5, glowBrightness=0.5)

    def _construct_header(self, parent_container):
        content_container = eveui.ContainerAutoSize(name='content_container', parent=parent_container, align=eveui.Align.to_top, alignMode=eveui.Align.to_top, padding=16)
        top_container = self._construct_top_container(parent=content_container)
        self._construct_career_tag(parent=top_container)
        self._construct_bg_flair(parent=parent_container)
        self._construct_top_buttons(parent=top_container)
        solar_system_id = self.job.solar_system_id
        if solar_system_id:
            container = eveui.Container(parent=content_container, align=eveui.Align.to_top, height=20, padTop=8)
            self._solar_system_chip = SolarSystemChip(parent=container, align=eveui.Align.to_left, solar_system_id=solar_system_id)
        self._construct_subtitle(content_container)
        self._construct_header_caption(content_container)
        bottom_container = eveui.ContainerAutoSize(parent=content_container, align=eveui.Align.to_top)
        content_tags_container = eveui.FlowContainer(parent=bottom_container, align=eveui.Align.to_top, contentSpacing=(8, 8))
        important_tags = []
        if self.job.feature_tag:
            important_tags.append(self.job.feature_tag.id)
        if self.job.career_tag:
            important_tags.append(self.job.career_tag.id)
        sorted_content_tags = sort_content_tags(self.job.content_tags.values(), important_tags=important_tags)
        primary_feature_tags = get_primary_feature_tags()
        for content_tag in sorted_content_tags:
            ContentTagChip(parent=content_tags_container, on_click=self._content_tag_clicked, content_tag=content_tag, show_icon=content_tag.id in primary_feature_tags)

        self._cta_buttons_container = eveui.ContainerAutoSize(parent=bottom_container, align=eveui.Align.to_top)
        self._construct_cta_buttons()

    def _construct_top_container(self, parent):
        top_container = eveui.Container(name='top_container', parent=parent, align=eveui.Align.to_top, height=20)
        return top_container

    def _construct_career_tag(self, parent):
        TagIcon(name='career_tag_icon', parent=parent, align=eveui.Align.center_left, texturePath=self.job.career_icon, hint=self.job.career_title)
        carbonui.TextBody(name='career_tag_label', parent=parent, align=eveui.Align.center_left, text=self.job.career_title, color=carbonui.TextColor.SECONDARY, left=28)

    def _construct_bg_flair(self, parent):
        self._bg_flair = eveui.Sprite(name='bg_flair', parent=parent, align=eveui.Align.top_left, width=500, height=500, left=-225, top=-224, texturePath=get_career_path_bg(self.job.career_id), color=eveThemeColor.THEME_FOCUSDARK, outputMode=carbonui.uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.0, opacity=0.7)

    def _construct_top_buttons(self, parent):
        self._top_buttons_container = eveui.ContainerAutoSize(name='top_buttons_container', parent=parent, align=eveui.Align.to_right)
        for button_info in self.job.get_buttons():
            ButtonIcon(parent=self._top_buttons_container, align=eveui.Align.to_right, width=20, height=20, iconSize=16, padLeft=4, color=carbonui.TextColor.SECONDARY, texturePath=button_info['icon'], func=button_info.get('on_click', None), hint=button_info.get('hint', ''))

        if self.job.is_linkable:
            link_button = ButtonIcon(name='link_button', parent=self._top_buttons_container, align=eveui.Align.to_right, width=20, height=20, iconSize=16, padLeft=4, color=carbonui.TextColor.SECONDARY, texturePath=eveicon.link, hint=localization.GetByLabel('UI/Opportunities/LinkButtonHint'))
            link_button.isDragObject = True
            link_button.GetDragData = self.job.get_drag_data

    def _construct_header_caption(self, parent):
        eveui.EveCaptionMedium(parent=parent, align=eveui.Align.to_top, text=self.job.title, padTop=16, padBottom=16)

    def _construct_cta_buttons(self):
        cta_buttons = self.job.get_cta_buttons() or []
        is_trackable = self.job.is_trackable or self.job.is_tracked
        if cta_buttons or is_trackable:
            self._cta_buttons = ButtonGroup(parent=self._cta_buttons_container, align=eveui.Align.to_top, button_alignment=carbonui.AxisAlignment.START, button_size_mode=ButtonSizeMode.STRETCH, padTop=16)
            TrackJobButton(parent=self._cta_buttons, job=self.job)
            for button_info in cta_buttons:
                if isinstance(button_info, dict):
                    button = eveui.Button(parent=self._cta_buttons, name=button_info.get('name', None), texturePath=button_info.get('icon', None), func=button_info['on_click'], label=button_info.get('label', ''), hint=button_info.get('hint', ''))
                    get_menu = button_info.get('get_menu', None)
                    if get_menu:
                        button.GetMenu = get_menu
                else:
                    button_info.align = eveui.Align.top_left
                    button_info.SetParent(self._cta_buttons)

            num_buttons = len(cta_buttons)
            if is_trackable:
                num_buttons += 1
            self._cta_buttons.maxWidth = min(num_buttons * 400, carbonui.IdealSize.SIZE_960)

    def _construct_body(self, parent_container):
        pass

    def _construct_subtitle(self, parent_container):
        pass

    def _construct_related_content(self, parent_container):
        eveui.GradientSprite(parent=parent_container, state=eveui.State.disabled, align=eveui.Align.to_top, height=1, rgbData=((0, eveColor.WHITE[:3]), (1.0, eveColor.WHITE[:3])), alphaData=((0.0, 0.0),
         (0.05, 0.2),
         (0.95, 0.2),
         (1.0, 0.0)), padBottom=24)
        self._related_gradient = eveui.GradientSprite(bgParent=parent_container, state=eveui.State.disabled, rgbData=((0, eveThemeColor.THEME_FOCUSDARK[:3]), (1.0, eveThemeColor.THEME_FOCUSDARK[:3])), alphaData=((0.0, 0.0),
         (0.05, 0.1),
         (0.95, 0.1),
         (1.0, 0.0)))
        RelatedJobCardSection(job=self.job, parent=parent_container, padBottom=24, title=localization.GetByLabel('UI/Opportunities/RelatedOpportunities'), show_feature_name=True, hide_empty=False)

    def _content_tag_clicked(self, value):
        get_job_board_service().open_browse_page(value)

    def OnColorThemeChanged(self):
        super(JobPage, self).OnColorThemeChanged()
        color = eveThemeColor.THEME_FOCUSDARK[:3]
        self._set_header_color()
        if self._bg_flair:
            self._bg_flair.rgb = color
        if self._show_related:
            (self._related_gradient.SetGradient(colorData=((0, color), (1.0, color))),)

    def _header_mouse_enter(self, *args):
        eveui.animate(self._bg_flair, 'glowBrightness', 0.3, duration=0.2)
        eveui.animate(self._bg_flair, 'rotation', end_value=self._bg_flair.rotation + 2 * math.pi, duration=80.0, curve_type=eveui.CurveType.linear)

    def _header_mouse_exit(self, *args):
        eveui.animate(self._bg_flair, 'glowBrightness', 0.0, duration=0.2)
        eveui.animate(self._bg_flair, 'rotation', end_value=self._bg_flair.rotation + 0.025, duration=0.2)


class DetailsSection(eveui.ContainerAutoSize):
    default_align = eveui.Align.to_top
    default_alignMode = eveui.Align.to_top
    default_padTop = 12
    default_padBottom = 12

    def __init__(self, title, hint = None, max_content_height = None, *args, **kwargs):
        super(DetailsSection, self).__init__(*args, **kwargs)
        self._max_content_height = max_content_height
        self._current_max_height = None
        self._collapsed = False
        self._header_cont = eveui.ContainerAutoSize(name='headerCont', parent=self, align=eveui.Align.to_top, padBottom=8)
        header = carbonui.TextHeader(parent=self._header_cont, align=eveui.Align.top_left, text=title, color=carbonui.TextColor.SECONDARY)
        if hint:
            self.info_icon = InfoGlyphIcon(parent=self._header_cont, align=eveui.Align.top_left, hint=hint, state=eveui.State.normal, pos=(header.width + 8,
             3,
             16,
             16))
        self.content_container = eveui.ContainerAutoSize(parent=self, align=eveui.Align.to_top, alignMode=eveui.Align.to_top, maxHeight=self._max_content_height, clipChildren=True)
        self._construct_body(self.content_container)
        if max_content_height:
            self._collapsed = True
            self._construct_expand()
            self.content_container._OnResize = self._on_content_resize
            self._update_collapse_display(animate=False)

    def _construct_body(self, parent_container):
        pass

    def _construct_expand(self):
        self._expand_container = eveui.Container(name='expand_container', state=eveui.State.normal, parent=self, align=eveui.Align.to_top, height=20, padTop=4)
        self._expand_container.OnClick = self._toggle_expand
        self._expand_container.OnMouseEnter = self._on_mouse_enter
        self._expand_container.OnMouseExit = self._on_mouse_exit
        self._caret_icon = eveui.Sprite(parent=self._expand_container, state=eveui.State.disabled, align=eveui.Align.center, opacity=carbonui.TextColor.NORMAL.opacity, height=16, width=16, texturePath=eveicon.chevron_down_double)
        left_cont = eveui.Container(parent=self._expand_container, align=eveui.Align.to_left_prop, width=0.5, padRight=16)
        eveui.Line(parent=left_cont, align=eveui.Align.to_top, weight=1, top=9)
        left_cont = eveui.Container(parent=self._expand_container, align=eveui.Align.to_all, padLeft=16)
        eveui.Line(parent=left_cont, align=eveui.Align.to_top, weight=1, top=9)

    def _on_mouse_enter(self, *args, **kwargs):
        eveui.fade(self._expand_container, end_value=1.5, duration=0.2)

    def _on_mouse_exit(self, *args, **kwargs):
        eveui.fade(self._expand_container, end_value=1, duration=0.2)

    def _toggle_expand(self, *args, **kwargs):
        self._collapsed = not self._collapsed
        if self._collapsed:
            self._caret_icon.texturePath = eveicon.chevron_down_double
        else:
            self._caret_icon.texturePath = eveicon.chevron_up_double
        self._update_collapse_display()

    def _on_content_resize(self, *args):
        self._update_collapse_display()

    def _update_collapse_display(self, animate = True):
        new_max_height = None
        exceeds_max_height = self.content_container.GetAutoSize()[1] > self._max_content_height
        if exceeds_max_height:
            if self._collapsed:
                new_max_height = self._max_content_height
            self._expand_container.Show()
        else:
            self._expand_container.Hide()
        self._update_max_height(new_max_height, animate=animate)

    def _update_max_height(self, max_height, animate):
        if self._current_max_height == max_height:
            return
        self._current_max_height = max_height
        if max_height is None:

            def reset_max_height():
                self.content_container.maxHeight = None

            end_value = self.content_container.GetAutoSize()[1]
            callback = reset_max_height
        else:
            self.content_container.maxHeight = self.content_container.GetAbsoluteSize()[1]
            end_value = max_height
            callback = None
        eveui.animate(self.content_container, 'maxHeight', end_value=end_value, duration=0.2 if animate else 0.0, on_complete=callback)
