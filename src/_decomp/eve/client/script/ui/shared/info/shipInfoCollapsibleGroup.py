#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\shipInfoCollapsibleGroup.py
import eveformat
import eveicon
import localization
from carbonui import Align, uiconst, TextBody, TextColor, TextDetail
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from dogma.attributes.format import GetFormattedAttributeAndValue
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveWindowUnderlay import ListEntryUnderlay
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.shared.info.infoUtil import GetColoredText, LoadAttributeTooltipPanel

class _CollapsibleGroupBase(ContainerAutoSize):
    default_state = uiconst.UI_NORMAL
    default_headerColor = (1, 1, 1, 0.05)
    default_expanderAlign = Align.TORIGHT
    default_expanderWidth = 32
    default_expanderPadding = (0, 0, 0, 0)

    def ApplyAttributes(self, attributes):
        self._hiliteFill = None
        self.default_state = uiconst.UI_NORMAL
        super(_CollapsibleGroupBase, self).ApplyAttributes(attributes)
        self.headerColor = attributes.get('headerColor', self.default_headerColor)
        self.expanderAlign = attributes.get('expanderAlign', self.default_expanderAlign)
        self.expanderWidth = attributes.get('expanderWidth', self.default_expanderWidth)
        self.expanderPadding = attributes.get('expanderPadding', self.default_expanderPadding)
        self._construct_layout()

    def _construct_layout(self):
        self._construct_header()
        self._construct_main_cont()

    def _construct_header(self):
        self.bgCont = ContainerAutoSize(name='bgCont', parent=self, align=Align.TOTOP)
        self._hiliteFill = ListEntryUnderlay(name='selectionHighlight', bgParent=self.bgCont)
        Fill(name='bgColor', bgParent=self.bgCont, color=self.headerColor)
        self.headerCont = Container(name='headerCont', parent=self.bgCont, align=Align.TOTOP, height=32)
        self.headerCont.OnClick = self.OnClick
        self._construct_expander()

    def _construct_expander(self):
        self.expanderCont = Container(name='expanderCont', parent=self.headerCont, align=self.expanderAlign, width=self.expanderWidth, padding=self.expanderPadding, state=uiconst.UI_PICKCHILDREN)
        self.expanderIcon = ButtonIcon(name='expander', parent=self.expanderCont, align=Align.CENTER, texturePath=eveicon.chevron_up, iconSize=18, func=self.OnClick)

    def _construct_main_cont(self):
        self.mainCont = ContainerAutoSize(name='mainCont', parent=self, align=Align.TOTOP, state=uiconst.UI_PICKCHILDREN, padTop=2)

    def SetCollapsed(self, collapsed):
        if collapsed:
            self.mainCont.Hide()
            self.expanderIcon.SetTexturePath(eveicon.chevron_down)
        else:
            self.mainCont.Show()
            self.expanderIcon.SetTexturePath(eveicon.chevron_up)

    def Toggle(self):
        self.SetCollapsed(self.mainCont.display)

    def OnClick(self, *args):
        super(_CollapsibleGroupBase, self).OnClick(*args)
        self.Toggle()

    def ConstructHiliteFill(self):
        if not self._hiliteFill:
            self._hiliteFill = ListEntryUnderlay(name='selectionHighlight', bgParent=self.bgCont)

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


