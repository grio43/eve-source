#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\collapseGroup.py
import eveicon
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.fill import Fill
from carbonui import Align, uiconst, TextBody, TextColor
from carbonui.control.buttonIcon import ButtonIcon
from eveui import fade

class CollapseGroup(ContainerAutoSize):
    default_icon = None
    default_label = ''
    default_align = Align.TOTOP
    icon = None
    text = None
    header_color = None

    def ApplyAttributes(self, attributes):
        super(CollapseGroup, self).ApplyAttributes(attributes)
        self.icon = attributes.Get('icon', self.default_icon)
        self.text = attributes.Get('text', self.default_label)
        self._construct_layout()

    def _construct_layout(self):
        self._construct_header()
        self._construct_main_cont()

    def _construct_header(self):
        self.headerCont = Container(name='headerCont', parent=self, state=uiconst.UI_NORMAL, align=Align.TOTOP, height=32)
        self.headerBG = Fill(bgParent=self.headerCont, opacity=0.05)
        self.headerCont.OnClick = self._on_click
        self.headerCont.OnMouseEnter = self._on_mouse_enter
        self.headerCont.OnMouseExit = self._on_mouse_exit
        if self.icon:
            self.iconCont = Container(name='iconCont', parent=self.headerCont, align=Align.TOLEFT, width=24, state=uiconst.UI_DISABLED)
            self.icon = Sprite(name='icon', parent=self.iconCont, align=Align.CENTERRIGHT, texturePath=self.icon, color=TextColor.SECONDARY, width=16, height=16, state=uiconst.UI_DISABLED)
        self.expanderCont = Container(name='expanderCont', parent=self.headerCont, align=Align.TORIGHT, width=32, state=uiconst.UI_PICKCHILDREN)
        self.expanderIcon = ButtonIcon(name='expander', parent=self.expanderCont, align=Align.CENTER, texturePath=eveicon.chevron_up, iconSize=18, func=self._on_click)
        self._construct_label()

    def _construct_main_cont(self):
        self.mainCont = ContainerAutoSize(name='mainCont', parent=self, align=Align.TOTOP, state=uiconst.UI_PICKCHILDREN, padTop=2)

    def _construct_label(self):
        self.labelCont = ContainerAutoSize(name='labelCont', parent=self.headerCont, align=Align.TOALL, state=uiconst.UI_DISABLED, clipChildren=True, padTop=6)
        self.label = TextBody(name='label', parent=self.labelCont, align=Align.TOLEFT, text=self.text, padLeft=8, color=TextColor.NORMAL, state=uiconst.UI_DISABLED, bold=True, autoFadeSides=16)

    def SetCollapsed(self, collapsed):
        if collapsed:
            self.mainCont.Hide()
            self.expanderIcon.SetTexturePath(eveicon.chevron_down)
        else:
            self.mainCont.Show()
            self.expanderIcon.SetTexturePath(eveicon.chevron_up)

    def Toggle(self):
        self.SetCollapsed(self.mainCont.display)

    def _on_click(self, *args):
        self.Toggle()

    def _on_mouse_enter(self, *args):
        fade(self.headerBG, end_value=0.1)

    def _on_mouse_exit(self, *args):
        fade(self.headerBG, end_value=0.05)
