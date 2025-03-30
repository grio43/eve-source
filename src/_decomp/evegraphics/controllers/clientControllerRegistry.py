#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\controllers\clientControllerRegistry.py
import evetypes
import uthread2
from eve.common.lib import appConst
import carbon.common.script.util.mathCommon as mathCommon
from carbon.common.lib.const import SEC
import hackingcommon.hackingConstants as hackingConst
from spacecomponents.client.components.decloakEmitter import GetPingIntervalForItem
from tacticalNavigation.ballparkFunctions import GetBallpark, GetBall
from spacecomponents.client.components.activate import GetActivationDurationForItem
from shipcaster.shipcasterConst import SHIPCASTER_SLIM_LINKED_TARGETS_ATTRIBUTE
from gametime import GetSecondsSinceSimTime
from gametime import GetSecondsSinceWallclockTime
from eve.common.script.sys.idCheckers import IsHighSecSystem, IsNewbieSystem
import logging as log

def TwoStatePlusToggleSetup(spaceObject, slimItemValue, stateVariableName, toggleVariableName):
    if slimItemValue:
        spaceObject.SetControllerVariable(stateVariableName, 1)
    else:
        spaceObject.SetControllerVariable(stateVariableName, 0)
    spaceObject.SetControllerVariable(toggleVariableName, slimItemValue > 1)


def GetTwoStatePlusToggleSetup(slimItemAttributeName, stateVariableName, toggleVariableName, defaultSlimItemValue = 0):

    def inner(spaceObject, slimItem):
        slimItemValue = getattr(slimItem, slimItemAttributeName)
        value = slimItemValue if slimItemValue is not None else defaultSlimItemValue
        TwoStatePlusToggleSetup(spaceObject, value, stateVariableName, toggleVariableName)

    return inner


def AlwaysOnSetup(spaceObject, stateVariableName, slimItemValue):
    spaceObject.SetControllerVariable(stateVariableName, slimItemValue)


def GetAlwaysOnSetup(stateVariableName, constantValue):

    def inner(spaceObject, slimItem):
        AlwaysOnSetup(spaceObject, stateVariableName, constantValue)

    return inner


def ToggleSetup(spaceObject, stateVariableName, slimItemValue):
    spaceObject.SetControllerVariable(stateVariableName, bool(slimItemValue))


def GetToggleSetup(slimItemAttributeName, stateVariableName):

    def inner(spaceObject, slimItem):
        slimItemValue = getattr(slimItem, slimItemAttributeName)
        ToggleSetup(spaceObject, stateVariableName, slimItemValue)

    return inner


def StargateSetup(spaceObject, slimItem):
    spaceObject.SetControllerVariable('ActivationState', slimItem.activationState if slimItem.activationState is not None else 2)
    spaceObject.SetControllerVariable('InvasionState', slimItem.poseID if slimItem.poseID is not None else 0)
    corruption, suppression = (0.0, 0.0)
    if session is not None and hasattr(session, 'solarsystemid2'):
        if IsHighSecSystem(session.solarsystemid2):
            spaceObject.SetControllerVariable('enablePropaganda', 1.0)
    if hasattr(slimItem, 'destinationCorruptionStageAndMaximum') and hasattr(slimItem, 'localCorruptionStageAndMaximum'):
        currentDestinationCorruptionStage = float(slimItem.destinationCorruptionStageAndMaximum[0] or 0.0)
        maxDestinationCorruptionStage = float(slimItem.destinationCorruptionStageAndMaximum[1] or 1.0)
        destinationCorruption = currentDestinationCorruptionStage / maxDestinationCorruptionStage
        currentLocalCorruptionStage = float(slimItem.localCorruptionStageAndMaximum[0] or 0.0)
        maxLocalCorruptionStage = float(slimItem.localCorruptionStageAndMaximum[1] or 1.0)
        localCorruption = currentLocalCorruptionStage / maxLocalCorruptionStage
        corruption = max(destinationCorruption, localCorruption)
    if hasattr(slimItem, 'destinationSuppressionStageAndMaximum') and hasattr(slimItem, 'localSuppressionStageAndMaximum'):
        currentDestinationSuppressionStage = float(slimItem.destinationSuppressionStageAndMaximum[0] or 0.0)
        maxDestinationSuppressionStage = float(slimItem.destinationSuppressionStageAndMaximum[1] or 1.0)
        destinationSuppression = currentDestinationSuppressionStage / maxDestinationSuppressionStage
        currentLocalSuppressionStage = float(slimItem.localSuppressionStageAndMaximum[0] or 0.0)
        maxLocalSuppressionStage = float(slimItem.localSuppressionStageAndMaximum[1] or 1.0)
        localSuppression = currentLocalSuppressionStage / maxLocalSuppressionStage
        suppression = max(destinationSuppression, localSuppression)
    spaceObject.SetControllerVariable('corruption', corruption)
    spaceObject.SetControllerVariable('suppression', suppression)
    idSeed = slimItem.itemID if slimItem.itemID is not None else 123
    idSeed = (idSeed << 8) % 1000
    spaceObject.SetControllerVariable('itemIdSeed', float(idSeed))
    spaceObject.SetControllerVariable('isDrifterAffectedGate', float(slimItem.hasVolumetricDrifterCloud or 0.0))


