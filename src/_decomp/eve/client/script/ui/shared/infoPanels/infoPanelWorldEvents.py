#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\infoPanelWorldEvents.py
import blue
import eveicon
import eveui
from carbonui import Align, TextColor
from eve.client.script.ui.shared.infoPanels.InfoPanelBase import InfoPanelBase
from eve.client.script.ui.shared.infoPanels.const.infoPanelConst import PANEL_WORLD_EVENTS
from objectives.client.ui.objective_chain import ObjectiveChainEntry
import eveformat
import localization
from carbonui.services.setting import SessionSettingNumeric
from eve.client.script.ui import eveColor, eveThemeColor
from metadata.common.content_tags import get_content_tag_as_object, ContentTags
from carbonui.control.buttonIcon import ButtonIcon
from jobboard.client import get_job_board_service, get_world_event_job, open_world_event
SCROLL_CONTAINER_HEIGHT_MAX = 450
HEADER_BG_COLOR = (0, 0, 0, 0.35)

class InfoPanelWorldEvents(InfoPanelBase):
    default_name = 'InfoPanelWorldEvents'
    panelTypeID = PANEL_WORLD_EVENTS
    hasSettings = False
    label = 'UI/Metadata/ContentTags/WorldEvents'
    _scroll_fraction = SessionSettingNumeric(0, 0.0, 1.0)

    @staticmethod
    def IsAvailable():
        return bool(sm.GetService('tale').get_active_world_event_tales())

    @classmethod
    def GetTexturePath(cls):
        return get_content_tag_as_object(ContentTags.feature_world_events).icon

    def __init__(self, **kwargs):
        self._entries = {}
        self._scroll_initialized = False
        self._constructing = True
        super(InfoPanelWorldEvents, self).__init__(**kwargs)
        self._layout()
        self._refresh_entries()
        self._update_content_container_scroll_position()

    def ConstructNormal(self):
        if self._constructing or self.destroyed:
            return
        self._refresh_entries()

    @property
    def service(self):
        return sm.GetService('tale')

    @eveui.skip_if_destroyed
    def _refresh_entries(self):
        tales = self.service.get_active_world_event_tales()
        tale_ids = set([ tale.tale_id for tale in tales ])
        previous_entry_ids = self._entries.keys()
        obsolete_entry_ids = list(set(previous_entry_ids) - tale_ids)
        for entry_id in obsolete_entry_ids:
            if entry_id not in self._entries:
                continue
            entry = self._entries[entry_id]
            entry.Close()
            self._entries[entry_id] = None
            self._entries.pop(entry_id)

        for index, tale in enumerate(tales):
            if tale.tale_id not in previous_entry_ids:
                self._construct_tale_entry(tale, index)
            else:
                self._entries[tale.tale_id].SetOrder(index)

        self._update_content_container_height()

    @eveui.skip_if_destroyed
    def _construct_tale_entry(self, tale, index):
        entry = TaleInfoPanelEntry(parent=self._content_container, tale=tale, padBottom=4, padTop=4, idx=index, callback=self._update_content_container_height)
        self._entries[tale.tale_id] = entry

    def _layout(self):
        self._constructing = True
        self._title = eveui.EveCaptionSmall(name='title', parent=self.headerCont, align=eveui.Align.center_left, text=localization.GetByLabel(self.label))
        self._content_container = eveui.ScrollContainer(name='content_scroll_container', parent=self.mainCont, align=Align.TOTOP, height=0)
        self._content_container.OnScrolledVertical = self._on_scroll
        self._constructing = False

    def ConstructHeaderButton(self):
        container = eveui.Container(parent=self.headerBtnCont, align=eveui.Align.center_right, width=28, height=28)
        return ButtonIcon(parent=container, align=eveui.Align.center, iconSize=18, width=18, height=18, texturePath=self.GetTexturePath(), func=self._open_job_board)

    def _open_job_board(self, *args, **kwargs):
        get_job_board_service().open_browse_page(content_tag_id=ContentTags.feature_world_events)

    def _update_content_container_height(self):
        if not self._content_container or self._content_container.destroyed:
            return
        totalHeight = self._content_container.mainCont.height
        self._content_container.height = min(totalHeight, SCROLL_CONTAINER_HEIGHT_MAX)
        self._content_container.clipCont.clipChildren = totalHeight > SCROLL_CONTAINER_HEIGHT_MAX

    def _update_content_container_scroll_position(self):
        blue.synchro.Yield()
        if not self._content_container or self._content_container.destroyed:
            return
        self._scroll_initialized = True
        self._content_container.ScrollToVertical(self._scroll_fraction.get())

    def _on_scroll(self, pos_fraction):
        if self._scroll_initialized:
            self._scroll_fraction.set(self._content_container.GetPositionVertical())


