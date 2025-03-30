#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\panels\PanelSovConstellation.py
import eveformat.client
import evelink.client
from carbonui.primitives.container import Container
from eve.client.script.ui.control.entries.universe import SystemNameHeader
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveScroll import Scroll
from eve.common.lib import appConst as const
from inventorycommon.const import typeTerritorialClaimUnit
from localization import GetByLabel
from sovDashboard import GetSovStructureInfoByTypeID
from sovDashboard.sovStatusEntries import SovSystemStatusEntry, SovStructureStatusEntry

class PanelSovConstellation(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.constellationID = attributes.constellationID
        self.sovSvc = sm.GetService('sov')
        self.mapSvc = sm.GetService('map')

    def Load(self):
        self.Flush()
        self.scroll = Scroll(name='sovScroll', parent=self, padding=const.defaultPadding)
        systemsList = []
        solarSystemsInConstellation = self.mapSvc.GetLocationChildren(self.constellationID)
        solarSystemsInConstellation.sort(key=lambda x: cfg.evelocations.Get(x).name)
        for solarSystemID in solarSystemsInConstellation:
            systemsList.extend(self.GetSolarSystemInfo(solarSystemID))

        self.scroll.Load(contentList=systemsList)

    def GetSolarSystemInfo(self, solarSystemID):
        contentList = []
        contentList.append(GetFromClass(SystemNameHeader, {'label': self.GetSystemNameText(solarSystemID)}))
        sovStructuresInfo = self.sovSvc.GetSovStructuresInfoForSolarSystem(solarSystemID)
        structureInfosByTypeID = GetSovStructureInfoByTypeID(sovStructuresInfo)
        tcuInfo = structureInfosByTypeID[typeTerritorialClaimUnit]
        isCapital = tcuInfo.get('isCapital', False)
        sovInfo = self.sovSvc.GetSovInfoForSolarsystem(solarSystemID, isCapital)
        multiplierInfo = self.GetMultiplierInfo(sovInfo, isCapital)
        contentList.append(GetFromClass(SovSystemStatusEntry, multiplierInfo))
        if sovStructuresInfo:
            for structureTypeID, structureInfo in structureInfosByTypeID.iteritems():
                if not structureInfo.get('itemID', None):
                    continue
                contentList.append(GetFromClass(SovStructureStatusEntry, {'structureInfo': structureInfo}))

        return contentList

    def GetMultiplierInfo(self, sovInfo, isCapital):
        if isCapital:
            defenseBonusTexture = 'res:/UI/Texture/classes/Sov/bonusShieldCapital16.png'
        else:
            defenseBonusTexture = 'res:/UI/Texture/classes/Sov/bonusShield16.png'
        defenseBonusInfo = {'statusNameText': GetByLabel('UI/Sovereignty/ActivityDefenseMultiplier'),
         'texturePath': defenseBonusTexture,
         'currentIndex': None,
         'bonusMultiplier': sovInfo.defenseMultiplier,
         'extraHelpLabelPath': 'UI/Sovereignty/DefenseBonusExplanation',
         'isCapital': isCapital}
        return defenseBonusInfo

    def GetSystemNameText(self, solarSystemID):
        return u'{security_status} {solar_system_name}'.format(security_status=eveformat.solar_system_security_status(solarSystemID), solar_system_name=evelink.location_link(solarSystemID))
