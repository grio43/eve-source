#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\entries\label_text.py
import blue
from carbon.common.script.sys.serviceConst import ROLE_GML
from carbonui import fontconst, uiconst
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.container import Container
from eve.client.script.ui.control.entries.text import Text
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelSmall, EveLabelSmallBold
from eve.client.script.ui.control.infoIcon import InfoIcon, MoreInfoIcon
from eve.client.script.ui.shared.info.infoUtil import GetColoredText, PrepareInfoTextForAttributeHint
from eve.client.script.ui.util import uix

class LabelText(SE_BaseClassCore):
    __guid__ = 'listentry.LabelText'

    def Startup(self, args):
        self.sr.label = EveLabelSmall(text='', parent=self, left=8, top=4, state=uiconst.UI_DISABLED, bold=True)
        self.sr.text = EveLabelMedium(text='', parent=self, left=0, top=4, align=uiconst.TOALL, state=uiconst.UI_DISABLED)

    def Load(self, node):
        self.sr.node = node
        self.sr.label.text = self.name = self.sr.node.label
        self.sr.text.left = int(self.sr.node.Get('textpos', 128)) + 4
        self.sr.text.text = self.sr.node.text
        if self.sr.node.Get('labelAdjust', 0):
            self.sr.label.width = self.sr.node.Get('labelAdjust', 0)

    def GetHeight(self, *args):
        node, width = args
        textpos = min(256, int(node.Get('textpos', 128)))
        height = uix.GetTextHeight(node.label, fontsize=fontconst.EVE_SMALL_FONTSIZE, width=textpos + 8, hspace=0, linespace=12)
        maxDescWidth = None
        if node.Get('scaleWithDesc', True):
            maxDescWidth = width - textpos
        height = max(height, uix.GetTextHeight(node.text, fontsize=fontconst.EVE_MEDIUM_FONTSIZE, width=maxDescWidth, hspace=0, linespace=12) + 2)
        node.height = max(19, height + 4)
        return node.height


class LabelTextTop(Text):
    __guid__ = 'listentry.LabelTextTop'
    default_showHilite = True

    def Startup(self, *args):
        self.sr.infoicon = InfoIcon(left=2, parent=self, idx=0, align=uiconst.CENTERRIGHT)
        self.sr.infoicon.OnClick = self.ShowInfo
        self.sr.icon = Icon(parent=self, pos=(1, 2, 24, 24), align=uiconst.TOPLEFT, idx=0, ignoreSize=True)
        self.sr.label = EveLabelSmall(text='', parent=self, left=8, top=2, state=uiconst.UI_DISABLED)
        self.textClipper = Container(parent=self)
        self.sr.text = EveLabelMedium(parent=self.textClipper, left=8, top=12, state=uiconst.UI_DISABLED, maxLines=1, align=uiconst.TOPLEFT, autoFadeSides=32)

    def Load(self, node):
        Text.Load(self, node)
        if self.sr.infoicon.display:
            self.textClipper.padRight = 20
        else:
            self.textClipper.padRight = 0
        self.sr.label.text = self.sr.node.label
        self.sr.label.left = self.sr.text.left
        self.sr.text.top = self.sr.label.top + self.sr.label.textheight

    def GetHeight(self, *args):
        node, width = args
        labelheight = uix.GetTextHeight(node.label, fontsize=fontconst.EVE_SMALL_FONTSIZE, maxLines=1, uppercase=1)
        textheight = uix.GetTextHeight(node.text, fontsize=fontconst.EVE_MEDIUM_FONTSIZE, maxLines=1)
        node.height = 2 + labelheight + textheight
        return node.height

    @classmethod
    def GetCopyData(cls, node):
        return '%s\t%s' % (node.label, unicode(node.text))


