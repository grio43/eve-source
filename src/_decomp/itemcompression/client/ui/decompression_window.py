#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\itemcompression\client\ui\decompression_window.py
import localization
import uthread2
from carbon.common.script.util.format import FmtAmt
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.ui import eveColor
from carbonui.control.button import Button
from eve.client.script.ui.control.eveLabel import EveLabelSmall, EveLabelMedium, EveLabelLarge, EveCaptionLarge, EveCaptionSmall
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.eveColor import SUCCESS_GREEN_HEX, WHITE_HEX
from eveui import Sprite
from itemcompression.client.gasDecompression import decompress_gas
from itemcompression.client.ui.base_compression_window import BaseCompressionWindow
from itemcompression.client.ui.label_paths import decompression_window_caption_label_path, decompress_action_label_path, decompression_window_tooltip_decompression_calculations_title, decompression_window_tooltip_structure_efficiency, decompression_window_tooltip_character_skills, decompression_window_tooltip_yield_title, decompression_window_lossy_warning, compression_completed_label_path
from itemcompression.gasDecompression import get_gas_decompression_efficiency, get_decompression_fractional_output

class GasDecompressionWindow(BaseCompressionWindow):
    default_captionLabelPath = decompression_window_caption_label_path
    default_minWidth = 550
    default_minSize = (400, 125)
    default_iconNum = 'res:/UI/Texture/WindowIcons/decompression.png'
    __notifyevents__ = ['OnSessionChanged', 'OnItemChange', 'OnSkillsChanged']
    default_windowID = 'decompression_window'

    def OnSkillsChanged(self, *args):
        while not self.window_constructed:
            uthread2.Yield()

        totalEfficiency = self._GetDecompressionEfficiency()
        self.UpdateEfficiencyGauge()
        self.ReconstructOutputIcons()

    def OnSessionChanged(self, *args):
        self.Close()

    def ApplyAttributes(self, attributes):
        item = attributes.get('invItem')
        self.input_items = [item]
        self.output_icons = {}
        self.decompression_button = None
        self.decompression_completed = False
        self.window_constructed = False
        self.structureEfficiency = attributes.get('structureEfficiency')
        self.characterEfficiency = attributes.get('characterEfficiency')
        super(GasDecompressionWindow, self).ApplyAttributes(attributes)
        self.ignore_inventory_events = False
        self.UpdateEfficiencyGauge()
        self._ReconstructInputOutputConts()
        self.window_constructed = True

    def _ReconstructInputOutputConts(self):
        self.ReconstructInputIcons()
        self.ReconstructOutputIcons()

    def OnItemChange(self, item, change, _location):
        if self.ignore_inventory_events:
            return
        ixLocationID = 3
        ixStackSize = 9
        if not self.HaveItemID(item.itemID):
            return
        if ixStackSize in change:
            if item.stacksize == 0:
                self.RemoveItem(item)
            self.ReplaceItem(item)
        elif ixLocationID in change:
            self.RemoveItem(item)

    def ConstructInputPanel(self):
        super(GasDecompressionWindow, self).ConstructInputPanel()
        totalEfficiency = self._GetDecompressionEfficiency()
        gauge_width = 64
        gauge_height = 18
        gaugeCont = Container(parent=self.input_header_cont, align=uiconst.CENTERRIGHT, width=gauge_width, height=gauge_height)
        self.efficiency_label = EveLabelLarge(parent=gaugeCont, align=uiconst.CENTER, text='{}%'.format(int(totalEfficiency * 100)), idx=0, bold=True)
        self.efficiency_gauge = _DecompressionEfficiencyGauge(parent=gaugeCont, name='efficiency_gauge', width=gauge_width, gaugeHeight=gauge_height, color=eveColor.CRYO_BLUE, characterEfficiency=self.characterEfficiency, structureEfficiency=self.structureEfficiency, totalEfficiency=totalEfficiency)

    def ConstructBottomButtons(self):
        super(GasDecompressionWindow, self).ConstructBottomButtons()
        self.decompression_button = Button(name='DecompressButton', parent=self.bottom_cont, align=uiconst.TOPRIGHT, label=localization.GetByLabel(decompress_action_label_path), func=self.DoDecompression)

    def UpdateEfficiencyGauge(self):
        self.structureEfficiency, self.characterEfficiency = sm.RemoteSvc('structureCompressionMgr').GetMyGasDecompressionEfficiency()
        totalEfficiency = self._GetDecompressionEfficiency()
        self.efficiency_gauge.SetValue(totalEfficiency, duration=0.25)
        self.efficiency_label.SetText('{}%'.format(int(totalEfficiency * 100)))
        self.efficiency_gauge.characterEfficiency = self.characterEfficiency
        self.efficiency_gauge.structureEfficiency = self.structureEfficiency
        self.efficiency_gauge.totalEfficiency = totalEfficiency

    def _GetDecompressionEfficiency(self):
        totalEfficiency = get_gas_decompression_efficiency(self.structureEfficiency, self.characterEfficiency)
        return totalEfficiency

    def ReconstructInputIcons(self):
        self.input_cont.Flush()
        for item in self.input_items:
            self._AddItemToInputCont(item)

    def _AddItemToInputCont(self, item):
        _StackedItemIcon(parent=self.input_cont, itemID=item.itemID, quantity=item.stacksize, typeID=item.typeID)

    def ReconstructOutputIcons(self):
        self.output_cont.Flush()
        self.output_icons = {}
        for item in self.input_items:
            self._AddItemToOuputCont(item)

    def _AddItemToOuputCont(self, item):
        totalEfficiency = self._GetDecompressionEfficiency()
        outputTypeID, outputFractionalQuantity = get_decompression_fractional_output(item.typeID, item.stacksize, totalEfficiency)
        self.output_icons[item.itemID] = _StackedItemIcon(parent=self.output_cont, quantity=outputFractionalQuantity, typeID=outputTypeID, output=True, opacity=0.5)

    def DoDecompression(self, *args):
        self.ignore_inventory_events = True
        for item in self.input_items:
            _sourceItemID, _sourceTypeID, _sourceQuantity, _outputItemID, _outputTypeID, outputQuantity = decompress_gas(item.itemID)
            if outputQuantity == 0:
                self.output_icons[item.itemID].Close()
            else:
                self.output_icons[item.itemID].MarkAsDecompressed(outputQuantity)

        self.MarkAsComplete()
        self.ignore_inventory_events = False

    def MarkAsComplete(self):
        self.input_items = []
        self.ReconstructInputIcons()
        if self.decompression_button:
            self.decompression_button.Close()
        completed_message_cont = ContainerAutoSize(name='completed_message_cont', parent=self.bottom_cont, align=uiconst.TORIGHT, alignMode=uiconst.TORIGHT, ping=5)
        sprite_cont = Container(name='sprite_cont', parent=completed_message_cont, width=self.bottom_cont.height, height=self.bottom_cont.height, align=uiconst.TORIGHT, top=-2)
        completed_sprite = Sprite(parent=sprite_cont, texturePath='res:/UI/Texture/classes/SkillPlan/completedIcon.png', width=34, height=34, align=uiconst.CENTER)
        completed_label = EveLabelLarge(color=eveColor.SUCCESS_GREEN, parent=self.bottom_cont, align=uiconst.TORIGHT, alignMode=uiconst.TORIGHT, text=localization.GetByLabel(compression_completed_label_path), opacity=0)
        uicore.animations.FadeIn(completed_label, duration=0.1)
        uicore.animations.SpMaskIn(completed_sprite)
        self.decompression_completed = True

    def AddItem(self, invItem):
        while not self.window_constructed:
            uthread2.Yield()

        if invItem in self.input_items:
            return
        self.input_items.append(invItem)
        if self.decompression_completed:
            self.decompression_completed = False
            self.window_constructed = False
            self._ReconstructInputOutputConts()
            self.window_constructed = True
            self.bottom_cont.Flush()
            self.ConstructBottomButtons()
        else:
            self._AddItemToInputCont(invItem)
            self._AddItemToOuputCont(invItem)

    @classmethod
    def AddItemOrOpenWindow(cls, invItem):
        structureEfficiency, characterEfficiency = sm.RemoteSvc('structureCompressionMgr').GetMyGasDecompressionEfficiency()
        window = cls.GetIfOpen()
        if window:
            window.AddItem(invItem)
        else:
            GasDecompressionWindow(invItem=invItem, structureEfficiency=structureEfficiency, characterEfficiency=characterEfficiency)

    def HaveItemID(self, itemID):
        for item in self.input_items:
            if itemID == item.itemID:
                return True

        return False

    def GetByItemID(self, itemID):
        for item in self.input_items:
            if itemID == item.itemID:
                return item

    def ReplaceItem(self, invItem):
        for i in range(len(self.input_items)):
            if self.input_items[i].itemID == invItem.itemID:
                self.input_items[i] = invItem

        self.UpdateEfficiencyGauge()
        self.ReconstructInputIcons()
        self.ReconstructOutputIcons()

    def RemoveItem(self, invItem):
        if self.HaveItemID(invItem.itemID):
            self.input_items.remove(self.GetByItemID(invItem.itemID))
            self.UpdateEfficiencyGauge()
            self.ReconstructInputIcons()
            self.ReconstructOutputIcons()