class CollapsibleGroup(_CollapsibleGroupBase):

    def ApplyAttributes(self, attributes):
        self.groupName = attributes.groupName
        self.iconID = attributes.groupIcon
        self._icon_color = attributes.get('iconColor', TextColor.SECONDARY)
        self._icon_size = attributes.get('iconSize', 16)
        self._bold = attributes.get('bold', True)
        super(CollapsibleGroup, self).ApplyAttributes(attributes)

    def _construct_header(self):
        super(CollapsibleGroup, self)._construct_header()
        self.iconCont = Container(name='iconCont', parent=self.headerCont, align=Align.TOLEFT, width=self._icon_size + 8, state=uiconst.UI_DISABLED)
        self.icon = Sprite(name='icon', parent=self.iconCont, align=Align.CENTERRIGHT, texturePath=self.iconID, width=self._icon_size, height=self._icon_size, state=uiconst.UI_DISABLED, color=self._icon_color)
        self._construct_label()

    def _construct_label(self):
        self.headerLabelWrapper = Container(name='headerLabelWrapper', parent=self.headerCont, align=Align.TOALL, clipChildren=True)
        self.labelCont = ContainerAutoSize(name='labelCont', parent=self.headerLabelWrapper, align=Align.TOLEFT, state=uiconst.UI_DISABLED)
        self.label = TextBody(name='label', parent=self.labelCont, align=Align.CENTERLEFT, text=self.groupName, padLeft=8, state=uiconst.UI_DISABLED, bold=self._bold)

    def OnMouseEnter(self, *args):
        super(CollapsibleGroup, self).OnMouseEnter(*args)
        self.expanderIcon.OnMouseEnter(*args)

    def OnMouseExit(self, *args):
        super(CollapsibleGroup, self).OnMouseExit(*args)
        self.expanderIcon.OnMouseExit(*args)


class CollapsibleGaugeGroup(CollapsibleGroup):

    def ApplyAttributes(self, attributes):
        self.itemID = attributes.itemID
        self.groupedAttributes = attributes.groupedAttributes
        self.damageTypeIcons = attributes.damageTypeIcons
        self.damageTypeColors = attributes.damageTypeColors
        self.ehp_description_path = attributes.ehpDescriptionPath
        self._calculate_effective_hp(attributes.layerHp)
        super(CollapsibleGaugeGroup, self).ApplyAttributes(attributes)

    def _construct_layout(self):
        self._construct_header()
        self._construct_gauges()
        self._construct_main_cont()

    def _construct_label(self):
        self.headerLabelCont = Container(parent=self.headerCont, align=Align.TOALL, clipChildren=True)
        self.labelCont = ContainerAutoSize(name='labelCont', parent=self.headerLabelCont, align=Align.TOLEFT, state=uiconst.UI_DISABLED, clipChildren=True)
        self.label = TextBody(name='label', parent=self.labelCont, align=Align.CENTERLEFT, text=self.groupName, padLeft=8, state=uiconst.UI_DISABLED, bold=True)
        self.ehpCont = ContainerAutoSize(name='ehpCont', parent=self.headerLabelCont, align=Align.TOLEFT, hint='Effective Hit Points', state=uiconst.UI_NORMAL, clipChildren=True)
        self.ehpCont.LoadTooltipPanel = self._load_ehp_tooltip_panel
        self.ehpLabel = TextBody(name='ehp', parent=self.ehpCont, align=Align.CENTERLEFT, text=localization.GetByLabel('UI/InfoWindow/EhpFormat', value=self.effectiveHpString, valueColor=TextColor.NORMAL), padLeft=16, color=TextColor.SECONDARY)

    def _load_ehp_tooltip_panel(self, tooltip_panel, *args):
        tooltip_panel.LoadGeneric1ColumnTemplate()
        tooltip_panel.AddLabelMedium(text=localization.GetByLabel('UI/InfoWindow/EffectiveHpHeader'))
        tooltip_panel.AddLabelSmall(text=localization.GetByLabel(self.ehp_description_path), color=TextColor.SECONDARY, wrapWidth=220)

    def _construct_gauges(self):
        self.gaugeCont = Container(parent=self.bgCont, name='gaugeCont', align=Align.TOTOP, height=34)
        self.highestAttribute = self._get_highest_attribute()
        self.CreateGauge('em', self.gaugeCont)
        self.CreateGauge('thermal', self.gaugeCont)
        self.CreateGauge('kinetic', self.gaugeCont)
        self.CreateGauge('explosive', self.gaugeCont)

    def CreateGauge(self, damageType, parent):
        attribute, modifiedAttribute = self.groupedAttributes[damageType]
        return ResistanceAttributeGauge(name=damageType, parent=parent, align=Align.TOLEFT_PROP, width=0.25, itemID=self.itemID, damageType=damageType, attribute=attribute, modifiedAttribute=modifiedAttribute, damageTypeIcon=self.damageTypeIcons[damageType], damageTypeColor=self.damageTypeColors[damageType], padding=(8, 0, 8, 8), highest=attribute.value == self.highestAttribute.value)

    def _calculate_effective_hp(self, layerHp):
        totalResistance = 0
        for damageType, (attrib, modifiedAttrib) in self.groupedAttributes.iteritems():
            totalResistance += attrib.value

        avgResistance = totalResistance / 4
        layerHp = layerHp
        self.effectiveHp = layerHp / avgResistance
        self.effectiveHpString = localization.formatters.FormatNumeric(self.effectiveHp, decimalPlaces=2, useGrouping=True)

    def _get_highest_attribute(self):
        highestAttrib = None
        for attribute, modifiedAttribute in self.groupedAttributes.itervalues():
            if not highestAttrib:
                highestAttrib = attribute
                continue
            if highestAttrib.value > attribute.value:
                highestAttrib = attribute

        return highestAttrib


