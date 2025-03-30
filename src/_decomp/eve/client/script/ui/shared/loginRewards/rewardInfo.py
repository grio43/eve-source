#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\loginRewards\rewardInfo.py
import evetypes
from localization import GetByMessageID

class RewardInfo(object):

    def __init__(self, day, reward, claimState, messageID = None, displayNameID = None, iconSize = None, tier = None):
        self.day = day
        self.typeID = reward.typeID
        self.qty = reward.quantity
        self.tier = tier or getattr(reward, 'tier', None)
        self.claimState = claimState
        self.messageID = messageID
        self.texturePath = getattr(reward, 'icon', None)
        self.overlayTexturePath = getattr(reward, 'overlayTexturePath', None)
        self.displayNameID = displayNameID
        self.iconSize = iconSize
        self.blueprintMaterialLevel = getattr(reward, 'blueprintMaterialLevel', None)
        self.blueprintProductivityLevel = getattr(reward, 'blueprintProductivityLevel', None)

    def GetRewardName(self):
        if self.displayNameID:
            return GetByMessageID(self.displayNameID)
        return evetypes.GetName(self.typeID)
