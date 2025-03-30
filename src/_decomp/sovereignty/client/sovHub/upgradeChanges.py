#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\client\sovHub\upgradeChanges.py
from inventorycommon.const import typeColonyReagentIce, typeColonyReagentLava
from sovereignty.client.sovHub.hubUtil import GetStartupCostForUpgrades
from sovereignty.upgrades.const import POWER_STATE_OFFLINE

def GetChanges(currentUpgrades, originalUpgrades, getOnline = True):
    oldPowerStates = {x.upgrade_type_id:x.power_state for x in originalUpgrades}
    changesInOnline = []
    newlyAdded = []
    powerStateChanges = []
    for nUpgrade in currentUpgrades:
        nTypeID = nUpgrade.typeID
        oPowerState = oldPowerStates.pop(nTypeID, None)
        if oPowerState is None:
            newlyAdded.append((nTypeID, nUpgrade.powerState))
        else:
            oConfiguredOnline = oPowerState != POWER_STATE_OFFLINE
            if getOnline and oConfiguredOnline != nUpgrade.isConfiguredOnline:
                changesInOnline.append((nTypeID, oConfiguredOnline, nUpgrade.isConfiguredOnline))
            elif nUpgrade.powerState != oPowerState:
                powerStateChanges.append((nTypeID, oPowerState, nUpgrade.powerState))

    return (changesInOnline, newlyAdded, powerStateChanges)


def GetPriorityChanges(currentUpgrades, originalUpgrades):
    afterList = [ x.typeID for x in currentUpgrades ]
    beforeList = [ x.upgrade_type_id for x in originalUpgrades ]
    moved = []
    for i, x in enumerate(afterList):
        if x not in beforeList:
            continue
        idxBefore = beforeList.index(x)
        if i != idxBefore:
            moved.append((x, idxBefore, i))

    return moved


def GetStartupCost(currentUpgrades, originalUpgrades):
    startupCosts = []
    for typeID in [typeColonyReagentLava, typeColonyReagentIce]:
        startupCost = GetStartupCostForUpgrades(currentUpgrades, originalUpgrades, typeID)
        if startupCost:
            startupCosts.append((typeID, startupCost))

    return startupCosts