def RefreshEssState(spaceObject, slimItem):
    spaceObject.SetControllerVariable('rbank_lock', slimItem.reserveUnlocked if slimItem.reserveUnlocked is not None else False)
    spaceObject.SetControllerVariable('rbank_count', float(slimItem.reserveLinkCount) if slimItem.reserveLinkCount is not None else 0.0)
    spaceObject.SetControllerVariable('mbank_count', float(slimItem.mainLinkCount) if slimItem.mainLinkCount is not None else 0.0)


def SpewContainerSetup(spaceObject, slimItem):
    spaceObject.SetControllerVariable('SecurityState', slimItem.hackingSecurityState or hackingConst.hackingStateSecure)


def ArkSetup(spaceObject, slimItem, defaultPose):
    poseID = slimItem.poseID or defaultPose
    if poseID == 1:
        spaceObject.SetControllerVariable('worldarc_active', 0.0)
    elif poseID > 1:
        spaceObject.SetControllerVariable('worldarc_active', 1.0)
    if poseID == 3:
        spaceObject.SetControllerVariable('worldArc_GateUse', 1.0)
    else:
        spaceObject.SetControllerVariable('worldArc_GateUse', 0.0)
    if poseID == 4:
        spaceObject.SetControllerVariable('Trig_WorldArcCloak', 0.0)
    else:
        spaceObject.SetControllerVariable('Trig_WorldArcCloak', 1.0)


def GetArkSetup(defaultPose):

    def inner(spaceObject, slimItem):
        return ArkSetup(spaceObject, slimItem, defaultPose=defaultPose)

    return inner


def GetDirectValueFromSlimItemSetup(slimItemAttributeName, stateVariableName, default = 0):

    def do_update(spaceObject, slimItem):
        slimItemValue = getattr(slimItem, slimItemAttributeName) or default
        spaceObject.SetControllerVariable(stateVariableName, slimItemValue)

    return do_update


def DefaultSetup(spaceObject, slimItem):
    spaceObject.SetControllerVariable('ActivationState', slimItem.activationState or 0)


def WormholeSetup(model, slimItem):
    model.SetControllerVariable('WH_State', int(not model.exploded))
    model.SetControllerVariable('WH_Age', slimItem.wormholeAge)
    model.SetControllerVariable('WH_ShipMass', slimItem.maxShipJumpMass)
    mapping = {1.0: 1.0,
     0.7: 2.0,
     0.4: 3.0}
    newSize = mapping[slimItem.wormholeSize]
    model.SetControllerVariable('WH_Size', newSize)
    model.SetControllerVariable('isDestTriglavian', slimItem.isDestTriglavian)


def SunSetup(model, slimItem):
    slimItem.starState = slimItem.starState or 0
    slimItem.starState_Timestamp = slimItem.starState_Timestamp or -1
    _UpdateLensflare(slimItem)
    try:
        model.SetControllerVariable('star_state', slimItem.starState)
    except AttributeError:
        return


def _UpdateLensflare(slimItem):
    sceneManager = sm.GetService('sceneManager')
    lensflare = sceneManager.registeredScenes['default'].lensflares[0]
    if len(lensflare.controllers) < 1:
        return
    timeSinceTransition = 0
    transitionDuration = 30
    if slimItem.starState_Timestamp == -1:
        timeSinceTransition = transitionDuration + 1
    else:
        timeSinceTransition = GetSecondsSinceSimTime(slimItem.starState_Timestamp)
    if timeSinceTransition > transitionDuration:
        lensflare.SetControllerVariable('star_state', slimItem.starState)
        lensflare.StartControllers()
    else:
        lensflare.StartControllers()
        lensflare.SetControllerVariable('star_state', slimItem.starState)


