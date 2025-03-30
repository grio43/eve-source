#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uihighlighting\ui\uipointertext.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelLarge, EveLabelMedium
from trinity import TR2_SBM_BLEND
import uihighlighting.ui.uiconst as highlightConst

class PointerTextContainer(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        text = attributes.get('text', '')
        title = attributes.get('title', '')
        self.texturePath = attributes.get('texturePath', None)
        self.iconSize = attributes.get('iconSize', 24)
        self.iconColor = attributes.get('iconColor', None)
        hasTitle = title and not title.isspace()
        if hasTitle:
            self._AddTitle(title)
            self._AddTitleLine()
        self.CreatePointerTextContainer()
        if self.texturePath:
            self._AddTextWithIcon(text)
        else:
            self._AddText(text)
        self._CorrectHeight(hasTitle)

    def _AddTitle(self, title):
        self.pointerTitleContainer = Container(parent=self, align=uiconst.TOTOP, name='pointerTitleContainer', width=self.width, height=0)
        pointerTitle = EveLabelLarge(text=title, parent=self.pointerTitleContainer, align=uiconst.CENTER, width=self.pointerTitleContainer.width, state=uiconst.UI_DISABLED, idx=0, opacity=highlightConst.TITLE_OPACITY, blendMode=TR2_SBM_BLEND, color=highlightConst.TITLE_COLOR)
        self._AdaptContainerHeightToLabel(self.pointerTitleContainer, pointerTitle)

    def _AddTitleLine(self):
        self.pointerTitleLineContainer = Container(parent=self, align=uiconst.TOTOP, name='pointerTitleLineContainer', width=self.width, height=2 * highlightConst.TITLE_LINE_VERTICAL_PADDING)
        pointerTitleLine = Line(name='pointerTitleLine', parent=self.pointerTitleLineContainer, align=uiconst.TOTOP, weight=highlightConst.TITLE_LINE_HEIGHT, opacity=highlightConst.TITLE_LINE_OPACITY, padTop=highlightConst.TITLE_LINE_VERTICAL_PADDING, padBottom=highlightConst.TITLE_LINE_VERTICAL_PADDING, color=highlightConst.TITLE_LINE_COLOR)
        self._AdaptContainerHeightToLine(self.pointerTitleLineContainer, pointerTitleLine)

    def CreatePointerTextContainer(self):
        self.pointerTextContainer = Container(parent=self, align=uiconst.TOTOP, name='pointerTextContainer', width=self.width, height=0)

    def _AddText(self, text):
        self.pointerText = EveLabelMedium(text=text, parent=self.pointerTextContainer, align=uiconst.CENTER, left=2, top=4, width=self.pointerTextContainer.width - 4, state=uiconst.UI_DISABLED, idx=0, opacity=highlightConst.TEXT_OPACITY)
        self._AdaptContainerHeightToLabel(self.pointerTextContainer, self.pointerText)

    def _AddTextWithIcon(self, text):
        Sprite(name='icon', parent=Container(parent=self.pointerTextContainer, width=self.iconSize, height=self.iconSize, align=uiconst.TOLEFT), texturePath=self.texturePath, width=self.iconSize, height=self.iconSize, align=uiconst.CENTERTOP, color=self.iconColor)
        self.pointerText = EveLabelMedium(text=text, parent=self.pointerTextContainer, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, opacity=highlightConst.TEXT_OPACITY, left=4)
        self._AdaptContainerHeightToLabel(self.pointerTextContainer, self.pointerText)

    def _CorrectHeight(self, hasTitle):
        self.height = max(self.pointerTextContainer.height, self.iconSize)
        if hasTitle:
            self.height = self.height + self.pointerTitleContainer.height + self.pointerTitleLineContainer.height

    def _AdaptContainerHeightToLabel(self, container, label):
        w, h = label.GetAbsoluteSize()
        container.height = container.height + h

    def _AdaptContainerHeightToLine(self, container, line):
        container.height = container.height + line.height
