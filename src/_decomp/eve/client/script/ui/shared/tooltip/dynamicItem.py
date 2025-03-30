#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\tooltip\dynamicItem.py
import dogma.data as dogma_data
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.client.script.ui.shared.dynamicItem.const import COLOR_NEGATIVE, COLOR_POSITIVE
from eve.client.script.ui.shared.info.attribute import Attribute, MutatedAttribute
import dynamicitemattributes as dynamicitems
import math
import evetypes
RES_BAR_FILL = 'res:/UI/Texture/Classes/DynamicItem/arrows.png'

def AddDynamicItemAttributes(panel, itemID, typeID, spacerHeight = None):
    if not dynamicitems.IsDynamicType(typeID):
        return
    if spacerHeight:
        panel.AddSpacer(height=spacerHeight, colSpan=panel.columns)
    container = ContainerAutoSize(align=uiconst.TOTOP, alignMode=uiconst.TOTOP)
    dynamicItem = GetDynamicItem(itemID)
    attributes = GetDynamicAttributes(dynamicItem)
    sortedAttributes = sorted(attributes, key=lambda a: dogma_data.get_attribute_display_name(a.attributeID))
    InputItemsEntry(parent=container, align=uiconst.TOTOP, mutatorTypeID=dynamicItem.mutatorTypeID, sourceTypeID=dynamicItem.sourceTypeID)
    for attribute in sortedAttributes:
        AttributeEntry(parent=container, align=uiconst.TOTOP, top=4, attribute=attribute)

    panel.AddSpacer(width=360, colSpan=panel.columns)
    panel.AddCell(container, colSpan=panel.columns)


def GetDynamicItem(itemID):
    dynamicItemSvc = sm.GetService('dynamicItemSvc')
    return dynamicItemSvc.GetDynamicItem(itemID)


def GetDynamicAttributes(item):
    attributes = []
    for attributeID in item.modifiers.keys():
        attributes.append(GetDynamicAttribute(item, attributeID))

    return attributes


def GetDynamicAttribute(item, attributeID):
    static = sm.GetService('clientDogmaStaticSvc')
    base = static.GetTypeAttribute(item.sourceTypeID, attributeID)
    mutatorAttributes = dynamicitems.GetMutatorAttributes(item.mutatorTypeID)
    bonusLow = mutatorAttributes[attributeID].min
    bonusHigh = mutatorAttributes[attributeID].max
    highIsGood = getattr(mutatorAttributes[attributeID], 'highIsGood', None)
    value = item.attributes[attributeID]
    return MutatedAttribute(attribute=Attribute(attributeID, value), sourceValue=base, minValue=base * bonusLow, maxValue=base * bonusHigh, highIsGood=highIsGood)


class InputItemsEntry(Container):
    default_height = 64

    def ApplyAttributes(self, attributes):
        super(InputItemsEntry, self).ApplyAttributes(attributes)
        self.mutatorTypeID = attributes.mutatorTypeID
        self.sourceTypeID = attributes.sourceTypeID
        self.Layout()

    def Layout(self):
        FillThemeColored(bgParent=self, colorType=uiconst.COLORTYPE_UIHILIGHT)
        InputItemEntry(parent=self, align=uiconst.TOTOP, typeID=self.mutatorTypeID)
        InputItemEntry(parent=self, align=uiconst.TOTOP, typeID=self.sourceTypeID)


class InputItemEntry(Container):
    default_height = 32

    def ApplyAttributes(self, attributes):
        super(InputItemEntry, self).ApplyAttributes(attributes)
        self.typeID = attributes.typeID
        self.Layout()

    def Layout(self):
        iconCont = Container(parent=self, align=uiconst.TOLEFT, width=32)
        ItemIcon(parent=iconCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=24, height=24, typeID=self.typeID)
        eveLabel.EveLabelSmall(parent=self, align=uiconst.TOTOP, top=4, text=evetypes.GetName(self.typeID), opacity=0.6)