class ResistanceAttributeGauge(Container):

    def ApplyAttributes(self, attributes):
        super(ResistanceAttributeGauge, self).ApplyAttributes(attributes)
        self.itemID = attributes.itemID
        self.damageType = attributes.damageType
        self.attribute = attributes.attribute
        self.modifiedAttribute = attributes.modifiedAttribute
        self.extraModifyingAttrIDs = attributes.get('extraModifyingAttrIDs', None)
        self.extraModifyingFactors = attributes.get('extraModifyingFactors', None)
        texturePath = attributes.damageTypeIcon
        color = attributes.damageTypeColor
        highest = attributes.get('highest', False)
        glowBrightness = 0.5 if highest else 0
        self.upperCont = Container(name='mainCont', parent=self, align=Align.TOTOP, height=16, state=uiconst.UI_NORMAL)
        self.gaugeCont = Container(name='gaugeCont', parent=self, align=Align.TOTOP, height=6, state=uiconst.UI_DISABLED, padTop=4)
        self.gauge = Gauge(name='gauge', parent=self.gaugeCont, align=Align.TOTOP, showMarker=False, lineWidth=6, colorBg=eveColor.BLACK, glowBrightness=glowBrightness, color=color, value=1 - self.attribute.value, state=uiconst.UI_DISABLED)
        iconCont = Container(name='iconCont', parent=self.upperCont, align=Align.TOLEFT, width=18, state=uiconst.UI_PICKCHILDREN)
        self.icon = Sprite(name='icon', parent=iconCont, align=Align.CENTER, width=18, height=18, texturePath=texturePath, state=uiconst.UI_DISABLED)
        self.labelCont = ContainerAutoSize(name='labelCont', parent=self.upperCont, align=Align.TOLEFT)
        self.label = TextDetail(name='label', parent=self.labelCont, align=Align.CENTERLEFT, text=GetColoredText(self.modifiedAttribute, self.GetDisplayValue()), state=uiconst.UI_DISABLED, bold=1 if highest else 0)
        self.label.LoadTooltipPanel = lambda tooltipPanel, *args: LoadAttributeTooltipPanel(tooltipPanel, self)
        if self.modifiedAttribute:
            self.label.state = uiconst.UI_NORMAL
        formatInfo = GetFormattedAttributeAndValue(self.attribute.attributeID, self.attribute.value)
        if formatInfo:
            self.upperCont.hint = formatInfo.displayName

    def GetDisplayValue(self):
        return u'{}%'.format(int(round((1.0 - self.attribute.value) * 100)))
