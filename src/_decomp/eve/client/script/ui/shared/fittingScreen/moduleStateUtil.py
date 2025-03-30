#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\moduleStateUtil.py
from eve.client.script.ui.shared.fittingScreen.fittingUtil import GetDefaultAndOverheatEffectForType
from eve.client.script.ui.shared.fittingScreen import OFFLINE, ONLINE, ACTIVE, OVERHEATED, OFFLINE_COLOR, ONLINE_COLOR, ACTIVE_COLOR, OVERHEATED_COLOR
from inventorycommon.util import IsSubsystemFlag
from localization import GetByLabel
from shipfitting.fittingStuff import IsRigSlot
PASSIVE = 0
ACTIVATABLE = 1
RIG = 2
SUBSYSTEM = 3

def GetCurrentStateForDogmaItemWithEffects(dogmaItem, typeEffectInfo, flagID):
    if IsRigSlot(flagID):
        if typeEffectInfo.defaultEffect.effectID in dogmaItem.activeEffects:
            return ONLINE
        else:
            return OFFLINE
    elif IsPassive(typeEffectInfo):
        if dogmaItem.IsOnline():
            return ONLINE
        else:
            return OFFLINE
    else:
        if not dogmaItem.IsOnline():
            return OFFLINE
        if not dogmaItem.IsActive():
            return ONLINE
        if typeEffectInfo.overloadEffect and typeEffectInfo.overloadEffect.effectID in dogmaItem.activeEffects:
            return OVERHEATED
        return ACTIVE


def IsPassive(typeEffectInfo):
    isPassive = not typeEffectInfo.defaultEffect or not typeEffectInfo.isActivatable
    return isPassive


def GetTextForCurrentStateForDogmaItem(dogmaItem):
    effectsForType = GetDefaultAndOverheatEffectForType(dogmaItem.typeID)
    currentState = GetCurrentStateForDogmaItemWithEffects(dogmaItem, effectsForType, dogmaItem.flagID)
    if IsRigSlot(dogmaItem.flagID):
        moduleType = RIG
    elif IsSubsystemFlag(dogmaItem.flagID):
        moduleType = SUBSYSTEM
        currentState = ONLINE
    elif IsPassive(effectsForType):
        moduleType = PASSIVE
    else:
        moduleType = ACTIVATABLE
    color = COLOR_BY_ACTIVATION_STATE.get(currentState)
    label = activationStateLabels.get((currentState, moduleType))
    return (label, color, currentState)


activationStateLabels = {(OFFLINE, ACTIVATABLE): GetByLabel('UI/Fitting/FittingWindow/ModuleModeOffline'),
 (OFFLINE, PASSIVE): GetByLabel('UI/Fitting/FittingWindow/ModuleModeOfflinePassive'),
 (OFFLINE, RIG): GetByLabel('UI/Fitting/FittingWindow/ModuleModeOfflineRig'),
 (ONLINE, SUBSYSTEM): GetByLabel('UI/Fitting/FittingWindow/ModuleModeOfflineSubsystem'),
 (ONLINE, ACTIVATABLE): GetByLabel('UI/Fitting/FittingWindow/ModuleModeOnline'),
 (ONLINE, PASSIVE): GetByLabel('UI/Fitting/FittingWindow/ModuleModeOnlinePassive'),
 (ONLINE, RIG): GetByLabel('UI/Fitting/FittingWindow/ModuleModeOnlineRig'),
 (ACTIVE, ACTIVATABLE): GetByLabel('UI/Fitting/FittingWindow/ModuleModeActive'),
 (ACTIVE, PASSIVE): GetByLabel('UI/Fitting/FittingWindow/ModuleModeOnlinePassive'),
 (OVERHEATED, ACTIVATABLE): GetByLabel('UI/Fitting/FittingWindow/ModuleModeOverheated')}
COLOR_BY_ACTIVATION_STATE = {OFFLINE: OFFLINE_COLOR[:3] + (1.0,),
 ONLINE: ONLINE_COLOR[:3] + (1.5,),
 ACTIVE: ACTIVE_COLOR[:3] + (1.0,),
 OVERHEATED: OVERHEATED_COLOR[:3] + (1.0,)}
