#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\panels\planetaryProductionPlanet.py
import evetypes
from carbonui.primitives.container import Container
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.shared.planet import planetCommon
from eve.client.script.ui.shared.planet.planetItemEntry import PlanetItemEntry
from eve.common.lib import appConst as const
from localization import GetByLabel
from fsdBuiltData.common.planet import get_resource_type_ids_for_planet_type_id

class PanelPlanetaryProductionPlanet(Container):

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
        scrolllist = []
        resourceTypeIDs = sorted(get_resource_type_ids_for_planet_type_id(self.typeID, []), key=lambda typeID: evetypes.GetName(typeID))
        if resourceTypeIDs:
            scrolllist.append(GetFromClass(Header, {'label': GetByLabel('UI/PI/Common/ExtractableResources')}))
        for typeID in resourceTypeIDs:
            scrolllist.append(GetFromClass(PlanetItemEntry, {'itemID': None,
             'typeID': typeID,
             'selectable': False,
             'label': planetCommon.GetProductNameAndTier(typeID),
             'getIcon': 1}))

        return scrolllist