def UpdateDynamicLineSetCircle(model, slimItem):

    def helper(attrTest, default = 0):
        if attrTest is not None:
            return attrTest
        else:
            return default

    model.SetControllerVariable('perimeter_look', helper(slimItem.perimeterLook, appConst.PERIMETER_LOOK_DEFAULT))
    model.SetControllerVariable('perimeter_radius', helper(slimItem.perimeterRadius, 2500))
    model.SetControllerVariable('perimeter_completeness', bool(helper(slimItem.perimeterToggleIsCircle, 1)))


def UpdateDynamicPerimeterBubble(model, slimItem):
    model.SetControllerVariable('bubbleLook', slimItem.bubbleLook or appConst.PERIMETER_LOOK_DEFAULT)
    model.SetControllerVariable('bubbleRadius', slimItem.bubbleRadius or 2500)


def UpdateStellarHarvesterArray(model, slimItem):
    poseID = slimItem.poseID or 0
    SetupLongMaterialization(model, slimItem)
    for each in model.model.effectChildren:
        each.SetControllerVariable('star_state', poseID)

    fxSequencer = sm.GetService('FxSequencer')
    targetID = fxSequencer.GetScene().sunBall.id
    info = {'poseID': poseID,
     'timeAddedToSpace': slimItem.timeAddedToSpace}
    fxSequencer.OnSpecialFX(model.id, None, None, targetID, None, 'effects.SunHarvestingBeam', 0, True, None, graphicInfo=info)


def TheFulcrumSetup(model, slimItem):
    fxSequencer = sm.GetService('FxSequencer')
    targetID = fxSequencer.GetScene().sunBall.id
    info = {'poseID': 3,
     'timeAddedToSpace': slimItem.timeAddedToSpace}
    fxSequencer.OnSpecialFX(model.id, None, None, targetID, None, 'effects.SunHarvestingBeamJove', 0, True, None, graphicInfo=info)


def SetupLongMaterialization(model, slimItem):
    timeAddedToSpace = slimItem.timeAddedToSpace or -1
    lifetime = GetSecondsSinceWallclockTime(timeAddedToSpace)
    model.SetControllerVariable('Trig_MaterializationElapsedTime', lifetime)
    model.SetControllerVariable('Trig_IsMaterialized', 1.0)


def UpdatePVPArena(model, slimItem):
    if slimItem.eventComplete == 1:
        model.SetControllerVariable('eventComplete', 1)
        return
    if slimItem.kill == 1:
        model.SetControllerVariable('explosionOccurred', 1)
        return
    timeAddedToSpace = slimItem.startTime or -1
    timeEventEnds = slimItem.endTime or -1
    arenaDuration = float(timeEventEnds - timeAddedToSpace) / SEC
    lifetime = GetSecondsSinceWallclockTime(timeAddedToSpace)
    remainingTime = arenaDuration - lifetime
    model.SetControllerVariable('duration', int(remainingTime + 1))
    model.SetControllerVariable('totalDuration', +int(arenaDuration))


def StationSetup(model, slimItem):
    activityLevel = getattr(slimItem, 'activityLevel')
    if slimItem.activityLevel is not None:
        model.SetControllerVariable('activityLevel', activityLevel)
    if session is not None and hasattr(session, 'solarsystemid2'):
        if IsHighSecSystem(session.solarsystemid2):
            model.SetControllerVariable('enablePropaganda', 1.0)


def _AsyncFOBSetup(model, slimItem):
    dashboardSvc = sm.GetService('insurgencyCampaignSvc')
    snapshot = dashboardSvc.GetLocalCampaignSnapshot()
    pirateAmbitionModifier = max(0, snapshot.piratePointsRequired - snapshot.antipiratePointsRequired)
    model.SetControllerVariable('ambition', float(pirateAmbitionModifier))
    StationSetup(model, slimItem)


def FOBSetup(model, slimItem):
    uthread2.StartTasklet(_AsyncFOBSetup, model, slimItem)


