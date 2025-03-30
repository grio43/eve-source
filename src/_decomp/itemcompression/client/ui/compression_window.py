#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\itemcompression\client\ui\compression_window.py
import blue
import evetypes
import itemcompression
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
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelSmall, EveLabelLarge, EveLabelMediumBold
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.control.message import ShowQuickMessage
from evetypes import GetTypeIDsByListID, GetTypeIDsByListIDs
from eveui import Sprite
from itemcompression.client.inSpaceCompression import GetFacilitiesInRange
from itemcompression.client.itemCompression import CompressItemInSpace, CompressItemInStructure
from itemcompression.client.ui.base_compression_window import BaseCompressionWindow
from itemcompression.client.ui.label_paths import compression_window_caption_label_path, compression_completed_label_path, compress_action_label_path, no_facility_label_path, compressed_by_label_path, reprocessing_facility_unavailable_tooltip_label_path
from structures import SERVICE_REPROCESSING

class CompressionWindow(BaseCompressionWindow):
    default_windowID = 'compression_window'
    default_captionLabelPath = compression_window_caption_label_path
    default_iconNum = 'res:/UI/Texture/WindowIcons/compression.png'
    default_in_structure = False
    __notifyevents__ = ['OnItemChange', 'OnSessionChanged']

    def OnSessionChanged(self, *args):
        self.Close()

    def ApplyAttributes(self, attributes):
        invItem = attributes.get('invItem')
        self.structure_location_item = attributes.get('structure_location_item', None)
        self.in_structure = False
        if self.structure_location_item:
            self.in_structure = True
        super(CompressionWindow, self).ApplyAttributes(attributes)
        self.ignore_inventory_events = False
        self.items = [invItem]
        self.facilities_to_types = {}
        self.uncompressed_item_icons = {}
        self.compressed_item_icons = {}
        if not self.in_structure:
            self.CacheFacilityData()
        self.refresh_locked = False
        self.ReconstructInputIcons()
        self.ReconstructOutputIcons()
        if not self.in_structure:
            uthread2.StartTasklet(self.StartRefreshLoop)

    def RefreshFacilityData(self):
        self.facilities_to_types = {}
        self.CacheFacilityData()

    def CacheFacilityData(self):
        fleet_members = sm.GetService('fleet').GetMembers().keys()
        facility_tuples = GetFacilitiesInRange(sm.GetService('michelle').GetBallpark(), fleet_members)
        for facility_tuple in facility_tuples:
            ballID, compressibleTypeListIDs = facility_tuple
            typeIDs = GetTypeIDsByListIDs(compressibleTypeListIDs)
            self.facilities_to_types[ballID] = typeIDs

    def GetCompressionFacilityBallID(self, typeID):
        for ballID, typeIDs in self.facilities_to_types.iteritems():
            if typeID in typeIDs:
                return ballID

    def Compress(self):
        compressedItemIDs = []
        self.ignore_inventory_events = True
        if self.in_structure:
            for invItem in self.items:
                CompressItemInStructure(invItem)
                compressedItemIDs.append(invItem.itemID)
                structure_name = cfg.evelocations.Get(session.structureid).locationName
                self.compressed_item_icons[invItem.itemID].MarkAsCompressed(structure_name)

        else:
            compressedItemIDs = []
            for invItem in self.items:
                ballID = self.GetCompressionFacilityBallID(invItem.typeID)
                if ballID:
                    CompressItemInSpace(invItem, ballID)
                    compressedItemIDs.append(invItem.itemID)
                    ship_name = cfg.evelocations.Get(ballID).name
                    self.compressed_item_icons[invItem.itemID].MarkAsCompressed(ship_name)

        remaining = []
        for invItem in self.items:
            if invItem.itemID not in compressedItemIDs:
                remaining.append(invItem)

        self.items = remaining
        if compressedItemIDs:
            self.MarkCompleted()
            self.ReconstructInputIcons()
        self.ignore_inventory_events = False

    def MarkCompleted(self):
        self.compress_button.Close()
        completed_message_cont = ContainerAutoSize(name='completed_message_cont', parent=self.bottom_cont, align=uiconst.TORIGHT, alignMode=uiconst.TORIGHT, padding=5)
        sprite_cont = Container(name='sprite_cont', parent=completed_message_cont, width=self.bottom_cont.height, height=self.bottom_cont.height, align=uiconst.TORIGHT, top=-2)
        completed_sprite = Sprite(parent=sprite_cont, texturePath='res:/UI/Texture/classes/SkillPlan/completedIcon.png', width=34, height=34, align=uiconst.CENTER)
        completed_label = EveLabelLarge(color=eveColor.SUCCESS_GREEN, parent=self.bottom_cont, align=uiconst.TORIGHT, alignMode=uiconst.TORIGHT, text=localization.GetByLabel(compression_completed_label_path), opacity=0)
        uicore.animations.FadeIn(completed_label, duration=0.1)
        uicore.animations.SpMaskIn(completed_sprite)

    def ConstructBottomButtons(self, compress_disabled = False):
        super(CompressionWindow, self).ConstructBottomButtons()
        self.compress_button = Button(name='compress_button', parent=self.bottom_cont, align=uiconst.TOPRIGHT, label=localization.GetByLabel(compress_action_label_path), func=lambda *_args: self.Compress())
        if self.in_structure:
            structureServies = sm.GetService('structureServices')
            compress_disabled = not structureServies.IsServiceAvailableForCharacter(SERVICE_REPROCESSING)
            if compress_disabled:
                self.compress_button.SetHint(localization.GetByLabel(reprocessing_facility_unavailable_tooltip_label_path))
        self.compress_button.disabled = compress_disabled

    def CanCompressType(self, typeID):
        return self.in_structure or self.GetCompressionFacilityBallID(typeID) is not None

    def ReconstructInputIcons(self):
        self.uncompressed_item_icons = {}
        self.input_cont.Flush()
        for item in self.items:
            can_compress = self.CanCompressType(item.typeID)
            icon = _StackedItemIcon(invItem=item, parent=self.input_cont, itemID=item.itemID, quantity=item.stacksize, typeID=item.typeID, can_compress=can_compress)
            self.uncompressed_item_icons[item.itemID] = icon

    def ReconstructOutputIcons(self):
        self.compressed_item_icons = {}
        self.output_cont.Flush()
        for item in self.items:
            can_compress = self.in_structure or self.GetCompressionFacilityBallID(item.typeID) is not None
            if can_compress:
                compressedTypeID = itemcompression.data.get_compressed_type_id(item.typeID)
                icon = _StackedItemIcon(invItem=item, parent=self.output_cont, typeID=compressedTypeID, quantity=item.stacksize, opacity=0.5)
                self.compressed_item_icons[item.itemID] = icon

    def async_AddItem(self, invItem):
        uthread2.StartTasklet(self.AddItem_RespectRefreshLock, invItem)

    def async_RemoveItem(self, invItem):
        uthread2.StartTasklet(self.RemoveItem_RespectRefreshLock, invItem)

    def async_ReplaceItem(self, invItem):
        uthread2.StartTasklet(self.ReplaceItem_RespectRefreshLock, invItem)

    def ReplaceItem_RespectRefreshLock(self, invItem):
        while self.refresh_locked:
            blue.pyos.BeNice()

        self.refresh_locked = True
        self.ReplaceItem(invItem)
        self.ReconstructInputIcons()
        self.ReconstructOutputIcons()
        self.refresh_locked = False

    def RemoveItem_RespectRefreshLock(self, invItem):
        while self.refresh_locked:
            blue.pyos.BeNice()

        self.refresh_locked = True
        self.RemoveItem(invItem)
        self.ReconstructInputIcons()
        self.ReconstructOutputIcons()
        self.refresh_locked = False

    def AddItem_RespectRefreshLock(self, invItem):
        while self.refresh_locked:
            blue.pyos.BeNice()

        self.refresh_locked = True
        self.AddItem(invItem)
        self.refresh_locked = False

    def ReplaceItem(self, invItem):
        for i in range(len(self.items)):
            if self.items[i].itemID == invItem.itemID:
                self.items[i] = invItem

    def RemoveItem(self, invItem):
        if self.HaveItemID(invItem.itemID):
            self.items.remove(self.GetByItemID(invItem.itemID))
            self.ReconstructInputIcons()
            self.ReconstructOutputIcons()
            compress_button_disabled = self.compress_button.disabled
            self.bottom_cont.Flush()
            self.ConstructBottomButtons(compress_disabled=compress_button_disabled)

    def HaveItemID(self, itemID):
        for item in self.items:
            if itemID == item.itemID:
                return True

        return False

    def GetByItemID(self, itemID):
        for item in self.items:
            if itemID == item.itemID:
                return item

    def OnItemChange(self, item, change, _location):
        if self.ignore_inventory_events:
            return
        ixLocationID = 3
        ixStackSize = 9
        if not self.HaveItemID(item.itemID):
            return
        if ixStackSize in change:
            if item.stacksize == 0:
                self.async_RemoveItem(item)
            self.async_ReplaceItem(item)
        elif ixLocationID in change:
            self.async_RemoveItem(item)

    def AddItem(self, invItem):
        if invItem not in self.items:
            self.items.append(invItem)
            self.ReconstructInputIcons()
            self.ReconstructOutputIcons()
            compress_button_disabled = self.compress_button.disabled
            self.bottom_cont.Flush()
            self.ConstructBottomButtons(compress_disabled=compress_button_disabled)

    @classmethod
    def AddItemOrOpenWindow(cls, invItem, structure_location_item = None):
        window = cls.GetIfOpen()
        if window:
            window.Maximize()
            window.async_AddItem(invItem)
        else:
            CompressionWindow(invItem=invItem, structure_location_item=structure_location_item)

    def StartRefreshLoop(self):
        while not self.destroyed:
            if not self.refresh_locked:
                self.refresh_locked = True
                try:
                    self.RefreshFacilityData()
                    self.CacheFacilityData()
                    self.RefreshIconsWhereNessecary()
                    self.UpdateCompressButton()
                finally:
                    self.refresh_locked = False

            uthread2.sleep(1)

    def RefreshIconsWhereNessecary(self):
        change = False
        for itemID, icon in self.uncompressed_item_icons.iteritems():
            can_compress = self.CanCompressType(icon.typeID)
            if can_compress != icon.can_compress:
                change = True
                icon.labelCont.Close()
                if icon.warning_sprite:
                    icon.warning_sprite.Close()
                icon.can_compress = can_compress
                icon.ConstructLayout()

        if change:
            self.ReconstructOutputIcons()

    def UpdateCompressButton(self):
        if not self.compressed_item_icons == {} and self.compress_button.disabled:
            self.compress_button.disabled = False
        elif self.compressed_item_icons == {} and not self.compress_button.disabled:
            self.compress_button.disabled = True


