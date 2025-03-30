#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\panels\panelItemIndustry.py
import evetypes
import localization
from carbonui import uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveScroll import Scroll
from evetypes import TypeNotFoundException
import itemcompression.data as compressiondata
from typematerials.data import get_type_materials_by_id, is_decompressible_gas_type

class PanelItemIndustry(Container):
    typeID = None

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.typeID = attributes.typeID

    def Load(self):
        self.Flush()
        entries = []
        entries.extend(self._GetBlueprintEntries())
        entries.extend(self._GetReprocessingEntries())
        entries.extend(self._GetRequiredForEntries())
        entries.extend(self._GetCompressionEntries())
        scroll = Scroll(parent=self, padding=uiconst.defaultPadding)
        scroll.Load(contentList=entries)

    def _GetCompressionEntries(self):
        entries = []
        if compressiondata.is_compressible_type(self.typeID):
            entryHeader = GetFromClass(Header, {'label': localization.GetByLabel('UI/InfoWindow/Subheaders/CompressionOutput')})
            entries.append(entryHeader)
            compressedTypeID = compressiondata.get_compressed_type_id(self.typeID)
            entryItem = GetFromClass(Item, {'label': evetypes.GetName(compressedTypeID),
             'typeID': compressedTypeID,
             'getIcon': 1})
            entries.append(entryItem)
        if compressiondata.is_compressed_type(self.typeID):
            entryHeader = GetFromClass(Header, {'label': localization.GetByLabel('UI/InfoWindow/Subheaders/CompressionInput')})
            entries.append(entryHeader)
            for sourceTypeID in compressiondata.get_compression_source_type_ids(self.typeID):
                entryItem = GetFromClass(Item, {'label': evetypes.GetName(sourceTypeID),
                 'typeID': sourceTypeID,
                 'getIcon': 1})
                entries.append(entryItem)

        return entries

    def _GetRequiredForEntries(self):
        entries = []
        blueprintIDs = cfg.blueprintsByMaterialTypeIDs.get(self.typeID, None)
        if blueprintIDs:
            for blueprintID in blueprintIDs:
                try:
                    if not evetypes.IsPublished(blueprintID):
                        continue
                except TypeNotFoundException:
                    continue

                entries.append(GetFromClass(Item, {'label': evetypes.GetName(blueprintID),
                 'typeID': blueprintID,
                 'getIcon': 1}))

            entries = sorted(entries, key=self._GetRequiredForSortKey)
            if entries:
                entries.insert(0, GetFromClass(Header, {'label': localization.GetByLabel('UI/InfoWindow/TabNames/RequiredFor')}))
        return entries

    def _GetRequiredForSortKey(self, entry):
        return entry.label

    def _GetReprocessingEntries(self):
        entries = []
        materials = get_type_materials_by_id(self.typeID)
        if materials:
            if is_decompressible_gas_type(self.typeID):
                entries.append(GetFromClass(Header, {'label': localization.GetByLabel('UI/InfoWindow/Subheaders/DecompressionOutput')}))
            else:
                entries.append(GetFromClass(Header, {'label': localization.GetByLabel('UI/Reprocessing/ReprocessedMaterials')}))
            for material in materials:
                typeID = material.materialTypeID
                quantity = material.quantity
                entries.append(GetFromClass(Item, {'label': localization.GetByLabel('UI/InfoWindow/TypeNameWithNumUnits', invType=typeID, qty=quantity),
                 'typeID': typeID,
                 'getIcon': 1,
                 'quantity': quantity}))

        return entries

    def _GetBlueprintEntries(self):
        entries = []
        bpData = sm.GetService('blueprintSvc').GetBlueprintByProduct(self.typeID)
        if bpData and evetypes.IsPublished(bpData.blueprintTypeID):
            entries.append(GetFromClass(Header, {'label': localization.GetByLabel('UI/Industry/Blueprint')}))
            entries.append(GetFromClass(Item, {'label': bpData.GetName(),
             'typeID': bpData.blueprintTypeID,
             'getIcon': 1}))
        return entries
