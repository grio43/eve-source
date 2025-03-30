#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\deployment\deploymentContUtil.py
from carbon.common.script.util.linkUtil import GetShowInfoLink
from eve.common.script.sys.idCheckers import IsDockableStructure
from evetypes import IsUpwellStargate
from localization import GetByLabel
from structures.deployment import GetStructureNamePrefix
from utillib import KeyVal
STEP_POSITION = 1
STEP_EXTRA = 2
STEP_SCHEDULE = 3
COLOR_WARNING = '0xBFFF0000'
COLOR_WARNING_FAINT = '0xFFFF5804'
COLOR_VALID = '0xFF73BAFF'

def GetDeploymentStepsLabelPath(structureTypeID):
    if IsUpwellStargate(structureTypeID):
        return 'UI/Structures/Deployment/DeploymentStepsStargate'
    if IsDockableStructure(structureTypeID):
        return 'UI/Structures/Deployment/DeploymentSteps'
    return 'UI/Structures/Deployment/DeploymentStepsNonDockable'


def GetStepsForStructure(structureTypeID):
    if IsUpwellStargate(structureTypeID):
        return [STEP_POSITION, STEP_EXTRA, STEP_SCHEDULE]
    return [STEP_POSITION, STEP_SCHEDULE]


def GetNextState(step, structureTypeID, forward = True):
    if HasExtraStep(structureTypeID):
        if step == STEP_POSITION:
            if forward:
                return STEP_EXTRA
            else:
                return None
        elif step == STEP_EXTRA:
            if forward:
                return STEP_SCHEDULE
            else:
                return STEP_POSITION
        elif step == STEP_SCHEDULE:
            if forward:
                pass
            else:
                return STEP_EXTRA
    elif step == STEP_POSITION:
        if forward:
            return STEP_SCHEDULE
        else:
            return None
    return STEP_POSITION


def HasExtraStep(structureTypeID):
    return IsUpwellStargate(structureTypeID)


ANCHOR_TOOLTIP = 'UI/Structures/Deployment/AnchorHint'
ANCHOR_DISABLED_TOOLTIP = 'UI/Structures/Deployment/AnchorDisabledTooltip'
POSITION_TOOLTIP = 'UI/Structures/Deployment/PositionHint'
POSITION_DISABLED_TOOLTIP = 'UI/Structures/Deployment/PositionDisbabledHint'
CANCEL_TOOLTIP = 'UI/Structures/Deployment/CancelHint'

def GetRightBtnHints(structureTypeID, stepID):
    if stepID == STEP_POSITION:
        return (POSITION_TOOLTIP, POSITION_DISABLED_TOOLTIP)
    if stepID == STEP_EXTRA:
        if IsUpwellStargate(structureTypeID):
            return ('UI/Structures/Deployment/StargateHint', 'UI/Structures/Deployment/StargateDisabledHint')
        return ('', '')
    if stepID == STEP_SCHEDULE:
        return (ANCHOR_TOOLTIP, ANCHOR_DISABLED_TOOLTIP)


def GetRightBtnLabel(structureTypeID, stepID):
    if stepID == STEP_POSITION:
        return 'UI/Structures/Deployment/Position'
    if stepID == STEP_EXTRA:
        if IsUpwellStargate(structureTypeID):
            return 'UI/Structures/Deployment/ConfirmStargateDest'
        return ''
    return ''


def GetLeftBtnHints(stepID):
    if stepID == STEP_POSITION:
        return CANCEL_TOOLTIP
    return 'UI/Structures/Deployment/BackHint'


def GetLeftBtnLabel(stepID):
    if stepID == STEP_POSITION:
        return 'UI/Common/Cancel'
    return 'UI/Commands/Back'


def GetPrefixForDeployment(structureTypeID, destinationSolarsystemID):
    extraConfig = KeyVal(destinationSolarsystemID=destinationSolarsystemID)
    return GetStructureNamePrefix(structureTypeID, session.solarsystemid2, extraConfig)


def GetDestinationText(destinationSolarsystemID):
    if destinationSolarsystemID:
        systemName = cfg.evelocations.Get(destinationSolarsystemID).name
        systemLink = GetShowInfoLink(const.typeSolarSystem, systemName, destinationSolarsystemID)
        stargateDestLabel = GetByLabel('UI/Structures/Deployment/SelectedDestination', systemLink=systemLink)
    else:
        stargateDestLabel = ''
    return stargateDestLabel


def GetPrimeHourLabelPath(structureTypeIDs):
    if structureTypeIDs is None:
        return 'UI/Structures/Deployment/SetPrimeHourHint'
    for eachStructureTypeID in structureTypeIDs:
        if IsDockableStructure(eachStructureTypeID):
            return 'UI/Structures/Deployment/SetPrimeHourHint'

    return 'UI/Structures/Deployment/SetPrimeHourHintNonDockable'


def GetPrimeHourSubtextLabelPath(structureTypeIDs):
    if structureTypeIDs is None:
        return 'UI/Structures/Deployment/SetPrimeHourSubtext'
    for eachStructureTypeID in structureTypeIDs:
        if IsDockableStructure(eachStructureTypeID):
            return 'UI/Structures/Deployment/SetPrimeHourSubtext'

    return 'UI/Structures/Deployment/SetPrimeHourSubtextNonDockable'


def GetHourPickerLabelPath(structureTypeIDs):
    if structureTypeIDs is None:
        return 'UI/Structures/Deployment/SetPrimeHour'
    for eachStructureTypeID in structureTypeIDs:
        if IsDockableStructure(eachStructureTypeID):
            return 'UI/Structures/Deployment/SetPrimeHour'

    return 'UI/Structures/Deployment/SetPrimeHourFLEX'


STRUC_DEPLOY_POINT_HERE = 'pointsToCurrent'
STRUC_DEPLOY_STRUCTURINFO = 'structureInfo'