def DeployableCynoSetup(model, slimItem):
    totalDuration = GetActivationDurationForItem(GetBallpark(), slimItem.itemID) or 120
    if slimItem.component_activate is None:
        return
    if slimItem.component_activate[0] is True:
        elapsedTime = totalDuration + 1
    else:
        activationTime = slimItem.component_activate[1] or -1
        remainingDuration = -GetSecondsSinceWallclockTime(activationTime)
        elapsedTime = max(0, totalDuration - remainingDuration)
    model.SetControllerVariable('IsBuilt', 1)
    model.SetControllerVariable('BuildTotalTime', totalDuration)
    model.SetControllerVariable('BuildElapsedTime', elapsedTime)


def DeployableCynoFieldSetup(model, slimItem):
    if slimItem.activityState is not None:
        model.SetControllerVariable('IsEffectOnline', slimItem.activityState)
    else:
        model.SetControllerVariable('IsEffectOnline', 1)


def VisualProximityEffectSetup(model, slimItem):
    if slimItem.timeAddedToSpace is None:
        log.error('ClientControllerRegistry: VisualProximityEffect missing attribute: timeAddedToSpace. Please add DOGMA attribute: attributeHasLongAnimationWhenAddedToSpaceScene')
        return
    elapsedTime = GetSecondsSinceWallclockTime(slimItem.timeAddedToSpace)
    model.SetControllerVariable('DisplayMe', 1.0)
    if elapsedTime < 5:
        model.SetControllerVariable('DoTransition', 1.0)


def DeployableDecloakDeviceSetup(model, slimItem):
    if slimItem.component_activate is None:
        return
    totalDuration = GetActivationDurationForItem(GetBallpark(), slimItem.itemID)
    built = slimItem.component_activate[0] or False
    model.SetControllerVariable('IsBuilt', True)
    if built:
        nextPingTimestamp = slimItem.component_decloakemitter_nextPing
        model.SetControllerVariable('BuildElapsedTime', totalDuration + 1)
        if nextPingTimestamp:
            pingInterval = GetPingIntervalForItem(GetBallpark(), slimItem.itemID)
            timeRemainingUntilNextPing = max(0, -GetSecondsSinceWallclockTime(nextPingTimestamp))
            model.SetControllerVariable('remainingTime', timeRemainingUntilNextPing)
            model.SetControllerVariable('totalDuration', pingInterval)
    else:
        activationTime = slimItem.component_activate[1]
        remainingTime = min(totalDuration, max(0, -GetSecondsSinceWallclockTime(activationTime)))
        model.SetControllerVariable('BuildTotalTime', totalDuration)
        model.SetControllerVariable('BuildElapsedTime', totalDuration - remainingTime)
        model.SetControllerVariable('remainingTime', -1)
        model.SetControllerVariable('totalDuration', totalDuration)


def NPE_SpaceAnomaly(model, slimItem):
    slimItemValue = getattr(slimItem, 'poseID')
    ToggleSetup(model, 'FU_IsActivated', slimItemValue)
    ToggleSetup(model, 'Trig_IsMaterialized', 0)


def BuiltWerpost(model, slimItem):
    model.SetControllerVariable('Trig_MaterializationDuration', 0)
    model.SetControllerVariable('Trig_IsMaterialized', 1)
    if slimItem.poseID:
        model.SetControllerVariable('TG_ScienceBall_ON', 0)
    else:
        model.SetControllerVariable('TG_ScienceBall_ON', 1)


def ActiveWerpost(model, slimItem):
    model.SetControllerVariable('Trig_MaterializationDuration', 0)
    model.SetControllerVariable('Trig_IsMaterialized', 1)
    if slimItem.poseID:
        model.SetControllerVariable('TG_ScienceBall_ON', 1)
    else:
        model.SetControllerVariable('TG_ScienceBall_ON', 0)


def NonInteractableWormhole(model, slimItem):
    poseID = slimItem.poseID
    model.SetControllerVariable('WH_Age', 0)
    if slimItem.poseID:
        model.SetControllerVariable('WH_State', 1)
    else:
        model.SetControllerVariable('WH_State', 0)
    if slimItem.poseID == 3:
        model.SetControllerVariable('_WH_OnUse', 3)


def StellarHarvesterSetup(model, slimItem):
    poseID = slimItem.poseID
    if poseID is None:
        poseID = _GetStellarHarvesterDefaultPose(slimItem)
    for each in model.model.effectChildren:
        try:
            each.SetControllerVariable('star_state', poseID)
        except AttributeError:
            continue

    fxSequencer = sm.GetService('FxSequencer')
    targetID = fxSequencer.GetScene().sunBall.id
    info = {'poseID': poseID,
     'timeAddedToSpace': slimItem.timeAddedToSpace}
    fxSequencer.OnSpecialFX(model.id, None, None, targetID, None, 'effects.StellarHarvester', 0, True, None, graphicInfo=info)
    slimItem.starState = poseID
    SunSetup(model, slimItem)


