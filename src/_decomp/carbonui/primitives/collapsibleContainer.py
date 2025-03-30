#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\primitives\collapsibleContainer.py
import eveicon
from carbonui import Align, TextBody, uiconst, TextColor
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.primitives.container import Container, Sprite
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.line import Line
from carbonui.util.color import Color
from carbonui.uiconst import PickState

class CollapsibleContainer(ContainerAutoSize):
    LINE_HEIGHT = 1
    LINE_TOP = 9
    default_collapsedHeight = 120
    default_maxFadeHeight = 20
    default_backgroundColor = None
    default_topSpacing = 0
    default_textClass = TextBody

    def ApplyAttributes(self, attributes):
        self.container_bottom_line_simple = None
        self.container_bottom_line_expander = None
        super(CollapsibleContainer, self).ApplyAttributes(attributes)
        self._collapsed_height = attributes.get('collapsedHeight', self.default_collapsedHeight)
        self._maxFadeHeight = attributes.get('maxFadeHeight', self.default_maxFadeHeight)
        self._backgroundColor = attributes.get('backgroundColor', self.default_backgroundColor)
        self._topSpacing = attributes.get('topSpacing', self.default_topSpacing)
        textCls = attributes.get('textClass', self.default_textClass)
        self._is_collapsed = True
        self._show_all = False
        self.sub_cont = ContainerAutoSize(parent=self, align=Align.TOTOP, clipChildren=True, padTop=self._topSpacing)
        self.lore = textCls(name='label_lore', parent=self.sub_cont, align=Align.TOTOP, state=uiconst.UI_NORMAL, color=Color.GRAY6)
        self._build_expander_bottom_line()
        self._build_simple_bottom_line()
        if self._backgroundColor:
            bgCont = Container(bgParent=self.sub_cont, align=Align.TOALL, bgColor=self._backgroundColor)

    def ToggleExpand(self):
        if self._is_collapsed:
            self.sub_cont.maxHeight = None
            self._is_collapsed = False
        else:
            self._is_collapsed = True
            self.sub_cont.maxHeight = self._collapsed_height
        self.update_collapse_display()

    def set_text(self, text, show_all = False):
        self._show_all = show_all
        self.lore.text = text
        self.update_collapse_display()

    def update_collapse_display(self):
        if not self.container_bottom_line_expander or not self.container_bottom_line_simple:
            return
        new_max_height = None
        if self.is_expander_needed() and not self._show_all:
            self.container_bottom_line_expander.Show()
            self.container_bottom_line_simple.Hide()
            if self._is_collapsed:
                new_max_height = self._collapsed_height
        else:
            self.container_bottom_line_expander.Hide()
            self.container_bottom_line_simple.Show()
        self.sub_cont.maxHeight = new_max_height
        if self.sub_cont.maxHeight:
            self.lore.SetBottomAlphaFade(self._collapsed_height, self._maxFadeHeight)
            self.expander_icon.SetTexturePath(eveicon.chevron_down_double)
        else:
            self.lore.SetBottomAlphaFade()
            self.expander_icon.SetTexturePath(eveicon.chevron_up_double)

    def is_expander_needed(self):
        text_height = self.lore.textheight
        return text_height > self._collapsed_height + 6

    def _build_simple_bottom_line(self):
        self.container_bottom_line_simple = Container(name='container_bottom_line_simple', parent=self, align=uiconst.TOTOP, height=20, padTop=4)
        Line(name='simple_line', parent=self.container_bottom_line_simple, align=uiconst.TOTOP, weight=self.LINE_HEIGHT, top=self.LINE_TOP)

    def _build_expander_bottom_line(self):
        self.container_bottom_line_expander = Container(name='container_bottom_line_expander', parent=self, align=uiconst.TOTOP, pickState=PickState.ON, height=20, padTop=4)
        self.container_bottom_line_expander.OnClick = self.ToggleExpand
        left_cont = Container(name='left_cont', parent=self.container_bottom_line_expander, align=uiconst.TOLEFT_PROP, width=0.5, padRight=16)
        Line(name='bottom_line_left', parent=left_cont, align=uiconst.TOTOP, weight=self.LINE_HEIGHT, top=self.LINE_TOP)
        right_cont = Container(name='right_cont', parent=self.container_bottom_line_expander, align=uiconst.TORIGHT_PROP, width=0.5, padLeft=16)
        Line(name='bottom_line_right', parent=right_cont, align=uiconst.TOTOP, weight=self.LINE_HEIGHT, top=self.LINE_TOP)
        self.expander_icon = ButtonIcon(parent=self.container_bottom_line_expander, align=uiconst.CENTER, width=20, height=20, iconSize=16, texturePath=eveicon.chevron_down_double, func=self.ToggleExpand, iconColor=TextColor.SECONDARY)
        self.container_bottom_line_expander.Hide()

    def _OnResize(self, *args):
        self.update_collapse_display()
