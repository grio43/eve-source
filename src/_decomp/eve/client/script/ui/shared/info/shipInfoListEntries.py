#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\shipInfoListEntries.py
import blue
import utillib
import evetypes
import eveicon
from carbon.common.script.sys.serviceConst import ROLE_QA
from carbonui.util.color import Color
from carbonui.control.dragdrop.dragdata import ItemDragData
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.shared.info.infoUtil import GetColoredText, LoadAttributeTooltipPanel, GetAttributeTooltipTitleAndDescription
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipHeaderDescriptionWrapper
from carbonui import uiconst, Align, TextBody, TextColor
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveWindowUnderlay import ListEntryUnderlay
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.control.itemIcon import ItemIcon

class _ListEntryBase(Container):
    default_height = 30
    default_state = uiconst.UI_NORMAL
    default_align = Align.TOTOP
    default_padBottom = 2

    def __init__(self, indent = 0, **kw):
        self.indent = indent
        super(_ListEntryBase, self).__init__(**kw)

    def ApplyAttributes(self, attributes):
        self._hiliteFill = None
        super(_ListEntryBase, self).ApplyAttributes(attributes)
        self.construct_layout()

    def construct_layout(self):
        self.content = Container(name='content', parent=self, align=Align.TOALL, padLeft=self.indent)

    def ConstructHiliteFill(self):
        if not self._hiliteFill:
            self._hiliteFill = ListEntryUnderlay(name='selectionHighlight', bgParent=self)

    def ShowHilite(self, animate = True):
        self.ConstructHiliteFill()
        self._hiliteFill.set_hovered(True, animate)

    def HideHilite(self, animate = True):
        if self._hiliteFill:
            self._hiliteFill.set_hovered(False, animate)

    def OnMouseEnter(self, *args):
        self.ShowHilite()

    def OnMouseExit(self, *args):
        self.HideHilite()

    def GetTooltipPointer(self):
        if self.tooltipPanelClassInfo:
            return getattr(self.tooltipPanelClassInfo, 'tooltipPointer', None)
        return uiconst.POINT_RIGHT_2


class ListEntry(_ListEntryBase):

    def __init__(self, label = None, text = None, texturePath = None, indent = 0, **kw):
        self.label = label
        self.text = text
        self.texturePath = texturePath
        super(ListEntry, self).__init__(indent, **kw)

    def ApplyAttributes(self, attributes):
        self.icon = None
        self.valueLabel = None
        self.nameLabel = None
        super(ListEntry, self).ApplyAttributes(attributes)

    def construct_layout(self):
        super(ListEntry, self).construct_layout()
        self._construct_icon()
        self._construct_labels()

    def _construct_icon(self):
        if not self.texturePath:
            return
        iconCont = Container(name='iconCont', parent=self.content, align=Align.TOLEFT, width=24, padLeft=4, state=uiconst.UI_DISABLED)
        self.icon = Sprite(name='icon', parent=iconCont, align=Align.CENTERLEFT, texturePath=self.texturePath, width=24, height=24, state=uiconst.UI_DISABLED)

    def _construct_labels(self):
        mainCont = Container(name='mainCont', parent=self.content, align=Align.TOALL)
        self._construct_value_label(mainCont)
        self._construct_name_label(mainCont)

    def _construct_value_label(self, parent):
        if not self.text:
            return
        valueCont = ContainerAutoSize(name='valueCont', parent=parent, align=Align.TORIGHT, state=uiconst.UI_PICKCHILDREN)
        self.valueLabel = TextBody(name='value', parent=valueCont, align=Align.CENTERRIGHT, text=self.text, state=uiconst.UI_NORMAL, padRight=8)

    def _construct_name_label(self, parent):
        if not self.label:
            return
        labelCont = Container(name='labelCont', parent=parent, align=Align.TOALL, clipChildren=True)
        self.nameLabel = TextBody(name='label', parent=labelCont, align=Align.CENTERLEFT, text=self.label, padLeft=4, state=uiconst.UI_DISABLED, autoFadeSides=16)


