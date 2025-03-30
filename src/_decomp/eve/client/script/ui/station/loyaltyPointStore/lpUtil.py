#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\loyaltyPointStore\lpUtil.py
import evetypes
import localization
from eve.common.lib import appConst as const

def GetItemText(typeID, qty, numberOfOffers = 1, checkIsBlueprint = True):
    isBlueprint = False
    if checkIsBlueprint:
        if evetypes.GetCategoryID(typeID) == const.categoryBlueprint:
            isBlueprint = True
    if isBlueprint:
        txt = localization.GetByLabel('UI/LPStore/BlueprintRunsLeft', quantity=numberOfOffers, typeID=typeID, numRuns=qty)
    else:
        txt = localization.GetByLabel('UI/LPStore/RewardItem', quantity=qty * numberOfOffers, rewardItem=typeID)
    return txt