def _GetStellarHarvesterDefaultPose(slimItem):
    poseByLocationID = {appConst.typeStellarHarvester: 4,
     appConst.typeStellarHarvester2: 0,
     appConst.typeStellarHarvester3: 0,
     appConst.typeStellarHarvesterStripped: 4}
    return poseByLocationID.get(slimItem.typeID, 0)


def NonInteractableObjectSetup(model, slimItem):
    if slimItem.typeId in appConst.TYPES_DECORATIVE_STATION_FLEET_ASSETS:
        poseID = slimItem.poseID or 0.0
        model.SetControllerVariable('trafficLevel', poseID)


def ShipCasterSetup(model, slimItem):
    newTargetTimings = getattr(slimItem, SHIPCASTER_SLIM_LINKED_TARGETS_ATTRIBUTE, None)
    linkedTargets = sum((1 for _ in (destination for destination in newTargetTimings if destination[0] is not None)))
    model.SetControllerVariable('linkedPylons', linkedTargets)


def _RotateToMoon(sourceBall, moonBall):
    celestialCenter = (moonBall.x, moonBall.y, moonBall.z)
    modelPosition = (sourceBall.x, sourceBall.y, sourceBall.z)
    model = sourceBall.GetModel()
    direction = mathCommon.GetNewQuatToFacePos(modelPosition, model.rotationCurve.value, celestialCenter)
    model.rotationCurve.value = direction


