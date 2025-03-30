#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\itemTrader\outputCont.py
import eveicon
import evetypes
from carbon.common.script.util.format import FmtAmt
from carbonui import TextAlign, TextColor
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.gridcontainer import GridContainer
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.vectorarc import VectorArc
import carbonui
from carbonui.uianimations import animations
import carbonui.const as uiconst
import trinity
from eve.client.script.ui.control.eveLabel import Label
from eveservices.menu import GetMenuService
from localization import GetByLabel
import math
ARC_RADIUS_1 = 145
ARC_RADIUS_2 = 205
ARC_RADIUS_3 = 320
ARC_RADIUS_4 = 520

class ItemTraderOutputCont(Container):

    def ApplyAttributes(self, attributes):
        self.itemTraderController = attributes.itemTraderController
        self.outputByTypeID = {}
        self.moreOutputIcon = None
        super(ItemTraderOutputCont, self).ApplyAttributes(attributes)
        self.contentCont = Container(name='contentCont', parent=self)
        self.decoCont = Container(name='decoCont', parent=self, pickState=carbonui.PickState.OFF)
        self.outputGrid = LayoutGrid(name='outputGrid', parent=self.contentCont, align=uiconst.CENTER, cellSpacing=10)
        self.output_label = carbonui.TextBody(parent=self.contentCont, text=GetByLabel('UI/Inflight/SpaceComponents/ItemTrader/DeliveredItems', itemCount=2), align=uiconst.CENTERTOP, padTop=12, color=TextColor.SECONDARY)
        self.ConstructArcs()

    def ConstructArcs(self):
        tradeIcon = Sprite(name='tradeIcon', parent=self.decoCont, align=uiconst.CENTERLEFT, pos=(-20, 0, 32, 32), texturePath=eveicon.trade, color=TextColor.SECONDARY)
        startAngleDegrees = -172
        endAngleDegrees = 172
        VectorArc(parent=self.decoCont, align=carbonui.Align.CENTER, radius=ARC_RADIUS_1, fill=False, lineWidth=0.5, endAngle=math.radians(endAngleDegrees), startAngle=math.radians(startAngleDegrees))
        VectorArc(parent=self.decoCont, align=carbonui.Align.CENTER, radius=ARC_RADIUS_2, fill=False, lineWidth=0.32, opacity=0.5)
        VectorArc(parent=self.decoCont, align=carbonui.Align.CENTER, radius=ARC_RADIUS_3, fill=False, lineWidth=0.25, opacity=0.5)
        VectorArc(parent=self.decoCont, align=carbonui.Align.CENTER, radius=ARC_RADIUS_4, fill=False, lineWidth=0.2, opacity=0.5)
        VectorArc(name='small_fill_circle', parent=self.decoCont, align=carbonui.Align.CENTER, radius=ARC_RADIUS_1, lineWidth=0, fill=True, color=(0, 0, 0, 0.35))
        VectorArc(name='medium_fill_circle', parent=self.decoCont, align=carbonui.Align.CENTER, radius=ARC_RADIUS_3, lineWidth=0, fill=True, color=(0, 0, 0, 0.2))
        sprite = Sprite(parent=self.decoCont, pos=(0, 0, 440, 440), align=carbonui.Align.CENTER, texturePath='res:/UI/Texture/classes/underConstruction/underConstructionLines.png', textureSecondaryPath='res:/UI/Texture/classes/DynamicItem/bgGlowRing.png', spriteEffect=trinity.TR2_SFX_MODULATE, state=uiconst.UI_DISABLED, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, opacity=0.0)
        Sprite(parent=self.decoCont, pos=(0, 0, 440, 440), align=carbonui.Align.CENTER, texturePath='res:/UI/Texture/classes/underConstruction/underConstructionLines.png', opacity=0.2)
        animations.FadeTo(sprite, startVal=1.0, endVal=2.5, duration=2.6, curveType=uiconst.ANIM_WAVE, loops=uiconst.ANIM_REPEAT)
        animations.MorphVector2(sprite, 'scaleSecondary', startVal=(0.5, 0.5), endVal=(1.0, 1.0), duration=2.6, curveType=uiconst.ANIM_LINEAR, loops=uiconst.ANIM_REPEAT)

    def AddOutputItems(self, outputItemsAndQty):
        self.outputGrid.Flush()
        self.outputGrid.columns = min(len(outputItemsAndQty), 3)
        self.outputByTypeID.clear()
        self.moreOutputIcon = None
        hasMultipleOutputs = len(outputItemsAndQty) > 1
        outputCounter = 0
        outputItemsAndQtyCopy = outputItemsAndQty[:]
        while outputItemsAndQtyCopy and outputCounter < 2:
            typeID, qty = outputItemsAndQtyCopy.pop(0)
            outputCounter += 1
            outputItem = OutputItem(parent=self.outputGrid, typeID=typeID, qty=qty, hasMultipleOutputs=hasMultipleOutputs)
            self.outputByTypeID[typeID] = outputItem

        if outputItemsAndQtyCopy:
            qtyByTypeID = {t:q for t, q in outputItemsAndQtyCopy}
            self.moreOutputIcon = MoreOutputItems(parent=self.outputGrid, qtyByTypeID=qtyByTypeID)

    def UpdateQty(self, typeID, qty):
        outputItem = self.outputByTypeID.get(typeID, None)
        if outputItem:
            outputItem.UpdateQty(qty)
        elif self.moreOutputIcon:
            self.moreOutputIcon.UpdateQty(typeID, qty)