class TaleInfoPanelEntry(eveui.ContainerAutoSize):
    default_align = Align.TOTOP
    default_alignMode = Align.TOTOP
    default_clipChildren = True

    def __init__(self, tale, *args, **kwargs):
        kwargs.setdefault('name', str(tale.tale_id))
        super(TaleInfoPanelEntry, self).__init__(*args, **kwargs)
        self._tale = tale
        self._is_hovered = False
        self._objective_chain_entry = None
        self._layout()
        if self._expanded:
            self._expand()
        self._update_hover_state()
        self._register()
        self._on_progress()

    def Close(self):
        self._unregister()
        if self._objective_chain_entry:
            self._objective_chain_entry.Close()
            self._objective_chain_entry = None
        super(TaleInfoPanelEntry, self).Close()
        self.callback = None
        self._tale = None

    def _register(self):
        self._tale.context.subscribe_to_value('current_progress', self._on_progress)

    def _unregister(self):
        self._tale.context.unsubscribe_from_value('current_progress', self._on_progress)

    @property
    def _expanded(self):
        return self._tale.context.get_value('is_expanded')

    @_expanded.setter
    def _expanded(self, value):
        self._tale.context.update_value('is_expanded', value)

    @property
    def _current_progress(self):
        return self._tale.context.get_value('current_progress', 0)

    @property
    def _target_progress(self):
        return self._tale.context.get_value('target_progress', 0)

    @property
    def _progress_percentage(self):
        target = self._target_progress
        if not target:
            return 0
        return float(self._current_progress) / target

    @property
    def _has_progress(self):
        return bool(self._target_progress)

    @property
    def _progress_text(self):
        target_progress = self._target_progress
        if not target_progress:
            return ''
        elif target_progress >= 100:
            return u'{value}%'.format(value=int(self._progress_percentage * 100))
        else:
            return u'{}/{}'.format(eveformat.number(self._current_progress, 0), eveformat.number(self._target_progress, 0))

    def _on_progress(self, *args, **kwargs):
        if not self._tale:
            return
        text = self._progress_text
        if not text:
            return
        self._progress_label.text = text
        eveui.animate(self._progress_fill, 'width', end_value=self._progress_percentage, duration=1)
        self._update_progress_color()

    def _layout(self):
        self._construct_header()
        self._content_container = eveui.ContainerAutoSize(name='content_container', parent=self, align=Align.TOTOP, alignMode=Align.TOTOP)

    def _construct_header(self):
        self._header_container = header_container = eveui.ContainerAutoSize(name='header_container', parent=self, state=eveui.State.normal, align=Align.TOTOP, alignMode=Align.TOTOP_NOPUSH, bgColor=HEADER_BG_COLOR)
        header_container.OnClick = self.OnClick
        header_container.GetMenu = self.GetMenu
        wrapper = eveui.ContainerAutoSize(parent=header_container, align=Align.TOTOP_NOPUSH, alignMode=Align.TOTOP, padding=8)
        job = get_world_event_job(self._tale.tale_id)
        if job:
            icon_container = eveui.ContainerAutoSize(parent=wrapper, align=eveui.Align.to_left, padRight=8, width=16)
            view_details_button = ButtonIcon(name='view_details_button', parent=icon_container, align=eveui.Align.center, texturePath=job.feature_tag.icon, iconSize=16, width=16, height=16, color=TextColor.NORMAL, func=self._open_tale_details, hint=localization.GetByLabel('UI/Opportunities/ViewOpportunity'))
            view_details_button.isDragObject = True
            view_details_button.GetDragData = job.get_drag_data
        progress_text_container = eveui.ContainerAutoSize(parent=wrapper, state=eveui.State.disabled, align=eveui.Align.to_right, clipChildren=True)
        self._progress_label = eveui.EveLabelLarge(parent=progress_text_container, align=eveui.Align.center_right, text=self._progress_text, maxLines=1, padLeft=4)
        title_container = eveui.ContainerAutoSize(parent=wrapper, state=eveui.State.disabled, align=Align.TOTOP, clipChildren=True)
        self._title = eveui.EveLabelLarge(parent=title_container, align=Align.TOTOP, text=self._tale.title, maxLines=1, showEllipsis=True, color=TextColor.HIGHLIGHT)
        progress_fill_container = eveui.Container(name='progress_fill_container', parent=header_container, align=eveui.Align.to_all, clipChildren=True, opacity=0.15)
        self._progress_fill = eveui.StretchSpriteHorizontal(parent=progress_fill_container, align=eveui.Align.to_left_prop, texturePath='res:/UI/Texture/classes/InfoPanels/progress_bar_solid.png', color=self._get_progress_color(), leftEdgeSize=2, rightEdgeSize=10, padLeft=-2, padRight=-10, width=self._progress_percentage)

    @eveui.skip_if_destroyed
    def _construct_body(self):
        if self._objective_chain_entry:
            self._objective_chain_entry.Close()
            self._objective_chain_entry = None
        objective_chain = self._tale.objective_chain
        if objective_chain:
            self._objective_chain_entry = ObjectiveChainEntry(parent=self._content_container, objective_chain=objective_chain)

    def _reconstruct_body(self):
        self._content_container.Flush()
        self._construct_body()

    def _expand(self):
        self._expanded = True
        self._reconstruct_body()
        self._update_hover_state()

    def _collapse(self):
        self._expanded = False
        self._content_container.Flush()
        self._update_hover_state()

    def OnClick(self):
        if self._expanded:
            eveui.Sound.collapse.play()
        else:
            eveui.Sound.expand.play()
        if self._expanded:
            self._collapse()
        else:
            self._expand()

    def GetMenu(self):
        return self._tale.get_menu()

    def OnMouseEnter(self, *args):
        super(TaleInfoPanelEntry, self).OnMouseEnter(*args)
        self._is_hovered = True
        self._update_hover_state()

    def OnMouseExit(self, *args):
        super(TaleInfoPanelEntry, self).OnMouseEnter(*args)
        self._is_hovered = False
        self._update_hover_state()

    def _update_hover_state(self):
        has_progress = self._has_progress
        self._progress_fill.display = has_progress and not self._expanded
        self._progress_label.display = has_progress and not self._expanded and not self._is_hovered
        if self._expanded or self._is_hovered:
            eveui.fade(self._header_container.bgFill, end_value=0.5, duration=0.2)
        else:
            eveui.fade(self._header_container.bgFill, end_value=HEADER_BG_COLOR[3], duration=0.2)

    def _get_progress_color(self):
        if self._progress_percentage < 1:
            return eveThemeColor.THEME_FOCUS
        else:
            return eveColor.SUCCESS_GREEN

    def _update_progress_color(self):
        self._progress_fill.color = self._get_progress_color()

    def OnColorThemeChanged(self):
        super(TaleInfoPanelEntry, self).OnColorThemeChanged()
        self._update_progress_color()

    def _open_tale_details(self, *args, **kwargs):
        open_world_event(self._tale.tale_id)
