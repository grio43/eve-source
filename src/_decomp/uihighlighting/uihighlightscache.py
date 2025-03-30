#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uihighlighting\uihighlightscache.py
from uihighlighting.fsdloaders import MenuHighlightsLoader
from uihighlighting.fsdloaders import SpaceObjectHighlightsLoader
from uihighlighting.fsdloaders import UIHighlightsLoader
from uihighlighting.uihighlights import UiHighlight, SpaceObjectHighlight, MenuHighlight

class UiHighlightsCache(object):

    def __init__(self):
        self.ui_highlights = {}
        self.space_object_highlights = {}
        self.menu_highlights = {}
        UIHighlightsLoader.ConnectToOnReload(self.clear)
        SpaceObjectHighlightsLoader.ConnectToOnReload(self.clear)
        MenuHighlightsLoader.ConnectToOnReload(self.clear)

    def clear(self):
        self.ui_highlights.clear()
        self.space_object_highlights.clear()
        self.menu_highlights.clear()

    def load_ui_highlight_by_id(self, id):
        ui_highlight = UIHighlightsLoader.GetByID(id)
        if ui_highlight is None:
            self.ui_highlights[id] = None
            return
        title = ui_highlight.title
        seconds_til_fadeout = ui_highlight.secondsTilFadeout
        audio_setting = ui_highlight.audioEffectOn
        additional_effects = ui_highlight.additionalEffects
        default_direction = ui_highlight.defaultDirection
        offset = ui_highlight.offset
        texturePath = ui_highlight.texturePath or False
        iconID = ui_highlight.iconID
        iconSize = ui_highlight.iconSize
        iconColor = ui_highlight.iconColor
        ui_class = ui_highlight.uiClass
        return UiHighlight(id, ui_highlight.name, ui_highlight.uiElementName, title, ui_highlight.message, seconds_til_fadeout, audio_setting, additional_effects, default_direction, offset, texturePath, iconID, iconSize, iconColor, ui_class)

    def get_ui_highlight_by_id(self, id):
        try:
            ui_highlight = self.ui_highlights[id]
        except KeyError:
            ui_highlight = self.load_ui_highlight_by_id(id)
            self.ui_highlights[id] = ui_highlight

        return ui_highlight

    def load_space_object_highlight_by_id(self, id):
        space_object_highlight = SpaceObjectHighlightsLoader.GetByID(id)
        if space_object_highlight is None:
            self.space_object_highlights[id] = None
            return
        return SpaceObjectHighlight(id, space_object_highlight.name, space_object_highlight.spaceObjectType, space_object_highlight.spaceObjectID, space_object_highlight.message, space_object_highlight.hint, space_object_highlight.secondsTilFadeout, space_object_highlight.audioEffectOn, space_object_highlight.disableBracketHighlight or False, space_object_highlight.disableBox or False)

    def get_space_object_highlight_by_id(self, id):
        try:
            space_object_highlight = self.space_object_highlights[id]
        except KeyError:
            space_object_highlight = self.load_space_object_highlight_by_id(id)
            self.space_object_highlights[id] = space_object_highlight

        return space_object_highlight

    def load_menu_highlight_by_id(self, id):
        menu_highlight = MenuHighlightsLoader.GetByID(id)
        if menu_highlight is None:
            self.menu_highlights[id] = None
            return
        type_ids = menu_highlight.typeID
        return MenuHighlight(id, menu_highlight.name, menu_highlight.menuName, type_ids)

    def get_menu_highlight_by_id(self, id):
        try:
            menu_highlight = self.menu_highlights[id]
        except KeyError:
            menu_highlight = self.load_menu_highlight_by_id(id)
            self.menu_highlights[id] = menu_highlight

        return menu_highlight
