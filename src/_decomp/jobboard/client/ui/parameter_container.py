#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\ui\parameter_container.py
import eveui
import carbonui
from carbonui import Align, PickState, TextColor, uiconst
from carbonui.primitives.cardsContainer import CardsContainer

class ParameterContainer(eveui.ContainerAutoSize):
    default_state = uiconst.UI_NORMAL
    default_alignMode = Align.TOPLEFT

    def ApplyAttributes(self, attributes):
        super(ParameterContainer, self).ApplyAttributes(attributes)
        caption = attributes.caption
        icon = attributes.icon
        text = attributes.text
        self.get_menu = attributes.get_menu
        self.displayTextBackground = attributes.get('displayTextBackground', True)
        padding_top = 0
        padding_left = 0
        min_row_height = 32
        if caption:
            carbonui.TextBody(parent=self, align=Align.TOPLEFT, text=caption, color=TextColor.SECONDARY)
            padding_top = 23
        if icon:
            icon_size = 16
            icon_container = eveui.Container(name='icon_container', parent=self, align=Align.TOPLEFT, pos=(0,
             padding_top,
             min_row_height,
             min_row_height), bgTexturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_SolidMirrored.png', bgColor=(1, 1, 1, 0.05))
            eveui.Sprite(name='icon', parent=icon_container, align=Align.CENTER, color=TextColor.SECONDARY, pos=(0,
             0,
             icon_size,
             icon_size), texturePath=icon)
            padding_left = min_row_height + 4
        if text:
            text_cont = eveui.ContainerAutoSize(name='text_cont', parent=self, align=Align.TOALL, clipChildren=True, pos=(padding_left,
             padding_top,
             0,
             0), minHeight=min_row_height)
            if self.displayTextBackground:
                eveui.Frame(bgParent=text_cont, cornerSize=9, texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png', color=(1, 1, 1, 0.1))
            self._text = carbonui.TextBody(parent=text_cont, align=Align.CENTERLEFT, text=text, left=8, maxLines=1, autoFadeSides=16, state=uiconst.UI_NORMAL)

    def GetMenu(self):
        if self.get_menu:
            return self.get_menu()

    @property
    def text(self):
        return self._text.text

    @text.setter
    def text(self, txt):
        self._text.text = txt


class GoalParameterContainer(eveui.ContainerAutoSize):
    default_alignMode = Align.TOTOP

    def __init__(self, controller, *args, **kwargs):
        super(GoalParameterContainer, self).__init__(*args, **kwargs)
        self._controller = controller
        self._layout()

    def _layout(self):
        carbonui.TextBody(parent=self, align=Align.TOTOP, text=self._controller.title, color=TextColor.SECONDARY, padBottom=6)
        content = eveui.ContainerAutoSize(parent=self, align=Align.TOTOP, alignMode=Align.TOTOP, minHeight=32)
        icon_container = eveui.Container(name='icon_container', parent=content, state=carbonui.uiconst.UI_NORMAL, align=Align.TOPLEFT, width=32, height=32, bgTexturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_SolidMirrored.png', bgColor=(1, 1, 1, 0.05), hint=self._controller.info)
        eveui.Sprite(name='icon', parent=icon_container, align=Align.CENTER, color=TextColor.SECONDARY, width=16, height=16, texturePath=self._controller.icon)
        values = self._controller.values
        entries_parent = CardsContainer(parent=content, align=Align.TOTOP, padLeft=36, cardHeight=self._controller.get_entry_height() if values else 32, cardMaxWidth=260, contentSpacing=(8, 8), allow_stretch=True)
        if values:
            if isinstance(values, list):
                for value in self._controller.values:
                    self._construct_entry(entries_parent, value)

            else:
                self._construct_entry(entries_parent, values)
        else:
            self._construct_none_entry(entries_parent)

    def _construct_entry(self, parent, value):
        entry = eveui.Container(name=u'entry_{}'.format(value), parent=parent, align=Align.TOTOP, state=carbonui.uiconst.UI_NORMAL, clipChildren=True)
        entry.GetMenu = lambda *args, **kwargs: self._controller.get_entry_menu(value)
        entry.GetDragData = lambda *args: self._get_entry_drag_data(value)
        entry.MakeDragObject()
        eveui.Frame(bgParent=entry, cornerSize=9, texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png', color=(1, 1, 1, 0.1))
        content = eveui.Container(parent=entry, align=Align.TOALL, padding=8)
        icon = self._controller.construct_entry_icon(value)
        if icon:
            icon_container = eveui.ContainerAutoSize(name='icon_container', parent=content, align=Align.TOLEFT, padRight=8)
            icon.SetParent(icon_container)
            icon.GetMenu = entry.GetMenu
            icon.GetDragData = entry.GetDragData
            icon.MakeDragObject()
        label_container = eveui.ContainerAutoSize(parent=content, align=Align.VERTICALLY_CENTERED)
        subtitle = self._controller.get_entry_subtitle(value)
        if subtitle:
            carbonui.TextDetail(parent=label_container, align=Align.TOTOP, text=subtitle, maxLines=1, autoFadeSides=16, color=TextColor.SECONDARY)
        title = self._controller.get_entry_title(value)
        carbonui.TextBody(parent=label_container, align=Align.TOTOP, text=title, maxLines=1, autoFadeSides=16)

    def _construct_none_entry(self, parent):
        entry = eveui.Container(parent=parent, align=Align.TOTOP, state=carbonui.uiconst.UI_NORMAL)
        entry.GetMenu = lambda *args, **kwargs: self._controller.get_none_entry_menu()
        eveui.Frame(bgParent=entry, cornerSize=9, texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png', color=(1, 1, 1, 0.1))
        content = eveui.Container(parent=entry, align=Align.TOALL, padding=8, clipChildren=True)
        carbonui.TextBody(parent=content, align=Align.CENTERLEFT, text=self._controller.get_none_value_text(), autoFadeSides=16)

    def _get_entry_drag_data(self, value):
        data = self._controller.get_entry_drag_data(value)
        if data:
            return [data]