class ListEntryEveType(_ListEntryBase):
    isDragObject = True

    def __init__(self, typeID, itemID = None, abstractinfo = None, text = None, indent = 0, **kw):
        self._typeID = typeID
        self._itemID = itemID
        self._abstractinfo = abstractinfo or utillib.KeyVal()
        self._text = text
        super(ListEntryEveType, self).__init__(indent, **kw)

    def ApplyAttributes(self, attributes):
        self.typeID = attributes.get('typeID', None)
        self.itemID = attributes.get('itemID', None)
        self.abstractInfo = attributes.get('abstractinfo', None)
        super(ListEntryEveType, self).ApplyAttributes(attributes)

    def construct_layout(self):
        super(ListEntryEveType, self).construct_layout()
        self._construct_icon()
        self._construct_info_icon()
        self._construct_label()

    def _construct_icon(self):
        container = Container(name='icon_container', parent=self.content, align=Align.TOLEFT, width=24, state=uiconst.UI_PICKCHILDREN)
        ItemIcon(parent=container, align=Align.CENTER, width=24, height=24, typeID=self._typeID, itemID=self._itemID, bpData=self._abstractinfo.get('bpData', None), isCopy=self._abstractinfo.get('isCopy', False))

    def _construct_info_icon(self):
        info_container = Container(name='info_container', parent=self.content, align=Align.TORIGHT, width=16, padRight=8, padLeft=4)
        info_icon = InfoIcon(parent=info_container, align=Align.CENTER, texturePath=eveicon.info, color=TextColor.SECONDARY)
        info_icon.OnClick = self.OnDblClick

    def _construct_label(self):
        container = Container(name='label_container', parent=self.content, align=Align.TOALL, clipChildren=True)
        TextBody(name='label', parent=container, align=Align.CENTERLEFT, text=self._text or evetypes.GetName(self._typeID), padLeft=4, state=uiconst.UI_DISABLED, autoFadeSides=16)

    def GetMenu(self):
        return sm.GetService('menu').GetMenuFromItemIDTypeID(self._itemID, self._typeID, abstractInfo=self._abstractinfo, includeMarketDetails=True)

    def GetDragData(self):
        return ItemDragData(itemID=self._itemID, typeID=self._typeID, isBlueprintCopy=self._abstractinfo.get('isCopy', False))

    def OnDblClick(self, *args, **kwargs):
        self._show_info()

    def _show_info(self):
        sm.GetService('info').ShowInfo(typeID=self._typeID, itemID=self._itemID, abstractinfo=self._abstractinfo)


class ListEntryAttribute(ListEntry):

    def __init__(self, label, text, texturePath, itemID, attributeID, modifiedAttribute = None, indent = 0, **kw):
        self.itemID = itemID
        self.attributeID = attributeID
        self.modifiedAttribute = modifiedAttribute
        self.extraModifyingAttrIDs = []
        self.extraModifyingFactors = []
        super(ListEntryAttribute, self).__init__(label=label, text=GetColoredText(modifiedAttribute, text), texturePath=texturePath, indent=indent, **kw)

    def construct_layout(self):
        super(ListEntryAttribute, self).construct_layout()
        if self.valueLabel:
            self.valueLabel.LoadTooltipPanel = lambda tooltipPanel, *args: LoadAttributeTooltipPanel(tooltipPanel, self)
        tooltipTitleText, tooltipDescriptionText = GetAttributeTooltipTitleAndDescription(self.attributeID)
        if tooltipTitleText:
            self.tooltipPanelClassInfo = TooltipHeaderDescriptionWrapper(header=tooltipTitleText, description=tooltipDescriptionText, tooltipPointer=uiconst.POINT_RIGHT_2)

    def GetMenu(self):
        ret = self.valueLabel.GetMenu()
        if session.role & ROLE_QA:
            ret.append(('QA - attributeID: %s' % self.attributeID, blue.pyos.SetClipboardData, (str(self.attributeID),)))
        return ret


class ListEntryTypeAttribute(ListEntryAttribute):

    def __init__(self, label, text, texturePath, itemID, attributeID, typeID, modifiedAttribute = None, indent = 0, **kw):
        self._typeID = typeID
        super(ListEntryTypeAttribute, self).__init__(label, text, texturePath, itemID, attributeID, modifiedAttribute, indent, **kw)

    def construct_layout(self):
        super(ListEntryTypeAttribute, self).construct_layout()
        self.valueLabel.SetState(uiconst.UI_DISABLED)

    def _construct_value_label(self, parent):
        self._construct_info_icon(parent)
        super(ListEntryTypeAttribute, self)._construct_value_label(parent)

    def _construct_info_icon(self, parent):
        info_container = Container(name='info_container', parent=parent, align=Align.TORIGHT, width=16, padRight=8, padLeft=0)
        info_icon = InfoIcon(parent=info_container, align=Align.CENTER, texturePath=eveicon.info, color=TextColor.SECONDARY)
        info_icon.OnClick = self.OnDblClick

    def OnDblClick(self, *args, **kwargs):
        self._show_info()

    def _show_info(self):
        sm.GetService('info').ShowInfo(typeID=self._typeID)

    def GetMenu(self):
        ret = sm.GetService('menu').GetMenuFromItemIDTypeID(itemID=None, typeID=self._typeID, abstractInfo=None, includeMarketDetails=True)
        for e in super(ListEntryTypeAttribute, self).GetMenu():
            ret.append(e)

        return ret


class ListEntryStatusBarAttribute(ListEntryAttribute):
    default_color = Color.GRAY

    def ApplyAttributes(self, attributes):
        self.color = attributes.get('color', self.default_color)
        self.value = attributes.get('value', 0.0)
        super(ListEntryStatusBarAttribute, self).ApplyAttributes(attributes)

    def construct_layout(self):
        super(ListEntryStatusBarAttribute, self).construct_layout()
        self.gauge = Gauge(parent=self, gaugeHeight=self.default_height - 1, align=Align.TOTOP, top=0, padding=(1, 0, 1, 0), state=uiconst.UI_DISABLED, value=self.value, color=self.color, glow=False)
