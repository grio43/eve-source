#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\ui\chip.py
import carbonui
import eveui
from carbonui import TextColor, uiconst
from eve.client.script.ui import eveThemeColor

class Chip(eveui.ContainerAutoSize):
    default_state = eveui.State.normal
    default_align = eveui.Align.no_align
    default_alignMode = eveui.Align.center_left
    default_height = 28

    def __init__(self, label, icon = None, on_click = None, selected = False, value = None, inner_padding = (8, 2, 8, 2), color = eveThemeColor.THEME_FOCUSDARK, *args, **kwargs):
        super(Chip, self).__init__(*args, **kwargs)
        self._value = value
        self._on_click = on_click
        self._color = color
        if icon:
            eveui.Sprite(parent=self, align=eveui.Align.center_left, texturePath=icon, height=16, width=16, left=6, color=carbonui.TextColor.NORMAL)
        self._label = carbonui.TextBody(parent=self, align=eveui.Align.center_left, text=label, padding=inner_padding, left=18 if icon else 0)
        self._hover_frame = eveui.Frame(parent=self, align=eveui.Align.to_all, color=self._color, opacity=0, frameConst=uiconst.FRAME_FILLED_CORNER9)
        if selected:
            self._selected_frame = eveui.Frame(bgParent=self, color=self._color, opacity=1.5, frameConst=uiconst.FRAME_BORDER1_CORNER9)
        else:
            self._selected_frame = None
        self._bg_frame = eveui.Frame(bgParent=self, color=self._color, opacity=0.3, frameConst=uiconst.FRAME_FILLED_CORNER9)

    def OnClick(self, *args):
        eveui.Sound.button_click.play()
        self._on_click(self._value)

    def OnMouseEnter(self, *args):
        super(Chip, self).OnMouseEnter(*args)
        eveui.Sound.button_hover.play()
        eveui.fade_in(self._hover_frame, end_value=0.5, duration=0.2)

    def OnMouseExit(self, *args):
        super(Chip, self).OnMouseExit(*args)
        eveui.fade(self._hover_frame, end_value=0, duration=0.2)

    def OnColorThemeChanged(self):
        super(Chip, self).OnColorThemeChanged()
        color = self._color[:3]
        self._hover_frame.rgb = color
        self._bg_frame.rgb = color
        if self._selected_frame:
            self._selected_frame.rgb = color


class ContentTagChip(Chip):

    def __init__(self, content_tag, show_icon = False, *args, **kwargs):
        self._content_tag = content_tag
        kwargs['name'] = u'{}_filter_chip'.format(content_tag.id)
        kwargs['value'] = content_tag.id
        kwargs['label'] = content_tag.title
        if show_icon:
            kwargs['icon'] = content_tag.icon
        super(ContentTagChip, self).__init__(*args, **kwargs)

    def LoadTooltipPanel(self, tooltip_panel, *args):
        tooltip_panel.LoadStandardSpacing()
        tooltip_panel.columns = 1
        tooltip_panel.AddLabelSmall(text=self._content_tag.tag_type_title, color=TextColor.SECONDARY)
        if self._content_tag.icon:
            tooltip_panel.AddSpriteLabel(texturePath=self._content_tag.icon, label=self._content_tag.title, iconSize=16, iconColor=TextColor.NORMAL, iconOffset=0)
        else:
            tooltip_panel.AddLabelMedium(text=self._content_tag.title)
        if self._content_tag.description:
            tooltip_panel.AddLabelMedium(text=self._content_tag.description, wrapWidth=300)