class _DecompressionEfficiencyGauge(Gauge):

    def ApplyAttributes(self, attributes):
        Gauge.ApplyAttributes(self, attributes)
        self.characterEfficiency = attributes.get('characterEfficiency')
        self.structureEfficiency = attributes.get('structureEfficiency')
        self.totalEfficiency = attributes.get('totalEfficiency')

    def LoadTooltipPanel(self, tooltipPanel, *args):
        container_grid = LayoutGrid(rows=2, columns=1)
        header_grid = LayoutGrid(columns=2, rows=1)
        body_grid = LayoutGrid(columns=1, rows=3)
        total_yield_grid = LayoutGrid(columns=1, rows=2)
        decompression_icon = Sprite(name='decompression_icon', width=32, height=32, texturePath='res:/UI/Texture/classes/decompression/decompression_32x32.png')
        compression_yield_title = EveLabelLarge(text=localization.GetByLabel(decompression_window_tooltip_yield_title), bold=True)
        total_efficiency_value = EveLabelMedium(text='{}%'.format(int(self.totalEfficiency * 100)), color=eveColor.CRYO_BLUE, bold=True)
        calculations_title = EveLabelMedium(text=localization.GetByLabel(decompression_window_tooltip_decompression_calculations_title), bold=True)
        structure_efficiency_value = EveLabelMedium(text=localization.GetByLabel(decompression_window_tooltip_structure_efficiency, textColor=WHITE_HEX, structureEfficiency=int(self.structureEfficiency * 100)))
        character_efficiency_value = EveLabelMedium(text=localization.GetByLabel(decompression_window_tooltip_character_skills, textColor=SUCCESS_GREEN_HEX, bonus=int(self.characterEfficiency * 100)))
        total_yield_grid.AddCell(compression_yield_title)
        total_yield_grid.AddCell(total_efficiency_value)
        body_grid.AddCell(calculations_title)
        body_grid.AddCell(structure_efficiency_value)
        body_grid.AddCell(character_efficiency_value)
        header_grid.AddCell(decompression_icon, colSpan=1)
        header_grid.AddCell(total_yield_grid, colSpan=1)
        container_grid.AddCell(header_grid, cellPadding=3)
        container_grid.AddCell(body_grid, cellPadding=(8, 3, 3, 3))
        tooltipPanel.AddCell(container_grid, cellPadding=10)


