#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\resource\client\reagent_split_production_simulation.py
from sovereignty.resource.client.data_types import HarvestSplitSimulationState, HarvestSplitConfiguration

def get_reagent_split_production_data_at_time(harvest_state_dynamic, harvest_state_static, timestamp):
    timeAtLastSim = harvest_state_dynamic.harvested_timestamp
    timeDiff = timestamp - timeAtLastSim
    numTicks = max(0, int(timeDiff / harvest_state_static.period_bluetime))
    if numTicks <= 0:
        return harvest_state_dynamic
    newHarvestedTimestamp = timeAtLastSim + numTicks * harvest_state_static.period_bluetime
    harvestedInTicks = numTicks * harvest_state_static.amount_per_period
    secureHarvested = int(harvest_state_static.secure_ratio * harvestedInTicks)
    insecureHarvested = harvestedInTicks - secureHarvested
    newSecureAmount = harvest_state_dynamic.secure_amount + secureHarvested
    newInsecureAmount = harvest_state_dynamic.insecure_amount + insecureHarvested
    overflowAmount = 0
    if newSecureAmount > harvest_state_static.secure_capacity:
        overflowAmount += newSecureAmount - harvest_state_static.secure_capacity
        newSecureAmount = harvest_state_static.secure_capacity
    if newInsecureAmount > harvest_state_static.insecure_capacity:
        overflowAmount += newInsecureAmount - harvest_state_static.insecure_capacity
        newInsecureAmount = harvest_state_static.insecure_capacity
    if overflowAmount and newSecureAmount < harvest_state_static.secure_capacity:
        extraAmount = min(overflowAmount, harvest_state_static.secure_capacity - newSecureAmount)
        newSecureAmount += extraAmount
        overflowAmount -= extraAmount
    if overflowAmount and newInsecureAmount < harvest_state_static.insecure_capacity:
        extraAmount = min(overflowAmount, harvest_state_static.insecure_capacity - newInsecureAmount)
        newInsecureAmount += extraAmount
        overflowAmount -= extraAmount
    return HarvestSplitSimulationState(newSecureAmount, newInsecureAmount, newHarvestedTimestamp)


def get_next_split_harvest_time_and_amount(harvest_state_dynamic, harvest_state_static, timestamp):
    currentSimulation = get_reagent_split_production_data_at_time(harvest_state_dynamic, harvest_state_static, timestamp)
    nextHarvestedTimestamp = currentSimulation.harvested_timestamp + harvest_state_static.period_bluetime
    nextSimulation = get_reagent_split_production_data_at_time(harvest_state_dynamic, harvest_state_static, nextHarvestedTimestamp)
    currentAmountTotal = currentSimulation.secure_amount + currentSimulation.insecure_amount
    nextAmountTotal = nextSimulation.secure_amount + nextSimulation.insecure_amount
    totalCapacity = harvest_state_static.secure_capacity + harvest_state_static.insecure_capacity
    nextAmountHarvested = nextAmountTotal - currentAmountTotal
    return (nextSimulation.harvested_timestamp, nextAmountHarvested, nextAmountTotal >= totalCapacity)


def get_next_split_amounts(harvest_state_dynamic, harvest_state_static, timestamp):
    currentSimulation = get_reagent_split_production_data_at_time(harvest_state_dynamic, harvest_state_static, timestamp)
    nextHarvestedTimestamp = currentSimulation.harvested_timestamp + harvest_state_static.period_bluetime
    nextSimulation = get_reagent_split_production_data_at_time(harvest_state_dynamic, harvest_state_static, nextHarvestedTimestamp)
    changeSecured = nextSimulation.secure_amount - currentSimulation.secure_amount
    changeUnsecured = nextSimulation.insecure_amount - currentSimulation.insecure_amount
    return (changeSecured, changeUnsecured)
