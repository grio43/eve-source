#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\section.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.uianimations import animations
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import EveHeaderMedium
COLOR_BG = (0, 0, 0, 0.25)
COLOR_HEADER = (0.5, 0.5, 0.5, 0.3)
COLOR_SUBSECTION_FRAME = (0.15, 0.15, 0.15, 1.0)

class ChildBypassMixin(object):

    def TurnOnBypassToMainCont(self):
        self.children.insert = self._InsertChild
        self.children.append = self._AppendChild
        self.children.remove = self._RemoveChild

    def _InsertChild(self, idx, obj):
        self.mainCont.children.insert(idx, obj)

    def _AppendChild(self, obj):
        self.mainCont.children.append(obj)

    def _RemoveChild(self, obj):
        self.mainCont.children.remove(obj)

    def Flush(self):
        self.mainCont.Flush()


class Section(ChildBypassMixin, Container):
    default_name = 'Section'
    default_inside_padding = (10, 10, 10, 10)
    default_headerText = ''

    def ApplyAttributes(self, attributes):
        super(Section, self).ApplyAttributes(attributes)
        self.headerText = attributes.Get('headerText', self.default_headerText)
        self.mainContainerPadding = attributes.Get('insidePadding', self.default_inside_padding)
        self.__ConstructLayout()
        self.TurnOnBypassToMainCont()

    def __ConstructLayout(self):
        self._ConstructHeader()
        self._ConstructMainContainer()
        self._ConstructFrame()

    def _ConstructHeader(self):
        self.headerCont = Header(parent=self, align=uiconst.TOTOP, text=self.headerText)

    def _ConstructMainContainer(self):
        self.mainCont = Container(name='mainCont', parent=self, padding=self.mainContainerPadding)

    def _ConstructFrame(self):
        Frame(bgParent=self, texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png', cornerSize=9, color=COLOR_BG)

    def SetText(self, text):
        self.headerCont.SetText(text)


class SectionAutoSize(ChildBypassMixin, ContainerAutoSize):
    default_name = 'SectionAutoSize'
    default_inside_padding = (10, 10, 10, 10)
    default_headerText = ''
    default_mirrored = False
    default_color = COLOR_BG

    def ApplyAttributes(self, attributes):
        super(SectionAutoSize, self).ApplyAttributes(attributes)
        self.headerText = attributes.Get('headerText', self.default_headerText)
        self.mainContainerPadding = attributes.Get('insidePadding', self.default_inside_padding)
        self.mirrored = attributes.get('mirrored', self.default_mirrored)
        self.color = attributes.get('color', self.default_color)
        self.__ConstructLayout()
        self.TurnOnBypassToMainCont()

    def __ConstructLayout(self):
        self._ConstructHeader()
        self._ConstructMainContainer()
        self._ConstructFrame()

    def _ConstructHeader(self):
        self.headerCont = Header(parent=self, align=uiconst.TOTOP, text=self.headerText)

    def _ConstructMainContainer(self):
        self.mainCont = ContainerAutoSize(name='mainCont', parent=self, align=uiconst.TOTOP, padding=self.mainContainerPadding, alignMode=self.alignMode)

    def _ConstructFrame(self):
        self.frame = Frame(bgParent=self, texturePath=self._GetFrameTexturePath(), cornerSize=9, color=self._bgColor or self.color)

    def _GetFrameTexturePath(self):
        if self.mirrored:
            return 'res:/UI/Texture/Shared/DarkStyle/panel1Corner_SolidMirrored.png'
        return 'res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png'

    def SetText(self, text):
        self.headerCont.SetText(text)

    def _SetupBackground(self):
        pass


class SubSection(ChildBypassMixin, Container):
    default_name = 'SubSection'
    default_inside_padding = (6, 6, 6, 6)
    default_headerText = ''
    default_stroked = True
    default_frameColor = COLOR_SUBSECTION_FRAME

    def ApplyAttributes(self, attributes):
        super(SubSection, self).ApplyAttributes(attributes)
        self.headerText = attributes.Get('headerText', self.default_headerText)
        self.mainContainerPadding = attributes.Get('insidePadding', self.default_inside_padding)
        self.stroked = attributes.Get('stroked', self.default_stroked)
        self.frameColor = attributes.Get('frameColor', self.default_frameColor)
        self.__ConstructLayout()
        self.TurnOnBypassToMainCont()

    def __ConstructLayout(self):
        self.caption = EveHeaderMedium(parent=self, align=uiconst.TOTOP, text=self.headerText, padBottom=2)
        self.mainCont = Container(name='mainCont', parent=self, padding=self.mainContainerPadding)
        self._ConstructFrame()

    def _ConstructFrame(self):
        texturePath = 'res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png'
        if self.stroked:
            texturePath = 'res:/UI/Texture/Shared/DarkStyle/panel1Corner_Stroke.png'
        Frame(bgParent=self, texturePath=texturePath, cornerSize=9, color=self.frameColor, padTop=18)

    def SetText(self, text):
        self.caption.SetText(text)


class SubSectionAutoSize(ChildBypassMixin, ContainerAutoSize):
    default_name = 'SubSectionAutoSize'
    default_inside_padding = (6, 6, 6, 6)
    default_headerText = ''
    default_framePadTop = 18

    def ApplyAttributes(self, attributes):
        super(SubSectionAutoSize, self).ApplyAttributes(attributes)
        self.headerText = attributes.Get('headerText', self.default_headerText)
        self.mainContainerPadding = attributes.Get('insidePadding', self.default_inside_padding)
        self.frame = None
        self._ConstructLayout()
        self.TurnOnBypassToMainCont()

    def _ConstructLayout(self):
        self._ConstructCaption()
        self._ConstructMainCont()
        self._ConstructFrame()
        self.fill = None

    def _ConstructCaption(self):
        self.caption = EveHeaderMedium(parent=self, align=uiconst.TOTOP, text=self.headerText, padBottom=2)

    def _ConstructMainCont(self):
        self.mainCont = ContainerAutoSize(name='mainCont', parent=self, align=uiconst.TOTOP, padding=self.mainContainerPadding, alignMode=self.alignMode)

    def _ConstructFrame(self):
        self.frame = Frame(bgParent=self, texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Stroke.png', cornerSize=9, color=COLOR_SUBSECTION_FRAME, padTop=self.default_framePadTop)

    def CheckConstructFill(self):
        if not self.fill:
            self.fill = Frame(bgParent=self, texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png', cornerSize=9, padding=(6, 24, 6, 6), color=(1.0, 1.0, 1.0, 0.5))

    def SetText(self, text):
        self.caption.SetText(text)

    def Blink(self, color):
        self.CheckConstructFill()
        self.fill.Show()
        if self.frame:
            self.frame.SetRGBA(*color)
            animations.FadeTo(self.frame, 0.2, 1.0, duration=1.5, curveType=uiconst.ANIM_WAVE, loops=uiconst.ANIM_REPEAT)
        self.fill.SetRGBA(*self._GetFillColor(color))
        animations.FadeTo(self.fill, 0.1, 0.15, duration=1.5, curveType=uiconst.ANIM_WAVE, loops=uiconst.ANIM_REPEAT)

    @staticmethod
    def _GetFillColor(color):
        return Color(*color).SetOpacity(0.15).GetRGBA()

    def StopBlink(self):
        if self.frame:
            self.frame.StopAnimations()
            self.frame.SetRGBA(*COLOR_SUBSECTION_FRAME)
        if self.fill:
            self.fill.StopAnimations()
            self.fill.opacity = 0.0

    def SetColor(self, color):
        self._SetFrameColor(color)
        if self.fill:
            self._SetFillColor(color)

    def _SetFrameColor(self, color):
        color = Color(*color).SetOpacity(self.frame.opacity).GetRGBA()
        self.frame.SetRGBA(*color)

    def _SetFillColor(self, color):
        color = Color(*color).SetOpacity(self.fill.opacity).GetRGBA()
        self.fill.SetRGBA(*color)


class Header(Container):
    default_name = 'Header'
    default_bgColor = COLOR_HEADER
    default_height = 24

    def ApplyAttributes(self, attributes):
        super(Header, self).ApplyAttributes(attributes)
        text = attributes.text
        Fill(parent=self, align=uiconst.TOLEFT, width=2, color=Color.WHITE, opacity=0.75)
        self.label = EveHeaderMedium(parent=self, align=uiconst.CENTER, text=text)

    def SetText(self, text):
        self.label.SetText(text)