class _StackedItemIcon(ItemIcon):
    default_width = 64
    default_height = 64
    default_align = uiconst.NOALIGN

    def ApplyAttributes(self, attributes):
        ItemIcon.ApplyAttributes(self, attributes)
        self.output = attributes.output
        self.quantity = attributes.quantity
        labelCont = ContainerAutoSize(parent=self, align=uiconst.BOTTOMRIGHT, alignMode=uiconst.TOPLEFT, bgColor=Color.BLACK, idx=0)
        quantity_txt = FmtAmt(self.quantity, 'ss')
        self.quantity_label = EveLabelSmall(parent=labelCont, align=uiconst.TOPLEFT, maxLines=1, padding=(4, 1, 4, 0), text=quantity_txt, color=Color.WHITE)
        self.warning_sprite = None
        if int(self.quantity) == 0 and self.output:
            self.warning_sprite = Sprite(parent=self, align=uiconst.TOPRIGHT, texturePath='res:/UI/Texture/classes/crab/warningIcon.png', width=24, height=24, idx=0)

    def MarkAsDecompressed(self, output_quantity):
        self.opacity = 1.0
        self.quantity = output_quantity
        self.quantity_label.SetText(FmtAmt(self.quantity, 'ss'))
        if self.warning_sprite:
            self.warning_sprite.Close()

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if int(self.quantity) == 0 and self.output:
            warningLabel = EveLabelSmall(text=localization.GetByLabel(decompression_window_lossy_warning), maxWidth=160)
            warningIcon = Sprite(texturePath='res:/UI/Texture/classes/crab/warningIcon.png', width=32, height=32)
            energyStateGrid = LayoutGrid(state=uiconst.UI_NORMAL, columns=2)
            energyStateGrid.AddCell(warningIcon, colSpan=1, rowSpan=2, cellPadding=(0, 0, 0, 5))
            energyStateGrid.AddCell(warningLabel, colSpan=1, cellPadding=(0, 5, 0, 5))
            tooltipPanel.AddCell(energyStateGrid)
        else:
            ItemIcon.LoadTooltipPanel(self, tooltipPanel, *args)
