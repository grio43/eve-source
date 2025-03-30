#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentPieces\factionalWarfareSystemContentPiece.py
from carbonui.util.bunch import Bunch
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentPieces.baseContentPiece import BaseContentPiece
from eve.client.script.ui.shared.agencyNew.contentPieces.factionalWarfareSiteContentPiece import FactionalWarfareSiteContentPiece
from eve.client.script.ui.shared.agencyNew.ui import agencyUIConst
from eve.common.lib import appConst
from eve.common.script.sys.idCheckers import IsCorporation
from eve.common.script.util.facwarCommon import IsSameFwFaction
from factionwarfare.client.text import GetSystemCaptureStatusText, GetSystemCaptureStatusHint
from fwwarzone.client.dashboard.const import ADJACENCY_TO_LABEL_TEXT, ADJACENCY_TO_LABEL_SYSTEM_TEXT
from fwwarzone.client.util import GetAttackerDefenderColors, GetSystemCaptureStatusColorFromVp
from localization import GetByLabel

class FactionalWarfareSystemContentPiece(BaseContentPiece):
    contentType = agencyConst.CONTENTTYPE_FACTIONALWARFARESYSTEM

    def __init__(self, myFactionID = None, dungeonInstances = None, **kwargs):
        super(FactionalWarfareSystemContentPiece, self).__init__(**kwargs)
        self.facWarSvc = sm.GetService('facwar')
        self.fwVictoryPointSvc = sm.GetService('fwVictoryPointSvc')
        self.fwWarzoneSvc = sm.GetService('fwWarzoneSvc')
        self.myFactionID = myFactionID
        self.contentPieces = self._ConstructFwSiteContentPieces(dungeonInstances)

    def _ConstructFwSiteContentPieces(self, dungeonInstances):
        return filter(None, [ self.ConstructFwSiteContentPiece(site) for site in dungeonInstances ])

    def ConstructFwSiteContentPiece(self, site):
        if self.ownerID != site.factionID:
            return None
        isFriendlySite = IsSameFwFaction(self.myFactionID, site.factionID)
        return FactionalWarfareSiteContentPiece(solarSystemID=self.solarSystemID, ownerID=site.factionID, enemyOwnerID=site.factionID if not isFriendlySite else None, itemID=site.siteID, locationID=site.siteID, site=site, dungeonNameID=site.dungeonNameID, position=site.position, isFriendlySite=isFriendlySite)

    def GetExpandedTitle(self):
        return '%s - %s' % (super(FactionalWarfareSystemContentPiece, self).GetTitle(), self.facWarSvc.GetSystemCaptureStatusTxt(self.solarSystemID))

    def GetExpandedSubtitle(self):
        return GetByLabel('UI/Agency/FacWarSystemLevel', level=self.facWarSvc.GetSolarSystemUpgradeLevel(self.solarSystemID))

    def GetBlurbText(self):
        return GetByLabel('UI/Agency/Blurbs/FactionalWarfareSystem')

    def _GetButtonState(self):
        return agencyUIConst.ACTION_SETDESTINATION

    def GetCardID(self):
        return (self.contentType, self.solarSystemID)

    def GetHint(self):
        text = '<b>%s</b>' % self.GetTitle()
        text += '<br>%s' % GetByLabel('UI/Map/StarModeHandler/militiaSystemStatus', name=cfg.eveowners.Get(self.ownerID).name, status=self.GetSystemStatusText())
        numJumps = self.GetSolarSystemAndSecurityAndNumJumpsText()
        if numJumps:
            text += '<br>%s' % numJumps
        return text

    def GetSystemUpgradeBenefitsForLevel(self, level = None):
        if not level:
            level = self.GetSystemUpgradeLevel()
        return list(self.facWarSvc.GetSystemUpgradeLevelBenefits(level)[:])

    def GetSystemUpgradeLevel(self):
        return self.facWarSvc.GetSolarSystemUpgradeLevel(self.solarSystemID)

    def GetCurrentLPsInSystem(self):
        return self.facWarSvc.GetSolarSystemLPs(self.solarSystemID)

    def GetLPRequiredForNextSystemLevel(self):
        currentLevel = self.GetSystemUpgradeLevel()
        nextLevel = currentLevel + 1 if currentLevel < appConst.facwarSolarSystemMaxLPPool else appConst.facWarSolarSystemMaxLevel
        return appConst.facwarSolarSystemUpgradeThresholds[nextLevel]

    def GetLPRequiredForLastSystemLevel(self):
        currentLevel = self.GetSystemUpgradeLevel()
        return appConst.facwarSolarSystemUpgradeThresholds[currentLevel]

    def GetSystemCaptureStatusHint(self):
        victoryPointState = self.fwVictoryPointSvc.GetVictoryPointState(self.solarSystemID)
        return GetSystemCaptureStatusHint(victoryPointState)

    def GetSystemStatusText(self):
        victoryPointState = self.fwVictoryPointSvc.GetVictoryPointState(self.solarSystemID)
        return GetSystemCaptureStatusText(victoryPointState)

    def GetSystemCaptureStatusColor(self):
        victoryPointState = self.fwVictoryPointSvc.GetVictoryPointState(self.solarSystemID)
        textColor = GetSystemCaptureStatusColorFromVp(victoryPointState)
        return textColor

    def GetAdjacencyText(self, longText = False):
        adjacencyState = self.GetAdjacencyState()
        if adjacencyState:
            if longText:
                labelDict = ADJACENCY_TO_LABEL_SYSTEM_TEXT
            else:
                labelDict = ADJACENCY_TO_LABEL_TEXT
            return labelDict[adjacencyState]
        return ''

    def GetAdjacencyState(self):
        fwOccupationState = self.fwWarzoneSvc.GetOccupationState(self.solarSystemID)
        if fwOccupationState:
            return fwOccupationState.adjacencyState

    def GetAttackerDefenderColors(self):
        return GetAttackerDefenderColors(self.solarSystemID)

    def GetVictoryPoints(self):
        victoryPointState = self.fwVictoryPointSvc.GetVictoryPointState(self.solarSystemID)
        return victoryPointState.score

    def GetCardSortValue(self):
        return (-self.GetVictoryPoints(), self.GetJumpsToSelfFromCurrentLocation())

    def GetOwnerTypeID(self, ownerID):
        if IsCorporation(ownerID):
            return appConst.typeCorporation
        return appConst.typeFaction

    def GetDragData(self):
        dragData = Bunch()
        dragData.__guid__ = 'xtriui.ListSurroundingsBtn'
        dragData.itemID = self.itemID
        dragData.typeID = self.typeID
        dragData.label = cfg.evelocations.Get(self.solarSystemID).name
        return [dragData]

    def GetContestedFraction(self):
        victoryPointState = self.fwVictoryPointSvc.GetVictoryPointState(self.solarSystemID)
        if victoryPointState:
            value = victoryPointState.contestedFraction
        else:
            value = 0.0
        return value
