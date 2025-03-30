#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentPieces\siteContentPiece.py
import inventorycommon.const as invConst
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentPieces.baseContentPiece import BaseContentPiece
from eve.client.script.ui.shared.agencyNew.ui import agencyUIConst
from eve.client.script.ui.shared.mapView.markers.mapMarkerUtil import GetSiteBracketIcon
from eve.common.lib import appConst
from eve.common.script.sys.eveCfg import IsDocked
from localization import GetByLabel, GetByMessageID
from evedungeons.client.data import GetDungeon

class SiteContentPiece(BaseContentPiece):
    contentType = agencyConst.CONTENTTYPE_SITES

    def __init__(self, site = None, **kwargs):
        BaseContentPiece.__init__(self, **kwargs)
        self.site = site

    def GetName(self):
        return self.GetSiteName()

    def GetSiteNameAndLevel(self):
        return GetByLabel('UI/Agency/SiteNameAndLevel', siteName=self.GetName(), level=self.GetSiteLevel())

    def GetSiteLevel(self):
        return getattr(self.site, 'difficulty', None)

    def GetSiteLevelText(self):
        return GetByLabel('UI/Agency/LevelX', level=self.GetSiteLevel())

    def GetSiteTypeName(self):
        return GetByLabel(agencyConst.SITE_NAMES_BY_ARCHETYPE.get(self.GetSiteArchetype(), 'Unknown Site'))

    def GetSiteArchetype(self):
        return getattr(self.site, 'archetypeID', None)

    def GetSubtitle(self):
        return self.GetSiteNameAndLevel()

    def GetSiteName(self):
        return GetByMessageID(self.site.dungeonNameID)

    def GetSiteDescription(self):
        return GetByMessageID(GetDungeon(self.site.dungeonID).descriptionID)

    def GetSiteGameplayDescription(self):
        return GetByMessageID(GetDungeon(self.site.dungeonID).gameplayDescriptionID)

    def GetSubSolarSystemPosition(self):
        return self.site.position

    def GetMenu(self):
        if IsDocked():
            return
        elif self.GetTargetID():
            scanSvc = sm.GetService('scanSvc')
            return scanSvc.GetScannedDownMenu(self.site)
        else:
            return sm.GetService('menu').GetMenuFromItemIDTypeID(self.solarSystemID, appConst.typeSolarSystem)

    def _ExecutePrimaryFunction(self, actionID):
        if actionID == agencyUIConst.ACTION_WARPTO:
            targetID = self.GetTargetID()
            sm.GetService('menu').WarpToScanResult(targetID)
        else:
            super(SiteContentPiece, self)._ExecutePrimaryFunction(actionID)

    def GetTargetID(self):
        return getattr(self.site, 'targetID', None)

    def GetBlurbText(self):
        if self.GetSiteArchetype() == appConst.dunArchetypeOreAnomaly:
            return GetByLabel('UI/Inflight/Scanner/OreSiteTooltip')
        if self.GetSiteArchetype() == appConst.dunArchetypeGasClouds:
            return GetByLabel('UI/Agency/Blurbs/GasSites')
        if self.GetSiteArchetype() == appConst.dunArchetypeRelicSites:
            return GetByLabel('UI/Inflight/Scanner/RelicSiteTooltip')
        if self.GetSiteArchetype() == appConst.dunArchetypeDataSites:
            return GetByLabel('UI/Inflight/Scanner/DataSiteTooltip')
        if self.GetSiteArchetype() == appConst.dunArchetypeWormhole:
            return GetByLabel('UI/Inflight/Scanner/WormholeTooltip')
        if self.GetSiteArchetype() == appConst.dunArchetypeCombatSites:
            return GetByLabel('UI/Inflight/Scanner/CombatSiteTooltip')
        if self.GetSiteArchetype() == appConst.dunArchetypeIceBelt:
            return GetByLabel('UI/Agency/Blurbs/IceSite')
        if self.GetSiteArchetype() == appConst.dunArchetypeEventSites:
            return GetByLabel('UI/Agency/Blurbs/EventSites')
        if self.GetSiteArchetype() == appConst.dunArchetypeCombatHacking:
            return GetByLabel('UI/Agency/Blurbs/CombatHacking')
        if self.GetSiteArchetype() == appConst.dunArchetypeSitesOfInterest:
            return GetByLabel('UI/Agency/Blurbs/SitesOfInterest')
        if self.GetSiteArchetype() == appConst.dunArchetypeDrifterSites:
            return GetByLabel('UI/Agency/Blurbs/DrifterSites')

    def GetModulesRequiredTypeIDs(self):
        if self.GetSiteArchetype() == appConst.dunArchetypeIceBelt:
            return ({invConst.typeIceMiningLaser, invConst.typeIceHarvester},)
        if self.GetSiteArchetype() == appConst.dunArchetypeOreAnomaly:
            return (invConst.typeMiningLaser,)
        if self.GetSiteArchetype() == appConst.dunArchetypeGasClouds:
            return (invConst.typeGasCloudHarvester,)
        if self.GetSiteArchetype() == appConst.dunArchetypeRelicSites:
            return (invConst.typeRelicAnalyzer,)
        if self.GetSiteArchetype() == appConst.dunArchetypeDataSites:
            return (invConst.typeDataAnalyzer,)
        if self.GetSiteArchetype() == appConst.dunArchetypeWormhole:
            return (invConst.typeCoreScannerProbe, invConst.typeCoreProbeLauncher)
        if self.GetSiteArchetype() == appConst.dunArchetypeCombatHacking:
            return (invConst.typeDataAnalyzer,)

    def GetIconTexturePath(self):
        if self.GetSiteArchetype() == appConst.dunArchetypeOreAnomaly:
            return 'res:/UI/Texture/Classes/Agency/Icons/ContentTypes/OreSite.png'
        if self.GetSiteArchetype() == appConst.dunArchetypeGasClouds:
            return 'res:/UI/Texture/Classes/Agency/Icons/ContentTypes/GasSite.png'
        if self.GetSiteArchetype() == appConst.dunArchetypeRelicSites:
            return 'res:/UI/Texture/Classes/Agency/Icons/ContentTypes/RelicSite.png'
        if self.GetSiteArchetype() == appConst.dunArchetypeDataSites:
            return 'res:/UI/Texture/Classes/Agency/Icons/ContentTypes/DataSite.png'
        if self.GetSiteArchetype() == appConst.dunArchetypeCombatSites:
            return 'res:/UI/Texture/Classes/Agency/Icons/ContentTypes/CombatSite.png'
        if self.GetSiteArchetype() == appConst.dunArchetypeWormhole:
            return 'res:/UI/Texture/Classes/Agency/Icons/ContentTypes/Wormhole.png'
        if self.GetSiteArchetype() == appConst.dunArchetypeIceBelt:
            return 'res:/UI/Texture/Classes/Agency/Icons/ContentTypes/iceSite.png'
        if self.GetSiteArchetype() == appConst.dunArchetypeGhostSites:
            return 'res:/UI/Texture/Classes/Agency/Icons/ContentTypes/ghostSite.png'
        if self.GetSiteArchetype() in appConst.dunArchetypesFactionalWarfare:
            return 'res:/ui/Texture/classes/agency/Icons/ContentTypes/FWSite.png'
        if self.GetSiteArchetype() == appConst.dunArchetypeEventSites:
            return 'res:/UI/Texture/Classes/Agency/Icons/ContentTypes/event.png'
        if self.GetSiteArchetype() in appConst.dunArchetypesIncursionSites:
            return 'res:/UI/Texture/Classes/Agency/Icons/incursions.png'
        if self.GetSiteArchetype() == appConst.dunArchetypeCombatHacking:
            return 'res:/UI/Texture/Classes/Agency/Icons/ContentTypes/DataSite.png'
        if self.GetSiteArchetype() == appConst.dunArchetypeSitesOfInterest:
            return 'res:/UI/Texture/Classes/Agency/Icons/ContentTypes/RelicSite.png'
        if self.GetSiteArchetype() == appConst.dunArchetypeDrifterSites:
            return 'res:/UI/Texture/Classes/Agency/Icons/allContent.png'

    def GetBracketIconTexturePath(self):
        return GetSiteBracketIcon(self.GetSiteArchetype())

    def GetContentSubTypeID(self):
        return self.GetSiteArchetype()