TYPE_ID_MAPPING = {appConst.typeTriglavianLocalConduit: GetAlwaysOnSetup('GateActive', 1),
 appConst.typeTriglavianUnlockedLocalConduit: GetAlwaysOnSetup('GateActive', 1),
 appConst.typeTriglavianUnlockingLocalConduit: GetToggleSetup('poseID', 'GateActive'),
 appConst.typeTriglavianExtractiveSuperNexus: SetupLongMaterialization,
 appConst.typeTriglavianDisintegratorWerpost: SetupLongMaterialization,
 appConst.typeTriglavianDamagedWerpost: SetupLongMaterialization,
 appConst.typeTriglavianDisintegratorWerpostBuilt: BuiltWerpost,
 appConst.typeTriglavianDisintegratorWerpostActive: ActiveWerpost,
 appConst.typeNonInteractableWormhole: NonInteractableWormhole,
 appConst.typeWebifyingFortificationUnit: GetTwoStatePlusToggleSetup('poseID', 'Trig_IsMaterialized', 'TGFU_WEB_ON'),
 appConst.typeECMFortificationUnit: GetTwoStatePlusToggleSetup('poseID', 'Trig_IsMaterialized', 'TGFU_ECM_ON'),
 appConst.typeSmartBombingFortificationUnit: GetTwoStatePlusToggleSetup('poseID', 'Trig_IsMaterialized', 'TGFU_SMARTBOMB_ON'),
 appConst.typeSmartBombingMiniFortificationUnit: GetTwoStatePlusToggleSetup('poseID', 'Trig_IsMaterialized', 'TGFU_SMARTBOMB_ON'),
 appConst.typeSensorDampeningFortificationUnit: GetTwoStatePlusToggleSetup('poseID', 'Trig_IsMaterialized', 'TGFU_DAMP_ON'),
 appConst.typeMicroJumpFieldFortificationUnit: GetTwoStatePlusToggleSetup('poseID', 'Trig_IsMaterialized', 'TGFU_FIELDJUMP_ON'),
 appConst.typeMicroJumpFieldMiniFortificationUnit: GetTwoStatePlusToggleSetup('poseID', 'Trig_IsMaterialized', 'TGFU_FIELDJUMP_ON'),
 appConst.typeNeutingMiniFortificationUnit: GetTwoStatePlusToggleSetup('poseID', 'Trig_IsMaterialized', 'TGFU_FIELDJUMP_ON'),
 appConst.typeECMMiniForticicationUnit: GetTwoStatePlusToggleSetup('poseID', 'Trig_IsMaterialized', 'TGFU_FIELDJUMP_ON'),
 appConst.typeSmallTrigavianRift: GetTwoStatePlusToggleSetup('poseID', 'Trig_Portal_State', 'Trig_Portal_Used'),
 appConst.typeLargeTrigavianRift: GetTwoStatePlusToggleSetup('poseID', 'Trig_Portal_State', 'Trig_Portal_Used'),
 appConst.typeTriglavianArc: GetArkSetup(defaultPose=2),
 appConst.typeTriglavianArcCloaked1: GetArkSetup(defaultPose=4),
 appConst.typeTriglavianArcCloaked2: GetArkSetup(defaultPose=4),
 appConst.typeTriglavianArcCloaked3: GetArkSetup(defaultPose=4),
 appConst.typeTriglavianBoundaryGeodesic140k: GetDirectValueFromSlimItemSetup('poseID', 'TRIG_LockRing_State'),
 appConst.typeTriglavianStellarObservatory: SetupLongMaterialization,
 appConst.typeTriglavianStellarObservatoryDressing: SetupLongMaterialization,
 appConst.typeWeaponOverchargeSubPylon: GetToggleSetup('poseID', 'FU_IsActivated'),
 appConst.typeConcordObservatoryOverchargeUnit: GetToggleSetup('poseID', 'FU_IsActivated'),
 appConst.typePerimeterLights: UpdateDynamicLineSetCircle,
 appConst.typeTriglavianStellarHarvesterPhaseOne: UpdateStellarHarvesterArray,
 appConst.typeTriglavianStellarHarvesterPhaseTwo: SetupLongMaterialization,
 appConst.typeTriglavianStellarHarvesterPhaseThree: SetupLongMaterialization,
 appConst.typeAbyssPVPArenaStructure: UpdatePVPArena,
 appConst.typeDeployableCynosuralBeacon: DeployableCynoSetup,
 appConst.typeDeployableCovertCynosuralBeacon: DeployableCynoSetup,
 appConst.typeDeployedCynosuralField: DeployableCynoFieldSetup,
 appConst.typeDeployedCovertCynosuralField: DeployableCynoFieldSetup,
 appConst.typeVisualProximityEffect: VisualProximityEffectSetup,
 appConst.typeUnidentifiedSpaceAnomaly: NPE_SpaceAnomaly,
 appConst.typeNonInteractableWarpMatrixRift: GetToggleSetup('animationState', 'GateActive'),
 appConst.typeSmugglerConstructionBlock: GetToggleSetup('poseID', 'isLooted'),
 appConst.typeConcordPrisonPerimeter: GetToggleSetup('poseID', 'shieldOn'),
 appConst.typeStellarHarvester: StellarHarvesterSetup,
 appConst.typeStellarHarvester2: StellarHarvesterSetup,
 appConst.typeStellarHarvester3: StellarHarvesterSetup,
 appConst.typeStellarHarvesterStripped: StellarHarvesterSetup,
 appConst.typePerimeterBubble: UpdateDynamicPerimeterBubble,
 appConst.typeStationTheFulcrum: TheFulcrumSetup,
 appConst.typeDeathlessFOBStationAngels: FOBSetup,
 appConst.typeDeathlessFOBStationGuristas: FOBSetup}
GROUP_ID_MAPPING = {appConst.groupStargate: StargateSetup,
 appConst.groupSpewContainer: SpewContainerSetup,
 appConst.groupSpawnContainer: SpewContainerSetup,
 appConst.groupWormhole: WormholeSetup,
 appConst.groupWarpGate: GetToggleSetup('animationState', 'GateActive'),
 appConst.groupSun: SunSetup,
 appConst.groupMobileObservatories: DeployableDecloakDeviceSetup,
 appConst.groupEncounterSurveillanceSystem: RefreshEssState,
 appConst.groupNonInteractableObject: NonInteractableObjectSetup,
 appConst.groupInterstellarShipcaster: ShipCasterSetup}
CATEGORY_ID_MAPPING = {appConst.categoryStation: StationSetup}

def ChangeControllerStateFromSlimItem(typeID, model, slimItem):
    if typeID in TYPE_ID_MAPPING:
        TYPE_ID_MAPPING[typeID](model, slimItem)
        return
    groupID = evetypes.GetGroupID(typeID)
    if groupID in GROUP_ID_MAPPING:
        GROUP_ID_MAPPING[groupID](model, slimItem)
        return
    categoryID = evetypes.GetCategoryID(typeID)
    if categoryID in CATEGORY_ID_MAPPING:
        CATEGORY_ID_MAPPING[categoryID](model, slimItem)
        return
    DefaultSetup(model, slimItem)
