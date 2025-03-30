#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\autocomplete\suggestion_entry.py
import abc
import proper
from carbonui import TextBody, TextDetail
from eveui import Container, ContainerAutoSize, Fill
from eveui.audio import Sound
from eveui.button.icon import ButtonIcon
from eveui.constants import Align, State
from eveui.decorators import lazy
from eveui.scale import reverse_scale_dpi
from eveui.autocomplete.fuzzy import get_highlighted_string

class SuggestionEntryBase(proper.Observable, Container):
    __metaclass__ = abc.ABCMeta
    isDragObject = True

    def __init__(self, autocomplete_controller, suggestion, **kwargs):
        self.controller = autocomplete_controller
        self.suggestion = suggestion
        self.__selected_highlight = None
        kwargs.setdefault('state', State.normal)
        kwargs.setdefault('clipChildren', True)
        super(SuggestionEntryBase, self).__init__(**kwargs)
        self.__layout()
        self.bind(selected=self.__on_selected)

    @abc.abstractmethod
    def layout(self):
        pass

    @proper.alias
    def selected(self):
        return self.controller.selected_suggestion == self.suggestion

    @proper.ty(default=None)
    def query(self):
        pass

    @lazy
    def leading_container(self):
        return ContainerAutoSize(parent=self, align=Align.to_left, idx=0)

    @lazy
    def trailing_container(self):
        return ContainerAutoSize(parent=self, align=Align.to_right, idx=0)

    def __on_selected(self, _, selected):
        if selected:
            Sound.entry_hover.play()
        self.__update_selected(selected)

    def __layout(self):
        self.layout()
        self.__update_selected(self.selected)

    def __update_selected(self, selected):
        if selected:
            self.__show_selected_highlight()
        else:
            self.__hide_selected_highlight()

    def __show_selected_highlight(self):
        if self.__selected_highlight is None:
            self.__selected_highlight = Fill(bgParent=self, color=(0.0, 0.0, 0.0))
        self.__selected_highlight.opacity = 0.4

    def __hide_selected_highlight(self):
        if self.__selected_highlight is not None:
            self.__selected_highlight.opacity = 0.0

    def OnMouseEnter(self, *args):
        try:
            self.controller.selected_suggestion = self.suggestion
        except ValueError:
            pass

    def OnClick(self):
        self.controller.complete()

    def GetMenu(self):
        return self.suggestion.get_menu()

    def GetDragData(self):
        drag_data = self.suggestion.get_drag_data()
        if drag_data is not None:
            return [drag_data]


class VerticalCenteredContainer(Container):

    def UpdateAlignment(self, *args, **kwds):
        budgetLeft, budgetTop, budgetWidth, budgetHeight, sizeChange = super(VerticalCenteredContainer, self).UpdateAlignment(*args, **kwds)
        if self.children:
            content_height = 0
            for child in self.children:
                content_height += child.height + child.padTop + child.padBottom

            free_height = reverse_scale_dpi(budgetHeight) - content_height
            self.children[0].top = int(round(free_height / 2.0))
        return (budgetLeft,
         budgetTop,
         budgetWidth,
         budgetHeight,
         sizeChange)


class InfoButtonComponent(object):

    def __init__(self, **kwargs):
        self.__container = None
        super(InfoButtonComponent, self).__init__(**kwargs)
        self.bind(selected=self.__on_selected)

    @property
    def is_info_button_available(self):
        return self.suggestion.has_show_info()

    @property
    def is_info_button_visible(self):
        return self.__container is not None

    def layout(self):
        super(InfoButtonComponent, self).layout()
        if self.selected and self.suggestion.has_show_info():
            self.__show_info_button()

    def __show_info_button(self):
        if self.is_info_button_visible:
            return
        self.__container = Container(parent=self.trailing_container, align=Align.to_right, width=24)
        ButtonIcon(parent=self.__container, align=Align.center, size=16, texture_path='res:/UI/Texture/Icons/38_16_208.png', on_click=self.__show_info)

    def __hide_info_button(self):
        if self.__container:
            self.__container.Close()
            self.__container = None

    def __show_info(self):
        self.suggestion.show_info()

    def __on_selected(self, _, selected):
        if not self.is_info_button_available:
            return
        if selected and self.is_info_button_available:
            self.__show_info_button()
        else:
            self.__hide_info_button()


class LargeSuggestionEntry(InfoButtonComponent, SuggestionEntryBase):
    default_height = 42

    def __init__(self, get_suggestion_text = None, **kwargs):
        self.__label = None
        self.__sublabel = None
        self.__icon_size = self.default_height - 2
        self.__icon_margin = 1
        self._get_suggestion_text = get_suggestion_text
        super(LargeSuggestionEntry, self).__init__(**kwargs)

    def layout(self):
        self._render_icon()
        text_container = VerticalCenteredContainer(parent=self, align=Align.to_all, padLeft=8)
        subtext = self.suggestion.subtext
        if subtext:
            self.__sublabel = TextDetail(parent=text_container, align=Align.to_top, text=subtext, maxLines=1, opacity=0.4)
        self.__label = TextBody(parent=text_container, align=Align.to_top, text=self.__get_text(), maxLines=2 if subtext is None else 1)
        super(LargeSuggestionEntry, self).layout()

    def _render_icon(self):
        icon = self.suggestion.render_icon(size=self.__icon_size)
        if icon is None:
            return
        if self.destroyed:
            icon.Close()
            return
        self.__icon_container = Container(parent=self.leading_container, align=Align.to_left, state=State.disabled, width=self.__icon_size + self.__icon_margin * 2)
        icon.align = Align.center
        icon.SetParent(self.__icon_container, idx=-1)

    def on_query(self, query):
        self.__label.SetText(self.__get_text())
        if self.__sublabel is not None:
            self.__sublabel.SetText(self.__get_subtext())

    def __get_text(self):
        text = self._get_suggestion_text(self.suggestion)
        return get_highlighted_string(text, self.query)

    def __get_subtext(self):
        return self.suggestion.subtext
