#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\panels\planetaryProduction.py
import evetypes
from carbonui.primitives.container import Container
from eve.client.script.ui.control import entries
from eve.client.script.ui.control.entries.header import Header, Subheader
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.control.entries.space import Space
from eve.client.script.ui.control.entries.text import Text
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.shared.planet import planetCommon
from eve.client.script.ui.shared.planet.planetSchematicItemEntry import PlanetSchematicItemEntry
from eve.common.lib import appConst as const
from fsdBuiltData.common.planet import get_planet_type_ids_for_resource_type_id
from fsdBuiltData.common.planet import get_schematic_types
from localization import GetByLabel
from utillib import KeyVal

class PanelPlanetaryProduction(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.typeID = attributes.typeID
        self.isInitialized = False

    def Load(self):
        if self.isInitialized:
            return
        self.scroll = Scroll(name='scroll', parent=self, padding=const.defaultPadding)
        scrolllist = self.GetScrollList()
        self.scroll.Load(fixedEntryHeight=27, contentList=scrolllist)
        self.isInitialized = True

    def GetScrollList(self):
        return self.GetSchematicScrolllist() + self.GetExtractedByScrolllist() + self.GetRequiredForScrolllist()

    def GetSchematicScrolllist(self):
        inputs, outputs = self._GetSchematicInputsAndOutputs()
        scrolllist = []
        if inputs and outputs:
            scrolllist.append(GetFromClass(Header, {'label': GetByLabel('UI/PI/Common/Schematic')}))
            schematic = planetCommon.GetSchematicDataForID(self.GetSchematicID())
            text = planetCommon.GetSchematicCycleTimeText(schematic)
            scrolllist.append(GetFromClass(Text, {'text': text}))
            text = planetCommon.GetSchematicOutputVolumeText(schematic)
            scrolllist.append(GetFromClass(Text, {'text': text}))
            scrolllist.append(GetFromClass(Subheader, {'label': GetByLabel('UI/PI/Common/SchematicInput')}))
            for data in inputs:
                scrolllist.append(GetFromClass(PlanetSchematicItemEntry, data))

            scrolllist.append(GetFromClass(Subheader, {'label': GetByLabel('UI/PI/Common/OutputProduct')}))
            for data in outputs:
                scrolllist.append(GetFromClass(PlanetSchematicItemEntry, data))

        return scrolllist

    def _GetSchematicInputsAndOutputs(self):
        schematicID = self.GetSchematicID()
        inputs = []
        outputs = []
        for typeID, typeInfo in get_schematic_types(schematicID, {}).iteritems():
            label = GetByLabel('UI/PI/Common/ItemAmount', itemName=planetCommon.GetProductNameAndTier(typeID), amount=typeInfo.quantity)
            data = KeyVal(label=label, typeID=typeID, itemID=None, getIcon=1, quantity=typeInfo.quantity, selectable=False)
            if typeInfo.isInput:
                inputs.append(data)
            else:
                outputs.append(data)

        return (inputs, outputs)

    def GetSchematicID(self):
        schematicID = planetCommon.GetSchematicByOutput(self.typeID)
        return schematicID

    def GetExtractedByScrolllist(self):
        scrolllist = []
        extractedByScrolllist = self._GetExtractableOnScrollList()
        if len(extractedByScrolllist) > 0:
            scrolllist.append(GetFromClass(Header, {'label': GetByLabel('UI/InfoWindow/ExtractableOnPlanet')}))
            scrolllist.extend(extractedByScrolllist)
        return scrolllist

    def GetRequiredForScrolllist(self):
        scrolllist = []
        scrolllist.append(GetFromClass(Space, {'height': 10}))
        consumingSchematicLines = self._GetRequiredForScrolllist()
        if len(consumingSchematicLines) > 0:
            scrolllist.append(GetFromClass(Header, {'label': GetByLabel('UI/InfoWindow/TabNames/RequiredFor')}))
            scrolllist.extend(consumingSchematicLines)
        return scrolllist

    def _GetRequiredForScrolllist(self):
        scrolllist = []
        for typeID in planetCommon.GetRequiredForItems(self.typeID):
            entry = GetFromClass(PlanetSchematicItemEntry, {'itemID': None,
             'typeID': typeID,
             'label': planetCommon.GetProductNameAndTier(typeID),
             'getIcon': 1,
             'selectable': False})
            scrolllist.append(entry)

        return scrolllist

    def _GetExtractableOnScrollList(self):
        scrolllist = []
        for planetTypeID in get_planet_type_ids_for_resource_type_id(self.typeID, []):
            scrolllist.append(GetFromClass(Item, {'itemID': None,
             'typeID': planetTypeID,
             'selectable': False,
             'label': evetypes.GetName(planetTypeID),
             'getIcon': 1}))

        return scrolllist
