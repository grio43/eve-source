#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentPieces\incursionContentPiece.py
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentPieces.baseContentPiece import BaseContentPiece
from eve.client.script.ui.shared.agencyNew.contentPieces.incursionSystemContentPiece import IncursionSystemContentPiece
from eve.client.script.ui.shared.comtool.constants import CHANNEL_INCURSIONS
from eve.client.script.ui.shared.incursions import incursionConst
from eve.common.lib import appConst
from grouprewards import REWARD_TYPE_LP
from localization import GetByLabel
from talecommon.influence import CalculateDecayedInfluence

class IncursionContentPiece(BaseContentPiece):
    contentType = agencyConst.CONTENTTYPE_INCURSIONS

    def __init__(self, incursionData, **kwargs):
        super(IncursionContentPiece, self).__init__(**kwargs)
        self.incursionData = incursionData
        self.state = incursionData.state
        self.constellationID = sm.GetService('map').GetItem(incursionData.stagingSolarSystemID).locationID
        self.influence = incursionData.influence
        self.hasFinalEncounter = incursionData.hasFinalEncounter

    def GetConstellationEffects(self):
        return self.incursionData.effects

    def GetIncursionState(self):
        return self.state

    def GetStateName(self):
        return incursionConst.NAME_BY_INCURSION_STATE[self.state]

    def GetStateHint(self):
        return incursionConst.HINT_BY_INCURSION_STATE[self.state]

    def GetStateColor(self):
        return incursionConst.COLOR_BY_INCURSION_STATE[self.state]

    def GetConstellationID(self):
        return self.constellationID

    def GetConstellationName(self):
        return cfg.evelocations.Get(self.constellationID).locationName

    def GetLPPayoutPool(self):
        rewards = sm.GetService('incursion').GetDelayedRewards(self.incursionData.rewardGroupID)
        if not rewards:
            return
        for reward in rewards:
            if reward.rewardTypeID == REWARD_TYPE_LP:
                return reward.rewardQuantity

    def GetConstellationText(self):
        return GetByLabel('UI/Incursion/Journal/ReportRowHeader', constellation=self.constellationID, constellationInfo=('showinfo', appConst.typeConstellation, self.constellationID))

    def GetInfluence(self):
        return CalculateDecayedInfluence(self.incursionData)

    def HasFinalEncounter(self):
        return self.hasFinalEncounter

    def GetCardID(self):
        return (self.contentType,
         self.solarSystemID,
         self.ownerID,
         self.enemyOwnerID)

    def GetChatChannelID(self):
        return CHANNEL_INCURSIONS

    def GetMenu(self):
        return sm.GetService('menu').GetMenuFromItemIDTypeID(self.solarSystemID, appConst.typeSolarSystem)

    def GetSystemContentPieces(self):
        solarSystemIDs = cfg.mapConstellationCache.Get(self.GetConstellationID()).solarSystemIDs
        sceneTypeBySolarSystemID = self.GetSceneTypeBySolarSystemID()
        contentPieces = [ self.ConstructContentPiece(solarSystemID, sceneTypeBySolarSystemID.get(solarSystemID, None)) for solarSystemID in solarSystemIDs if solarSystemID in sceneTypeBySolarSystemID ]
        return sorted(contentPieces, key=lambda x: x.GetJumpsToSelfFromCurrentLocation())

    def ConstructContentPiece(self, solarSystemID, sceneType):
        return IncursionSystemContentPiece(solarSystemID=solarSystemID, itemID=solarSystemID, sceneType=sceneType, hasFinalEncounter=self.hasFinalEncounter)

    def GetSceneTypeBySolarSystemID(self):
        rows = sm.RemoteSvc('map').GetSystemsInIncursions()
        return {row.locationID:row.sceneType for row in rows}