class OutputItem(Container):
    default_height = 80
    default_width = 80
    default_align = uiconst.CENTER

    def ApplyAttributes(self, attributes):
        super(OutputItem, self).ApplyAttributes(attributes)
        self.typeID = attributes.typeID
        hasMultipleOutputs = attributes.hasMultipleOutputs
        qty = attributes.qty
        iconFrame = Sprite(parent=self, pos=(0, 0, 80, 80), align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/underConstruction/iconFrame.png', opacity=0.5)
        self.ConstructIcon()
        self.ConstructLabels(qty, hasMultipleOutputs)

    def ConstructIcon(self):
        output_item_icon = Sprite(name='Item logo', parent=self, align=uiconst.CENTER, height=64, width=64)
        sm.GetService('photo').GetIconByType(output_item_icon, self.typeID)
        output_item_icon.hint = evetypes.GetName(self.typeID)
        output_item_icon.GetMenu = lambda *args: GetMenuService().GetMenuFromItemIDTypeID(None, self.typeID, includeMarketDetails=True)

    def ConstructLabels(self, qty, hasMultipleOutputs):
        item_label = evetypes.GetName(self.typeID)
        labelCont = ContainerAutoSize(parent=self, align=uiconst.CENTERTOP, width=100 if hasMultipleOutputs else 200)
        output_item_label = carbonui.TextDetail(name='output_item_label', parent=labelCont, text=item_label, align=uiconst.TOTOP_NOPUSH, top=103, maxLines=3, textAlign=TextAlign.CENTER)
        self.qtyLabel = carbonui.TextBody(name='qtyLabel', parent=self, text=FmtAmt(qty), align=uiconst.CENTERTOP, top=84)

    def UpdateQty(self, qty):
        self.qtyLabel.SetText(FmtAmt(qty))


class MoreOutputItems(Container):
    default_width = 24
    default_height = 24
    default_align = uiconst.CENTER

    def ApplyAttributes(self, attributes):
        super(MoreOutputItems, self).ApplyAttributes(attributes)
        self.qtyByTypeID = attributes.qtyByTypeID
        Sprite(parent=self, pos=(0, 0, 24, 24), align=carbonui.Align.CENTER, texturePath='res:/UI/Texture/classes/ItemTrader/moreCircle.png', state=uiconst.UI_DISABLED, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, opacity=0.3)
        sprite = ButtonIcon(parent=self, pos=(0, 0, 24, 24), align=carbonui.Align.CENTER, texturePath='res:/UI/Texture/classes/ItemTrader/morePlus.png')
        sprite.LoadTooltipPanel = self.LoadTooltipPanel

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadStandardSpacing()
        tooltipPanel.columns = 4
        tooltipPanel.state = uiconst.UI_NORMAL
        for typeID, qty in self.qtyByTypeID.iteritems():
            row = tooltipPanel.AddRow()
            row.state = uiconst.UI_NORMAL
            carbonui.TextBody(parent=row, text=FmtAmt(qty))
            carbonui.TextBody(parent=row, text='x')
            typeIcon = Sprite(parent=row, align=uiconst.CENTERLEFT, pos=(0, 0, 20, 20))
            sm.GetService('photo').GetIconByType(typeIcon, typeID)
            carbonui.TextBody(parent=row, text=evetypes.GetName(typeID))
            row.GetMenu = lambda t = typeID, *args: GetMenuService().GetMenuFromItemIDTypeID(None, t, includeMarketDetails=True)

    def UpdateQty(self, typeID, qty):
        self.qtyByTypeID[typeID] = qty


def DefaultTooltip(tooltipPanel, text):
    tooltipPanel.LoadStandardSpacing()
    tooltipPanel.columns = 1
    tooltipPanel.AddLabelMedium(text=text)
