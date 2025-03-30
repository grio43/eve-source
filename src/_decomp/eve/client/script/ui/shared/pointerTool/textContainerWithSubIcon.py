#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\pointerTool\textContainerWithSubIcon.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelLarge
from eve.client.script.ui.util.uix import GetTextHeight
import uihighlighting.ui.uiconst as highlightConst

class PointerContainerWithPath(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.pointerTextContainer = None
        self.pointerTitleContainer = None
        textAndIconObjects = attributes.get('textAndIconObjects', None)
        titleAndIcon = attributes.get('titleAndIcon', None)
        self.iconSize = attributes.get('iconSize', 24)
        if titleAndIcon:
            self._AddTitle(titleAndIcon)
        if titleAndIcon and textAndIconObjects:
            self._AddTitleLine()
        if textAndIconObjects:
            self.CreatePointerTextContainer()
            for i, each in enumerate(textAndIconObjects):
                left = i * each.indentAmount
                self._AddTextAndIcon(left, each, bold=i == len(textAndIconObjects) - 1)

        height = 0
        if self.pointerTextContainer:
            height += self.pointerTextContainer.height
            height += self.pointerTitleLineContainer.height
        if self.pointerTitleContainer:
            height += self.pointerTitleContainer.height
        self.height = max(self.iconSize, height)

    def _AddTitle(self, titleAndTexture):
        self.pointerTitleContainer = Container(parent=self, align=uiconst.TOTOP, name='pointerTitleContainer', width=self.width, height=0)
        cont = Container(parent=self.pointerTitleContainer, align=uiconst.TOTOP, minHeight=self.iconSize, alignMode=uiconst.CENTERLEFT)
        texturePath = titleAndTexture.GetTexturePath()
        iconData = titleAndTexture.GetIconData()
        left = 0
        if texturePath:
            iconSizes = titleAndTexture.GetIconSizes()
            width, height = (self.iconSize, self.iconSize) if iconSizes is None else iconSizes
            sprite = Sprite(name='icon', parent=cont, texturePath=texturePath, width=width, height=height, align=uiconst.CENTERLEFT)
            left += sprite.width + 4
            if iconSizes is None:
                self.SetIconSize(sprite)
        elif iconData:
            maxIconDataSize = max(iconData.sizes)
            iconSize = min(maxIconDataSize, self.iconSize)
            sprite = Sprite(name='icon', parent=cont, texturePath=iconData, width=iconSize, height=iconSize, align=uiconst.CENTERLEFT)
            left += sprite.width + 4
        pointerTitle = EveLabelLarge(text=titleAndTexture.GetText(), parent=cont, align=uiconst.CENTER, width=self.pointerTitleContainer.width, state=uiconst.UI_DISABLED, idx=0, opacity=highlightConst.TITLE_OPACITY, color=highlightConst.TITLE_COLOR, left=left)
        cont.height = GetTextHeight(pointerTitle.text, width=self.pointerTitleContainer.width - pointerTitle.left, fontsize=pointerTitle.fontsize)
        self.pointerTitleContainer.height = cont.height

    def _AddTitleLine(self):
        self.pointerTitleLineContainer = Container(parent=self, align=uiconst.TOTOP, name='pointerTitleLineContainer', width=self.width, height=2 * highlightConst.TITLE_LINE_VERTICAL_PADDING)
        pointerTitleLine = Line(name='pointerTitleLine', parent=self.pointerTitleLineContainer, align=uiconst.TOTOP, weight=highlightConst.TITLE_LINE_HEIGHT, opacity=highlightConst.TITLE_LINE_OPACITY, padTop=highlightConst.TITLE_LINE_VERTICAL_PADDING, padBottom=highlightConst.TITLE_LINE_VERTICAL_PADDING, color=highlightConst.TITLE_LINE_COLOR)

    def CreatePointerTextContainer(self):
        self.pointerTextContainer = ContainerAutoSize(parent=self, align=uiconst.TOTOP, name='pointerTextContainer', width=self.width, height=0, alignMode=uiconst.TOTOP)

    def _AddTextAndIcon(self, contLeft, textAndIconObject, bold = False):
        text = textAndIconObject.GetText()
        texturePath = textAndIconObject.GetTexturePath()
        iconData = textAndIconObject.GetIconData()
        cont = Container(parent=self.pointerTextContainer, align=uiconst.TOTOP, minHeight=self.iconSize, alignMode=uiconst.CENTERLEFT, left=contLeft, padding=(0,
         3,
         contLeft,
         3))
        indentChar = textAndIconObject.GetIndentChar()
        if indentChar:
            identLabel = EveLabelMedium(text=indentChar, parent=cont, align=uiconst.CENTERLEFT)
            indentOffset = identLabel.textwidth
        else:
            indentOffset = 0
        left = indentOffset
        if texturePath:
            iconSizes = textAndIconObject.GetIconSizes()
            width, height = (self.iconSize, self.iconSize) if iconSizes is None else iconSizes
            sprite = Sprite(name='icon', parent=cont, texturePath=texturePath, width=width, height=height, align=uiconst.CENTERLEFT, left=indentOffset + 2)
            if not iconSizes:
                self.SetIconSize(sprite)
            left += sprite.left + sprite.width
        elif iconData:
            maxIconDataSize = max(iconData.sizes)
            iconSize = min(maxIconDataSize, self.iconSize)
            sprite = Sprite(name='icon', parent=cont, texturePath=iconData, width=iconSize, height=iconSize, align=uiconst.CENTERLEFT, left=indentOffset + 2)
            left += sprite.left + sprite.width
        else:
            left += 6
        labelWidth = self.pointerTextContainer.width - contLeft - left
        if bold:
            text = '<b>%s</b>' % text
        pointerText = EveLabelMedium(text=text, parent=cont, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, opacity=highlightConst.TEXT_OPACITY, left=left, width=labelWidth)
        cont.height = max(self.iconSize, GetTextHeight(text, width=labelWidth))
        self.pointerTextContainer.height = self.pointerTextContainer.height + cont.height + cont.padTop + cont.padBottom

    def SetIconSize(self, sprite):
        try:
            textureWidth = sprite.renderObject.texturePrimary.atlasTexture.width
            textureHeight = sprite.renderObject.texturePrimary.atlasTexture.height
            newWidth = min(self.iconSize, max(16, textureWidth))
            newHeight = min(self.iconSize, max(16, textureHeight))
            widthRatio = newWidth / float(textureWidth)
            heightRatio = newHeight / float(textureHeight)
            if widthRatio != heightRatio:
                smallerRatio = min(widthRatio, heightRatio)
                newWidth = int(smallerRatio * textureWidth)
                newHeight = int(smallerRatio * textureHeight)
            sprite.width = int(newWidth)
            sprite.height = int(newHeight)
        except StandardError as e:
            pass