class AttributeEntry(Container):
    default_state = uiconst.UI_DISABLED
    default_height = 34

    def ApplyAttributes(self, attributes):
        super(AttributeEntry, self).ApplyAttributes(attributes)
        self.attribute = attributes.attribute
        self.Layout()

    def Layout(self):
        FillThemeColored(bgParent=self, colorType=uiconst.COLORTYPE_UIHILIGHT)
        iconCont = Container(parent=self, align=uiconst.TOLEFT, width=32)
        Icon(parent=iconCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, size=24, icon=self.attribute.iconID)
        labelName = eveLabel.EveLabelSmall(parent=self, align=uiconst.TOTOP, top=2, maxLines=1, text=dogma_data.get_attribute_display_name(self.attribute.attributeID), opacity=0.6)
        labelName.SetRightAlphaFade(fadeEnd=300, maxFadeWidth=200)
        FinalAttributeValueLabel(parent=self, align=uiconst.TOTOP_NOPUSH, height=14, attribute=self.attribute)
        MutationBar(parent=self, align=uiconst.TOBOTTOM, idx=0, attribute=self.attribute)


class FinalAttributeValueLabel(Container):
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        super(FinalAttributeValueLabel, self).ApplyAttributes(attributes)
        self.attribute = attributes.attribute
        self.Layout()

    def Layout(self):
        self.valueLabel = eveLabel.EveLabelSmall(parent=self, align=uiconst.BOTTOMLEFT, text=self.attribute.displayValue, autoFitToText=True)
        self.diffLabel = eveLabel.EveLabelSmall(parent=self, align=uiconst.BOTTOMLEFT)
        self.UpdateDiff()

    def UpdateDiff(self):
        diff = self.attribute.value - self.attribute.sourceValue
        diffStr = self.attribute.FormatDiff(diff)
        if self.attribute.isMutationPositive:
            color = Color(*COLOR_POSITIVE).GetHex()
        else:
            color = Color(*COLOR_NEGATIVE).GetHex()
        text = u'<color={color}>({diff})</color>'.format(color=color, diff=diffStr)
        self.diffLabel.SetText(text)
        self.diffLabel.left = self.valueLabel.textwidth + 8


class MutationBar(Container):
    default_height = 4
    default_clipChildren = False

    def ApplyAttributes(self, attributes):
        super(MutationBar, self).ApplyAttributes(attributes)
        self.attribute = attributes.attribute
        self.Layout()
        self.UpdateBar()

    def Layout(self):
        FillThemeColored(bgParent=self, colorType=uiconst.COLORTYPE_UIHILIGHT)
        self.barPin = Container(parent=self, align=uiconst.TOPLEFT_PROP, left=0.5, height=1.0, width=1.0)
        Fill(parent=self.barPin, align=uiconst.TOPLEFT, height=self.height, width=1, color=(0.7, 0.7, 0.7, 1.0))
        self.barFill = Sprite(parent=self, align=uiconst.TOLEFT_PROP, left=0.5, width=0.0, texturePath=RES_BAR_FILL, tileX=True)

    def UpdateBar(self):
        attribute = self.attribute
        trueSource = max(attribute.sourceValue, attribute.mutationMin)
        if attribute.isMutationPositive:
            self.barFill.align = uiconst.TOLEFT_PROP
            self.barFill.SetRGB(*COLOR_POSITIVE)
            self.barFill.rotation = 0.0
            rangeWidth = abs(attribute.mutationHigh - trueSource)
        else:
            self.barFill.align = uiconst.TORIGHT_PROP
            self.barFill.SetRGB(*COLOR_NEGATIVE)
            self.barFill.rotation = math.pi
            rangeWidth = abs(attribute.mutationLow - trueSource)
        if rangeWidth > 0.0:
            width = abs(attribute.value - trueSource) / rangeWidth
        else:
            width = 0.0
        sign = 1.0 if attribute.isMutationPositive else -1.0
        self.barPin.left = 0.5 + sign * (width / 2.0)
        self.barFill.width = width / 2.0