class LabelTextSides(Text):
    __guid__ = 'listentry.LabelTextSides'
    default_showHilite = True

    def Startup(self, *args):
        Text.Startup(self, args)
        self.sr.label = EveLabelMedium(text='', parent=self, left=8, top=0, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT)
        self.sr.text.SetAlign(uiconst.CENTERRIGHT)
        self.sr.text.top = 0
        self.sr.infoicon.SetAlign(uiconst.CENTERRIGHT)
        self.sr.infoicon.top = 0
        self.sr.infoicon.left = 6

    def Load(self, node):
        Text.Load(self, node)
        self.sr.label.text = self.sr.node.label
        if self.sr.infoicon.display:
            self.sr.text.left = 26
        else:
            self.sr.text.left = 8
        self.sr.text.top = 0
        if not self.sr.icon.display and node.get('iconID', None) is None:
            self.sr.label.left = 8
        else:
            self.sr.label.left = self.sr.icon.width + 4

    def GetHeight(self, *args):
        node, width = args
        node.height = 30
        return 30

    def _OnSizeChange_NoBlock(self, newWidth, newHeight):
        textWidth = self.sr.text.textwidth
        availableTextWidth = newWidth - textWidth - self.sr.label.left - 10
        self.sr.label.SetRightAlphaFade(fadeEnd=availableTextWidth, maxFadeWidth=20)

    @classmethod
    def GetCopyData(cls, node):
        return '%s\t%s' % (node.label, unicode(node.text))


class LabelTextSidesAttributes(LabelTextSides):
    __guid__ = 'listentry.LabelTextSidesAttributes'

    def Load(self, node):
        LabelTextSides.Load(self, node)
        modifiedAttribute = node.modifiedAttribute
        if modifiedAttribute:
            coloredText = GetColoredText(modifiedAttribute, text=self.sr.text.text)
            self.sr.text.text = coloredText
            PrepareInfoTextForAttributeHint(self.sr.text, modifiedAttribute, node.itemID, node.extraModifyingAttrIDs, node.extraModifyingFactors)

    def GetMenu(self):
        m = []
        if session.role & ROLE_GML > 0:
            node = self.sr.node
            m.append(('GM - attributeID: %s' % node.attributeID, blue.pyos.SetClipboardData, (str(node.attributeID),)))
        m += LabelTextSides.GetMenu(self)
        return m


class LabelTextSidesMoreInfo(LabelTextSides):
    __guid__ = 'listentry.LabelTextSidesMoreInfo'
    default_showHilite = True

    def Startup(self, *args):
        LabelTextSides.Startup(self, args)
        self.sr.moreinfoicon = MoreInfoIcon(left=2, parent=self, idx=0, align=uiconst.CENTERRIGHT)
        self.sr.moreinfoicon.SetAlign(uiconst.CENTERRIGHT)
        self.sr.moreinfoicon.top = 0
        self.sr.moreinfoicon.left = 6
        self.sr.infoicon.display = False

    def Load(self, node):
        LabelTextSides.Load(self, node)
        self.sr.text.left = 26
        self.sr.moreinfoicon.hint = node.get('moreInfoHint', '')


class LabelMultilineTextTop(LabelTextSides):
    __guid__ = 'listentry.LabelMultilineTextTop'

    def Startup(self, *args):
        LabelTextSides.Startup(self, args)
        self.sr.label.SetAlign(uiconst.TOPLEFT)
        self.sr.label.top = 10
        self.sr.text.maxLines = None
        self.rightTextCont = []

    def Load(self, node):
        LabelTextSides.Load(self, node)
        self.sr.text.display = False
        rightTextLabels = node.rightTextLabels
        for i, (txt, hint) in enumerate(rightTextLabels):
            if i < len(self.rightTextCont):
                cont = self.rightTextCont[i]
                txtLabel = cont.txtLabel
            else:
                cont = Container(parent=self, align=uiconst.TOTOP)
                txtLabel = EveLabelMedium(text='', parent=cont, left=8, top=0, state=uiconst.UI_DISABLED, maxLines=1, align=uiconst.TOPRIGHT)
                cont.txtLabel = txtLabel
                self.rightTextCont.append(cont)
            if i == 0:
                cont.top = 10
            txtLabel.text = txt
            txtLabel.hint = hint or ''
            txtLabel.state = uiconst.UI_NORMAL if hint else uiconst.UI_DISABLED
            cont.display = True
            cont.height = uix.GetTextHeight(txt, fontsize=fontconst.EVE_MEDIUM_FONTSIZE)

        for cont in self.rightTextCont[len(rightTextLabels):]:
            cont.display = False

    def GetHeight(self, *args):
        node, width = args
        labelheight = uix.GetTextHeight(node.label, fontsize=fontconst.EVE_SMALL_FONTSIZE, maxLines=1, uppercase=1)
        rightTextLabels = node.rightTextLabels
        firstTxt = rightTextLabels[0][0] if rightTextLabels else ''
        textheight = uix.GetTextHeight(firstTxt, fontsize=fontconst.EVE_MEDIUM_FONTSIZE, maxLines=None)
        node.height = 2 + labelheight + textheight * len(rightTextLabels)
        return node.height

    @classmethod
    def GetCopyData(cls, node):
        rightTxt = '\n\t'.join([ x[0] for x in node.rightTextLabels ])
        return '%s\t%s' % (node.label, rightTxt)


