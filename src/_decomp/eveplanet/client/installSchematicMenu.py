#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveplanet\client\installSchematicMenu.py
from collections import defaultdict
from carbonui.control.contextMenu.menuData import MenuData
from eve.client.script.ui.shared.planet.planetCommon import GetSchematicData, GetSchematicDataForID, GetTierByTypeID
from localization import GetByLabel

class MultiPinMenuProvider(object):

    def __init__(self, callback):
        self.callback = callback

    def GetMenu(self, pins):
        schematicsAvailable = defaultdict(list)
        for pin in pins:
            if not pin.IsProcessor():
                continue
            sd = GetSchematicData(pin.typeID)
            for s in sd:
                schematicsAvailable[s.schematicID].append(pin)

        m = MenuData()
        if schematicsAvailable:
            m.AddEntry(GetByLabel('UI/PI/InstallSchematic'), subMenuData=lambda : self._GetSchematicsSubMenu(schematicsAvailable))
        return m

    def _GetSchematicsSubMenu(self, schematicsAvailable):
        m = MenuData()
        tiers = defaultdict(list)
        for schematicID, pins in schematicsAvailable.iteritems():
            data = GetSchematicDataForID(schematicID)
            output = data.outputs[0]
            tier = GetTierByTypeID(output.typeID)
            tiers[tier].append((schematicID, data.name, pins))

        sortedTierItems = sorted(tiers.items())
        for tier, schematicesInTier in sortedTierItems:
            sortedSchematics = tuple(sorted(schematicesInTier, key=lambda x: x[1]))
            m.AddEntry(GetByLabel('UI/PI/Common/TierX', tier=tier), subMenuData=lambda sc = sortedSchematics: self.GetTierSubMenu(sc))

        return m

    def GetTierSubMenu(self, schematicesInTier):
        m = MenuData()
        for schematicID, schematicName, pins in schematicesInTier:
            m.AddEntry('%s (%s)' % (schematicName, len(pins)), lambda (scID, ps) = (schematicID, pins): self.InstallSchematic(scID, ps))

        return m

    def InstallSchematic(self, schematicID, pins):
        return self.callback(schematicID, pins)
