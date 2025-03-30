#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\panels\panelSov.py
from carbonui.primitives.container import Container
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveScroll import Scroll
from eve.common.lib import appConst as const
from inventorycommon.const import typeTerritorialClaimUnit
from localization import GetByLabel
from sovDashboard import GetSovStructureInfoByTypeID
from sovDashboard.devIndexHints import SetNormalBoxHint, SetStrategyHint
from sovDashboard.sovStatusEntries import SovSystemStatusEntry, SovStructureStatusEntry, SovAllianceEntry

class PanelSov(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.solarsystemID = attributes.solarsystemID
        self.sovSvc = sm.GetService('sov')

    def Load(self):
        self.Flush()
        self.scroll = Scroll(name='sovScroll', parent=self, padding=const.defaultPadding)
        contentList = []
        sovStructuresInfo = self.sovSvc.GetSovStructuresInfoForSolarSystem(self.solarsystemID)
        structureInfosByTypeID = GetSovStructureInfoByTypeID(sovStructuresInfo)
        tcuInfo = structureInfosByTypeID[typeTerritorialClaimUnit]
        isCapital = tcuInfo.get('isCapital', False)
        sovInfo = self.sovSvc.GetSovInfoForSolarsystem(self.solarsystemID, isCapital)
        devIndices = self.sovSvc.GetDevelopmentIndicesForSystem(self.solarsystemID)
        sovAllianceEntry = GetFromClass(SovAllianceEntry, {'sovHolderID': sovInfo.sovHolderID})
        contentList.append(sovAllianceEntry)
        headerEntry = GetFromClass(Header, {'label': GetByLabel('UI/Sovereignty/SystemSovStatus')})
        contentList.append(headerEntry)
        indexAndMultiplierInfo = self.GetIndexAndMultiplierInfo(sovInfo, isCapital, devIndices)
        for entryData in indexAndMultiplierInfo:
            statusEntry = GetFromClass(SovSystemStatusEntry, entryData)
            contentList.append(statusEntry)

        if sovStructuresInfo:
            headerEntry2 = GetFromClass(Header, {'label': GetByLabel('UI/Sovereignty/StructureSovStatus')})
            contentList.append(headerEntry2)
            for structureTypeID, structureInfo in structureInfosByTypeID.iteritems():
                if not structureInfo.get('itemID', None):
                    continue
                structureEntry = GetFromClass(SovStructureStatusEntry, {'structureInfo': structureInfo})
                contentList.append(structureEntry)

        self.scroll.Load(contentList=contentList)

    def GetIndexAndMultiplierInfo(self, sovInfo, isCapital, devIndices):
        if isCapital:
            defenseBonusTexture = 'res:/UI/Texture/classes/Sov/bonusShieldCapital16.png'
        else:
            defenseBonusTexture = 'res:/UI/Texture/classes/Sov/bonusShield16.png'
        defenseBonusInfo = {'indexID': None,
         'statusNameText': GetByLabel('UI/Sovereignty/ActivityDefenseMultiplier'),
         'texturePath': defenseBonusTexture,
         'currentIndex': None,
         'bonusMultiplier': sovInfo.defenseMultiplier,
         'extraHelpLabelPath': 'UI/Sovereignty/DefenseBonusExplanation',
         'isCapital': isCapital}
        strategicInfo = {'indexID': const.attributeDevIndexSovereignty,
         'statusNameText': GetByLabel('UI/Sovereignty/StrategicIndex'),
         'texturePath': 'res:/UI/Texture/classes/Sov/strategicIndex.png',
         'currentIndex': sovInfo.strategicIndexLevel,
         'bonusMultiplier': None,
         'boxTooltipFunc': SetStrategyHint,
         'extraHelpLabelPath': 'UI/Sovereignty/StrategicIndexExplanation',
         'partialValue': sovInfo.strategicIndexRemainder}
        militaryInfo = {'indexID': const.attributeDevIndexMilitary,
         'statusNameText': GetByLabel('UI/Sovereignty/MilitaryIndex'),
         'texturePath': 'res:/UI/Texture/classes/Sov/militaryIndex.png',
         'currentIndex': sovInfo.militaryIndexLevel,
         'bonusMultiplier': None,
         'boxTooltipFunc': SetNormalBoxHint,
         'extraHelpLabelPath': 'UI/Sovereignty/MilitaryIndexExplanation',
         'partialValue': sovInfo.militaryIndexRemainder,
         'devIndex': devIndices.get(const.attributeDevIndexMilitary, None)}
        industryInfo = {'indexID': const.attributeDevIndexIndustrial,
         'statusNameText': GetByLabel('UI/Sovereignty/IndustryIndex'),
         'texturePath': 'res:/UI/Texture/classes/Sov/industryIndex.png',
         'currentIndex': sovInfo.industrialIndexLevel,
         'bonusMultiplier': None,
         'boxTooltipFunc': SetNormalBoxHint,
         'extraHelpLabelPath': 'UI/Sovereignty/IndustryIndexExplanation',
         'partialValue': sovInfo.industrialIndexRemainder,
         'devIndex': devIndices.get(const.attributeDevIndexIndustrial, None)}
        return [defenseBonusInfo,
         strategicInfo,
         militaryInfo,
         industryInfo]