class _StackedItemIcon(ItemIcon):
    default_width = 64
    default_height = 64
    default_align = uiconst.NOALIGN
    default_can_compress = True

    def ApplyAttributes(self, attributes):
        ItemIcon.ApplyAttributes(self, attributes)
        self.can_compress = attributes.get('can_compress', _StackedItemIcon.default_can_compress)
        self.invItem = attributes.get('invItem')
        self.compressed_by_player_name = None
        self.quantity = attributes.quantity
        self.ConstructLayout()

    def ConstructLayout(self):
        self.labelCont = ContainerAutoSize(parent=self, align=uiconst.BOTTOMRIGHT, alignMode=uiconst.TOPLEFT, bgColor=Color.BLACK, idx=0)
        quantity_txt = FmtAmt(self.quantity, 'ss')
        EveLabelSmall(parent=self.labelCont, align=uiconst.TOPLEFT, maxLines=1, padding=(4, 1, 4, 0), text=quantity_txt, color=Color.WHITE)
        self.warning_sprite = None
        if not self.can_compress:
            self.warning_sprite = Sprite(parent=self, align=uiconst.TOPRIGHT, texturePath='res:/UI/Texture/classes/crab/warningIcon.png', width=24, height=24, idx=0)

    def MarkAsCompressed(self, playerName):
        self.compressed_by_player_name = playerName
        self.opacity = 1.0

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if self.compressed_by_player_name:
            grid = LayoutGrid(columns=2, rows=2)
            grid.AddCell(EveLabelMediumBold(text=evetypes.GetName(self.typeID)), colSpan=2)
            grid.AddCell(EveLabelMedium(text=localization.GetByLabel(compressed_by_label_path, facility_name=self.compressed_by_player_name), width=220))
            tooltipPanel.AddCell(grid, cellPadding=7)
        elif not self.can_compress:
            warningLabel = EveLabelSmall(text=localization.GetByLabel(no_facility_label_path), maxWidth=160, padding=10)
            warningIcon = Sprite(texturePath='res:/UI/Texture/classes/crab/warningIcon.png', width=32, height=32, top=16)
            energyStateGrid = LayoutGrid(state=uiconst.UI_NORMAL, columns=2)
            energyStateGrid.AddCell(warningIcon, colSpan=1, rowSpan=2)
            energyStateGrid.AddCell(warningLabel, colSpan=1, cellPadding=(0, 0, 0, 5))
            tooltipPanel.AddCell(energyStateGrid)


