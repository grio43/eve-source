#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\loginrewards\common\rewardUtils.py
import evetypes
import loginrewards.common.const as loginrewardsConst
from inventorycommon.const import categoryBlueprint
CURRENCY_SKILLPOINTS = 'skillPoints'
CURRENCY_ISK = 'ISK'
EVER_GREEN_SKIN_COLLECTION_CRATES = 349

def GetTierColor(tier):
    return loginrewardsConst.TIER_COLORS.get(tier, None)


def GetTierFanfareVideoPath(tier):
    if tier == loginrewardsConst.TIER2:
        return 'res:/UI/Texture/classes/LoginCampaign/tier_2.webm'
    if tier == loginrewardsConst.TIER3:
        return 'res:/UI/Texture/classes/LoginCampaign/tier_3.webm'
    if tier == loginrewardsConst.TIER4:
        return 'res:/UI/Texture/classes/LoginCampaign/tier_4.webm'
    if tier == loginrewardsConst.TIER5:
        return 'res:/UI/Texture/classes/LoginCampaign/tier_5.webm'
    return 'res:/UI/Texture/classes/LoginCampaign/tier_1.webm'


def GetAnimationTime(tier):
    if tier in (loginrewardsConst.TIER1,
     loginrewardsConst.TIER2,
     loginrewardsConst.TIER3,
     loginrewardsConst.TIER4):
        return 0.3
    return 2


def GetCloneStateVideoPath(isOmegaEntry):
    if isOmegaEntry:
        return 'res:/UI/Texture/classes/LoginCampaign/omega_gold.webm'
    else:
        return 'res:/UI/Texture/classes/LoginCampaign/alpha_white.webm'


def GetTierName(tier, fullName = True):
    if tier == loginrewardsConst.TIER1:
        if fullName:
            return 'UI/LoginRewards/Tier1'
        return 'UI/LoginRewards/Tier1Short'
    if tier == loginrewardsConst.TIER2:
        if fullName:
            return 'UI/LoginRewards/Tier2'
        return 'UI/LoginRewards/Tier2Short'
    if tier == loginrewardsConst.TIER3:
        if fullName:
            return 'UI/LoginRewards/Tier3'
        return 'UI/LoginRewards/Tier3Short'
    if tier == loginrewardsConst.TIER4:
        if fullName:
            return 'UI/LoginRewards/Tier4'
        return 'UI/LoginRewards/Tier4Short'
    if tier == loginrewardsConst.TIER5:
        if fullName:
            return 'UI/LoginRewards/Tier5'
        return 'UI/LoginRewards/Tier5Short'
    if tier == loginrewardsConst.TIER6:
        return None


def GetClaimState(isClaimed, isNextClaimable, somethingCanBeClaimedNow):
    if isClaimed:
        return loginrewardsConst.CLAIM_STATE_CLAIMED
    if isNextClaimable and somethingCanBeClaimedNow:
        return loginrewardsConst.CLAIM_STATE_CLAIMABLE
    return loginrewardsConst.CLAIM_STATE_UNCLAIMED


CURRENCY_COLORS = {CURRENCY_SKILLPOINTS: (0.2, 0.35, 0.45, 1.0),
 CURRENCY_ISK: (0.2, 0.35, 0.45, 1.0)}
BUCKET_TEXTS_BY_CURRENCY = {CURRENCY_SKILLPOINTS: ('UI/LoginRewards/BonusSkillPoints', 'UI/LoginRewards/SPHelpIcon', 'UI/LoginRewards/BonusSkillPointProgress'),
 CURRENCY_ISK: ('UI/LoginRewards/BonusISK', 'UI/LoginRewards/ISKHelpIcon', 'UI/LoginRewards/BonusISKProgress')}

def ShouldShowQty(rewardInfo):
    if evetypes.GetCategoryID(rewardInfo.typeID) == categoryBlueprint:
        return False
    if rewardInfo.qty <= 1:
        return False
    return True
