#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uihighlighting\uihighlightingservice.py
from carbon.common.lib.const import MSEC, SEC
from carbon.common.script.sys.service import Service
from carbon.common.script.util.timerstuff import AutoTimer
from copy import deepcopy
from fsdBuiltData.common.iconIDs import GetIconFile
from localization import GetByMessageID
from uihighlighting.const import SpaceObjectType, DEFAULT_AUDIO_ON
from uihighlighting.ui.uipointer import PointerBasicData
from uihighlighting.ui import uipointereffect
from uihighlighting.uihighlightscache import UiHighlightsCache
import logging
logger = logging.getLogger(__name__)

class UiHighlightingService(Service):
    __guid__ = 'svc.UiHighlightingService'
    serviceName = 'svc.UiHighlightingService'
    __displayname__ = 'UiHighlightingService'
    __servicename__ = 'UiHighlightingService'
    __notifyevents__ = ['OnSessionReset', 'OnCharacterSessionChanged']

    def __init__(self):
        super(UiHighlightingService, self).__init__()
        self.ui_pointer_svc = None
        self.ui_highlights_cache = None
        self.audio_separation_thread = None
        self.menu_highlights = set()

    def Run(self, *args, **kwargs):
        Service.Run(self, *args, **kwargs)
        self.ui_pointer_svc = sm.GetService('uipointerSvc')
        self._initialize()

    def OnSessionReset(self):
        self.ui_highlights_cache = None
        if self.audio_separation_thread is not None:
            self.audio_separation_thread.kill()
        self.audio_separation_thread = None
        self.menu_highlights = set()

    def OnCharacterSessionChanged(self, _oldCharacterID, newCharacterID):
        if newCharacterID is not None:
            self._initialize()

    def _get_cache(self):
        if not self.ui_highlights_cache:
            self.ui_highlights_cache = UiHighlightsCache()
        return self.ui_highlights_cache

    def _initialize(self):
        self._active_space_highlight_ids = {}
        self._clear_ui_elements_highlighting_timer_threads = {}
        self._clear_space_object_item_highlighting_timer_threads = {}
        self._clear_dungeon_space_object_highlighting_timer_threads = {}
        self._clear_dungeon_space_entity_group_highlighting_timer_threads = {}
        self._clear_space_object_type_highlighting_timer_threads = {}
        self._clear_space_object_group_highlighting_timer_threads = {}
        self.space_object_to_clear_highlight_data = {SpaceObjectType.TYPE_ID: [self.ui_pointer_svc.RemoveSpaceObjectUiPointersByType, self._clear_space_object_type_highlighting_timer_threads],
         SpaceObjectType.GROUP_ID: [self.ui_pointer_svc.RemoveSpaceObjectUiPointersByGroup, self._clear_space_object_group_highlighting_timer_threads],
         SpaceObjectType.OBJECT_ID: [self.ui_pointer_svc.RemoveSpaceObjectUiPointersByDungeonObject, self._clear_dungeon_space_object_highlighting_timer_threads],
         SpaceObjectType.ENTITY_GROUP_ID: [self.ui_pointer_svc.RemoveSpaceObjectUiPointersByDungeonEntityGroup, self._clear_dungeon_space_entity_group_highlighting_timer_threads],
         SpaceObjectType.ITEM_ID: [self.ui_pointer_svc.RemoveSpaceObjectUiPointersByItem, self._clear_space_object_item_highlighting_timer_threads]}

    def highlight_ui_element_by_name(self, ui_element_name, message, fadeout_seconds = None, title = None, audio_setting = DEFAULT_AUDIO_ON, default_direction = None, offset = None, texturePath = None, textureSize = None, iconColor = None, allowOffscreenPointing = False, ui_class = None, idx = -1):
        self._highlight_ui_element_by_name(ui_element_name, message, title, fadeout_seconds, audio_setting, default_direction, offset, texturePath, textureSize, iconColor, allowOffscreenPointing=allowOffscreenPointing, ui_class=ui_class, idx=idx)

    def custom_highlight_ui_element_by_name(self, ui_element_name, highlight_content, fadeout_seconds = None, audio_setting = DEFAULT_AUDIO_ON, default_direction = None, offset = None, allowOffscreenPointing = False, ui_class = None, idx = -1):
        self._highlight_ui_element_by_name(ui_element_name, None, None, fadeout_seconds, audio_setting, default_direction, offset, highlight_content=highlight_content, allowOffscreenPointing=allowOffscreenPointing, ui_class=ui_class, idx=idx)

    def _highlight_ui_element_by_name(self, ui_element_name, message = None, title = None, fadeout_seconds = None, audio_setting = DEFAULT_AUDIO_ON, default_direction = None, offset = None, texturePath = None, textureSize = None, iconColor = None, highlight_content = None, allowOffscreenPointing = False, ui_class = None, idx = -1):
        try:
            self._clear_ui_elements_highlighting_timer_threads.pop(ui_element_name, None)
            basicData = PointerBasicData(pointToID=ui_element_name, uiPointerText=message, uiPointerTitle=title, defaultDirection=default_direction, offset=offset, audioSetting=audio_setting, texturePath=texturePath, textureSize=textureSize, iconColor=iconColor, highlightContent=highlight_content, showEvenOffscreen=allowOffscreenPointing, uiClass=ui_class, idx=idx)
            self.ui_pointer_svc.PointTo(basicData=basicData)
        finally:
            if fadeout_seconds:
                fadeout_milliseconds = fadeout_seconds * SEC / MSEC
                self._clear_ui_elements_highlighting_timer_threads[ui_element_name] = AutoTimer(fadeout_milliseconds, self.clear_ui_highlighting_for_element, ui_element_name)

    def clear_ui_highlighting_for_element(self, pointToID):
        self.ui_pointer_svc.StopPointingTo(pointToID)
        self._clear_ui_elements_highlighting_timer_threads.pop(pointToID, None)
        uipointereffect.stop_effects_for_element(pointToID)

    def _highlight_space_object(self, space_object_type, space_object_id, message, hint, fadeout_seconds = None, audio_setting = DEFAULT_AUDIO_ON, show_box = True, highlight_bracket = True, highlight_id = None):
        try:
            item_id = type_id = group_id = object_id = entity_group_id = None
            if space_object_type == SpaceObjectType.ITEM_ID:
                item_id = space_object_id
            elif space_object_type == SpaceObjectType.TYPE_ID:
                type_id = space_object_id
            elif space_object_type == SpaceObjectType.GROUP_ID:
                group_id = space_object_id
            elif space_object_type == SpaceObjectType.OBJECT_ID:
                object_id = space_object_id
            elif space_object_type == SpaceObjectType.ENTITY_GROUP_ID:
                entity_group_id = space_object_id
            self.ui_pointer_svc.AddSpaceObjectTypeUiPointer(type_id, group_id, message, hint, audio_setting, localize=False, itemID=item_id, objectID=object_id, entityGroupID=entity_group_id, showBox=show_box, highlightBracket=highlight_bracket)
            if highlight_id:
                self._active_space_highlight_ids[highlight_id] = (space_object_type, space_object_id)
        finally:
            if fadeout_seconds:
                fadeout_milliseconds = fadeout_seconds * SEC / MSEC
                clear_function, clear_thread = self._get_clear_space_object_highlighting_data(space_object_type)
                clear_thread[space_object_id] = AutoTimer(fadeout_milliseconds, self._clear_space_object_highlighting, space_object_id, clear_function, clear_thread, highlight_id)

    def highlight_space_object_by_dungeon_object_id(self, object_id, message, hint, fadeout_seconds = None, audio_setting = DEFAULT_AUDIO_ON, show_box = True, highlight_bracket = True, highlight_id = None):
        self._highlight_space_object(highlight_id=highlight_id, space_object_type=SpaceObjectType.OBJECT_ID, space_object_id=object_id, message=message, hint=hint, fadeout_seconds=fadeout_seconds, audio_setting=audio_setting, show_box=show_box, highlight_bracket=highlight_bracket)

    def highlight_space_object_by_item_id(self, item_id, message, hint, fadeout_seconds = None, audio_setting = DEFAULT_AUDIO_ON, show_box = True, highlight_bracket = True, highlight_id = None):
        self._highlight_space_object(highlight_id=highlight_id, space_object_type=SpaceObjectType.ITEM_ID, space_object_id=item_id, message=message, hint=hint, fadeout_seconds=fadeout_seconds, audio_setting=audio_setting, show_box=show_box, highlight_bracket=highlight_bracket)

    def highlight_space_object_by_dungeon_entity_group_id(self, entity_group_id, message, hint, fadeout_seconds = None, audio_setting = DEFAULT_AUDIO_ON, show_box = True, highlight_bracket = True, highlight_id = None):
        self._highlight_space_object(highlight_id=highlight_id, space_object_type=SpaceObjectType.ENTITY_GROUP_ID, space_object_id=entity_group_id, message=message, hint=hint, fadeout_seconds=fadeout_seconds, audio_setting=audio_setting, show_box=show_box, highlight_bracket=highlight_bracket)

    def highlight_space_object_by_type(self, type_id, message, hint, fadeout_seconds = None, audio_setting = DEFAULT_AUDIO_ON, show_box = True, highlight_bracket = True, highlight_id = None):
        self._highlight_space_object(highlight_id=highlight_id, space_object_type=SpaceObjectType.TYPE_ID, space_object_id=type_id, message=message, hint=hint, fadeout_seconds=fadeout_seconds, audio_setting=audio_setting, show_box=show_box, highlight_bracket=highlight_bracket)

    def highlight_space_object_by_group(self, group_id, message, hint, fadeout_seconds = None, audio_setting = DEFAULT_AUDIO_ON, show_box = True, highlight_bracket = True, highlight_id = None):
        self._highlight_space_object(highlight_id=highlight_id, space_object_type=SpaceObjectType.GROUP_ID, space_object_id=group_id, message=message, hint=hint, fadeout_seconds=fadeout_seconds, audio_setting=audio_setting, show_box=show_box, highlight_bracket=highlight_bracket)

    def highlight_space_object_by_next_in_route(self, message, hint, audio_setting = DEFAULT_AUDIO_ON, show_box = True, highlight_bracket = True):
        self.ui_pointer_svc.AddNextInRouteUiPointer(message, hint, audio_setting, showBox=show_box, highlightBracket=highlight_bracket)

    def highlight_ui_elements(self, ui_highlight_ids):
        self.clear_ui_element_highlighting()
        for ui_highlight_id in ui_highlight_ids:
            self.highlight_ui_element(ui_highlight_id)

    def highlight_ui_element(self, ui_highlight_id):
        ui_highlight = self._get_cache().get_ui_highlight_by_id(ui_highlight_id)
        self._trigger_ui_highlight(ui_highlight)

    def highlight_ui_element_by_id_and_name(self, ui_highlight_id, ui_element_name):
        ui_highlight = deepcopy(self._get_cache().get_ui_highlight_by_id(ui_highlight_id))
        ui_highlight.ui_element_name = ui_element_name
        self._trigger_ui_highlight(ui_highlight)

    def _trigger_ui_highlight(self, ui_highlight):
        name = ui_highlight.ui_element_name
        if not name:
            logger.warn('Failed to trigger UI highlight, name of the UI element to highlight is not defined. Highlight ID: %s', ui_highlight.id)
            return
        msg = GetByMessageID(ui_highlight.message_path)
        timer = ui_highlight.seconds_til_fadeout
        audio_setting = ui_highlight.audio_setting
        default_direction = ui_highlight.default_direction
        offset = ui_highlight.offset
        title = GetByMessageID(ui_highlight.title_path) if ui_highlight.title_path else None
        ui_class = ui_highlight.ui_class
        uipointereffect.start_effects(name, ui_highlight.additional_effects)
        texturePath = GetIconFile(ui_highlight.iconID) if ui_highlight.iconID else None
        iconSize = ui_highlight.iconSize
        iconColor = ui_highlight.iconColor
        self.highlight_ui_element_by_name(name, msg, timer, title, audio_setting, default_direction, offset, texturePath, iconSize, iconColor, ui_class=ui_class)

    def get_ui_highlight_name(self, ui_highlight_id):
        ui_highlight = self._get_cache().get_ui_highlight_by_id(ui_highlight_id)
        if ui_highlight:
            return ui_highlight.ui_element_name

    def are_any_ui_highlights_active(self):
        return self.ui_pointer_svc.IsAnyPointerActive()

    def remove_highlight_from_ui_element_by_id(self, ui_highlight_id):
        ui_highlight_name = self.get_ui_highlight_name(ui_highlight_id)
        if ui_highlight_name:
            self.remove_highlight_from_ui_element_by_name(ui_highlight_name)

    def remove_highlight_from_ui_element_by_name(self, ui_highlight_name):
        self.ui_pointer_svc.StopPointingTo(ui_highlight_name)
        uipointereffect.stop_effects_for_element(ui_highlight_name)

    def _get_space_object_target(self, highlight, object_id, entity_group_id, type_id, group_id, item_id):
        if item_id is not None:
            return (SpaceObjectType.ITEM_ID, item_id)
        if object_id is not None:
            return (SpaceObjectType.OBJECT_ID, object_id)
        if entity_group_id is not None:
            return (SpaceObjectType.ENTITY_GROUP_ID, entity_group_id)
        if type_id is not None:
            return (SpaceObjectType.TYPE_ID, type_id)
        if group_id is not None:
            return (SpaceObjectType.GROUP_ID, group_id)
        return (getattr(highlight, 'space_object_type', None), getattr(highlight, 'space_object_id', None))

    def highlight_space_object(self, highlight_id = None, object_id = None, entity_group_id = None, type_id = None, group_id = None, item_id = None):
        highlight = self._get_cache().get_space_object_highlight_by_id(highlight_id) if highlight_id else None
        space_object_type, space_object_id = self._get_space_object_target(highlight, object_id, entity_group_id, type_id, group_id, item_id)
        if not all((space_object_type, space_object_id)):
            logger.warn('unable to load space object highlight, ID: %s objectID: %s entityGroupID: %s typeID: %s groupID: %s itemID: %s', highlight_id, object_id, entity_group_id, type_id, group_id, item_id)
            return
        msg = GetByMessageID(highlight.message_path) if highlight else ''
        hint = GetByMessageID(highlight.hint_path) if highlight else ''
        timer = highlight.seconds_til_fadeout if highlight else None
        audio_setting = highlight.audio_setting if highlight else DEFAULT_AUDIO_ON
        highlight_bracket = not highlight.disable_bracket_highlight if highlight else True
        show_box = not highlight.disable_box if highlight else False
        if space_object_type == SpaceObjectType.OBJECT_ID:
            self.highlight_space_object_by_dungeon_object_id(space_object_id, msg, hint, timer, audio_setting, show_box, highlight_bracket, highlight_id)
        elif space_object_type == SpaceObjectType.ENTITY_GROUP_ID:
            self.highlight_space_object_by_dungeon_entity_group_id(space_object_id, msg, hint, timer, audio_setting, show_box, highlight_bracket, highlight_id)
        elif space_object_type == SpaceObjectType.TYPE_ID:
            self.highlight_space_object_by_type(space_object_id, msg, hint, timer, audio_setting, show_box, highlight_bracket, highlight_id)
        elif space_object_type == SpaceObjectType.GROUP_ID:
            self.highlight_space_object_by_group(space_object_id, msg, hint, timer, audio_setting, show_box, highlight_bracket, highlight_id)
        elif space_object_type == SpaceObjectType.ITEM_ID:
            self.highlight_space_object_by_item_id(space_object_id, msg, hint, timer, audio_setting, show_box, highlight_bracket, highlight_id)
        elif space_object_type == SpaceObjectType.NEXT_ITEM_IN_ROUTE:
            self.highlight_space_object_by_next_in_route(msg, hint, audio_setting, show_box, highlight_bracket)
        else:
            logger.warn("space object highlight '%s' has unsupported space object type '%s'", highlight_id, space_object_type)

    def highlight_menu_by_ids(self, menu_highlight_ids):
        menu_highlights = [ self._get_cache().get_menu_highlight_by_id(hID) for hID in menu_highlight_ids ]
        for menu_highlight in menu_highlights:
            menu_name = menu_highlight.menu_name
            type_ids = menu_highlight.type_ids
            self.highlight_menu_by_name(menu_name, type_ids)

    def highlight_menu_by_name(self, menu_name, type_ids):
        if type_ids:
            for type_id in type_ids:
                self.menu_highlights.add((menu_name, type_id))
                sm.ScatterEvent('OnMenuHighlightActivated', menu_name, type_id)

        else:
            self.menu_highlights.add((menu_name, None))
            sm.ScatterEvent('OnMenuHighlightActivated', menu_name, None)

    def is_menu_highlighted(self, menu_name, type_id):
        return (menu_name, type_id) in self.menu_highlights

    def clear_all_highlighting(self):
        self.clear_ui_element_highlighting()
        self.clear_space_object_highlighting()
        self.clear_menu_highlighting()

    def clear_ui_element_highlighting(self):
        try:
            self.ui_pointer_svc.ClearPointers()
            uipointereffect.clear_all_effects()
        finally:
            self.clear_ui_element_highlighting_timer_thread = None

    def clear_space_object_highlighting(self):
        self.ui_pointer_svc.RemoveSpaceObjectUiPointers()
        self._clear_space_object_item_highlighting_timer_threads.clear()
        self._clear_dungeon_space_object_highlighting_timer_threads.clear()
        self._clear_dungeon_space_entity_group_highlighting_timer_threads.clear()
        self._clear_space_object_type_highlighting_timer_threads.clear()
        self._clear_space_object_group_highlighting_timer_threads.clear()
        self._active_space_highlight_ids.clear()

    def _get_clear_space_object_highlighting_data(self, space_object_type):
        clear_function = None
        clear_threads = None
        if space_object_type in self.space_object_to_clear_highlight_data:
            clear_function, clear_threads = self.space_object_to_clear_highlight_data[space_object_type]
        return (clear_function, clear_threads)

    def _clear_space_object_highlighting(self, space_object_id, clear_function, clear_thread, highlight_id):
        if clear_function and clear_thread:
            try:
                clear_function(space_object_id)
            finally:
                if space_object_id in clear_thread:
                    del clear_thread[space_object_id]
                if highlight_id and highlight_id in self._active_space_highlight_ids:
                    del self._active_space_highlight_ids[highlight_id]

    def clear_space_object_highlight(self, highlight_id = None, object_id = None, entity_group_id = None, type_id = None, group_id = None, item_id = None):
        if highlight_id and highlight_id in self._active_space_highlight_ids:
            space_object_type, space_object_id = self._active_space_highlight_ids[highlight_id]
        else:
            highlight = self._get_cache().get_space_object_highlight_by_id(highlight_id) if highlight_id else None
            space_object_type, space_object_id = self._get_space_object_target(highlight, object_id, entity_group_id, type_id, group_id, item_id)
            if not all((space_object_type, space_object_id)):
                return
        if space_object_type == SpaceObjectType.OBJECT_ID:
            self.clear_space_object_highlight_for_dungeon_object_id(space_object_id)
        elif space_object_type == SpaceObjectType.ENTITY_GROUP_ID:
            self.clear_space_object_highlight_for_dungeon_entity_group_id(space_object_id)
        elif space_object_type == SpaceObjectType.TYPE_ID:
            self.clear_space_object_highlight_for_type(space_object_id)
        elif space_object_type == SpaceObjectType.GROUP_ID:
            self.clear_space_object_highlight_for_group(space_object_id)
        elif space_object_type == SpaceObjectType.ITEM_ID:
            self.clear_space_object_highlight_for_item_id(space_object_id)
        else:
            logger.warn("space object highlight '%s' is of unsupported type '%s'", highlight_id, space_object_type)
            return
        self._active_space_highlight_ids.pop(highlight_id, None)

    def clear_space_object_highlight_for_dungeon_object_id(self, object_id):
        self.ui_pointer_svc.RemoveSpaceObjectUiPointersByDungeonObject(object_id)

    def clear_space_object_highlight_for_dungeon_entity_group_id(self, entity_group_id):
        self.ui_pointer_svc.RemoveSpaceObjectUiPointersByDungeonEntityGroup(entity_group_id)

    def clear_space_object_highlight_for_type(self, type_id):
        self.ui_pointer_svc.RemoveSpaceObjectUiPointersByType(type_id)

    def clear_space_object_highlight_for_group(self, group_id):
        self.ui_pointer_svc.RemoveSpaceObjectUiPointersByGroup(group_id)

    def clear_space_object_highlight_for_item_id(self, item_id):
        self.ui_pointer_svc.RemoveSpaceObjectUiPointersByItem(item_id)

    def clear_menu_highlighting(self):
        self.menu_highlights.clear()
        sm.ScatterEvent('OnMenuHighlightsCleared')