class DirectCompressInSpace(object):

    def __init__(self):
        self.facilities_to_types = {}
        self.PrimeFacilities()

    def PrimeFacilities(self):
        fleet_members = sm.GetService('fleet').GetMembers().keys()
        facility_tuples = GetFacilitiesInRange(sm.GetService('michelle').GetBallpark(), fleet_members)
        for facility_tuple in facility_tuples:
            ballID, compressibleTypeListIDs = facility_tuple
            typeIDs = GetTypeIDsByListIDs(compressibleTypeListIDs)
            self.facilities_to_types[ballID] = typeIDs

    def GetCompressionFacilityBallID(self, typeID):
        for ballID, typeIDs in self.facilities_to_types.iteritems():
            if typeID in typeIDs:
                return ballID

    def CompressItems(self, invItems):
        failureToCompress = False
        someSuccess = False
        for item in invItems:
            ballID = self.GetCompressionFacilityBallID(item.typeID)
            if ballID:
                wasCompressed = CompressItemInSpace(item, ballID)
                if wasCompressed:
                    someSuccess = True
                else:
                    failureToCompress = True
            else:
                failureToCompress = True

        if failureToCompress:
            if someSuccess:
                ShowQuickMessage(localization.GetByLabel('UI/Compression/FailureToCompressSome'))
            else:
                ShowQuickMessage(localization.GetByLabel('UI/Compression/FailureToCompressAny'))


def DirectlyCompressInSpace(invItems):
    directCompressObject = DirectCompressInSpace()
    directCompressObject.CompressItems(invItems)


def DirectlyCompressInStructure(invItems):
    for item in invItems:
        CompressItemInStructure(item)