class IconLabelText(SE_BaseClassCore):
    __guid__ = 'listentry.IconLabelText'
    ICON_POS_REPLACES_LABEL = 0
    ICON_POS_REPLACES_TEXT = 1
    ICON_POS_IN_FRONT_OF_LABEL = 2
    ICON_POS_BEHIND_LABEL = 3
    ICON_POS_IN_FRONT_OF_TEXT = 4
    ICON_POS_BEHIND_TEXT = 5
    ICON_POS_NO_ICON = 6
    iconSize = 16
    margin = 4
    defaultTextWidth = 128

    def Startup(self, args):
        self.sr.label = EveLabelSmallBold(text='', parent=self, left=8, top=4, state=uiconst.UI_DISABLED)
        self.sr.text = EveLabelSmall(text='', parent=self, left=0, top=4, align=uiconst.TOALL, state=uiconst.UI_DISABLED)

    def Load(self, node):
        self.sr.node = node
        iconPositioning = self.sr.node.Get('iconPositioning', IconLabelText.ICON_POS_IN_FRONT_OF_LABEL)
        self.iconID = self.sr.node.Get('icon', None)
        if self.iconID is None:
            iconPositioning = IconLabelText.ICON_POS_NO_ICON
        hasLabel = True
        hasText = True
        if iconPositioning == IconLabelText.ICON_POS_REPLACES_LABEL:
            hasLabel = False
            textOffset = self.margin
            self.InsertIcon(textOffset)
        elif iconPositioning == IconLabelText.ICON_POS_REPLACES_TEXT:
            hasText = False
            textOffset = int(self.sr.node.Get('textpos', self.defaultTextWidth)) + self.margin
            self.InsertIcon(textOffset)
        elif iconPositioning == IconLabelText.ICON_POS_IN_FRONT_OF_LABEL:
            textOffset = self.margin
            self.InsertIcon(textOffset)
            textOffset += self.sr.icon.width
            self.sr.label.left = textOffset + self.margin
        elif iconPositioning == IconLabelText.ICON_POS_IN_FRONT_OF_TEXT:
            textOffset = self.margin + self.sr.text.left
            self.InsertIcon(textOffset)
            textOffset += self.sr.icon.width
            self.sr.text.left = textOffset + self.margin
        if hasLabel:
            self.sr.label.text = self.name = self.sr.node.label
            if self.sr.node.Get('labelAdjust', 0):
                self.sr.label.width = self.sr.node.Get('labelAdjust', 0)
        if hasText:
            self.sr.text.left = int(self.sr.node.Get('textpos', self.defaultTextWidth)) + self.margin
            self.sr.text.text = self.sr.node.text
        if iconPositioning == IconLabelText.ICON_POS_BEHIND_LABEL:
            textOffset = self.margin + self.sr.label.left + self.sr.label.width
            self.InsertIcon(textOffset)
        elif iconPositioning == IconLabelText.ICON_POS_BEHIND_TEXT:
            textOffset = self.margin + self.sr.text.left + self.sr.text.width
            self.InsertIcon(textOffset)

    def InsertIcon(self, offset):
        self.sr.icon = Icon(icon=self.iconID, parent=self, pos=(offset,
         1,
         self.iconSize,
         self.iconSize), align=uiconst.TOPLEFT, idx=0)

    def GetHeight(self, *args):
        node, width = args
        height = IconLabelText.GetDynamicHeight(node, width)
        node.height = height
        return height

    @staticmethod
    def GetDynamicHeight(node, width):
        textpos = node.Get('textpos', 128)
        labelWidth, labelHeight = EveLabelSmallBold.MeasureTextSize(node.label, width=width)
        descWidth, descHeight = EveLabelSmall.MeasureTextSize(node.text, width=width - textpos)
        height = max(19, labelHeight, descHeight)
        return height + 8
