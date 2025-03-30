#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\fitting\fittingTooltipUtils.py
from carbon.common.script.util.logUtil import LogError
from eve.client.script.ui.shared.fittingScreen import BROWSE_MODULES, BROWSE_CHARGES, TAB_CONFIGNAME_SKINS, TAB_CONFIGNAME_BROWSER, TAB_CONFIGNAME_STATS, BROWSE_FITTINGS, BROWSE_HARDWARE, TAB_CONFIGNAME_INVENTORY
from eve.client.script.ui.tooltips.tooltipUtil import SetTooltipHeaderAndDescription, SetTooltipDescription
import localization
tooltipLabelPathDict = {'ActiveDefenses': ('Tooltips/FittingWindow/ActiveDefenses', 'Tooltips/FittingWindow/ActiveDefenses_description'),
 'BrowseSavedFittings': ('Tooltips/FittingWindow/BrowseSavedFittings', None),
 'Calibration': ('Tooltips/FittingWindow/Calibration', 'Tooltips/FittingWindow/Calibration_description'),
 'CargoHold': ('Tooltips/FittingWindow/CargoHold', 'Tooltips/FittingWindow/CargoHold_description'),
 'CollapseSidePane': ('Tooltips/FittingWindow/CollapseSidePane', None),
 'ExpandSidePane': ('Tooltips/FittingWindow/ExpandSidePane', None),
 'CPU': ('Tooltips/FittingWindow/CPU', 'Tooltips/FittingWindow/CPU_description'),
 'DamagePerSecond': ('Tooltips/FittingWindow/DamagePerSecond', 'Tooltips/FittingWindow/DamagePerSecond_description'),
 'DroneBay': ('Tooltips/FittingWindow/DroneBay', 'Tooltips/FittingWindow/DroneBay_description'),
 'DroneBayStructure': ('Tooltips/FittingWindow/DroneBay', None),
 'FighterBay': ('Tooltips/FittingWindow/FighterBay', 'Tooltips/FittingWindow/FighterBay_description'),
 'FighterBayStructure': ('Tooltips/FittingWindow/FighterBay', 'Tooltips/FittingWindow/FighterBayStructure_description'),
 'StructureAmmoHold': ('Tooltips/FittingWindow/StructureAmmoHold', 'Tooltips/FittingWindow/StructureAmmoHold_description'),
 'EffectiveHitPoints': ('Tooltips/FittingWindow/EffectiveHitPoints', 'Tooltips/FittingWindow/EffectiveHitPoints_description'),
 'InertiaModifier': ('Tooltips/FittingWindow/InertiaModifier', 'Tooltips/FittingWindow/InertiaModifier_description'),
 'LauncherHardPointBubbles': ('Tooltips/FittingWindow/LauncherHardPointBubbles', 'Tooltips/FittingWindow/LauncherHardPointBubbles_description'),
 'LauncherIcon': ('Tooltips/FittingWindow/LauncherIcon', None),
 'MaximumVelocity': ('Tooltips/FittingWindow/MaximumVelocity', 'Tooltips/FittingWindow/MaximumVelocity_description'),
 'MaxLockedTargets': ('Tooltips/FittingWindow/MaxLockedTargets', 'Tooltips/FittingWindow/MaxLockedTargets_description'),
 'MaxTargetingRange': ('Tooltips/FittingWindow/MaxTargetingRange', 'Tooltips/FittingWindow/MaxTargetingRange_description'),
 'PowerGrid': ('Tooltips/FittingWindow/PowerGrid', 'Tooltips/FittingWindow/PowerGrid_description'),
 'SaveFitting': ('', 'Tooltips/FittingWindow/SaveFitting'),
 'ScanResolution': ('Tooltips/FittingWindow/ScanResolution', 'Tooltips/FittingWindow/ScanResolution_description'),
 'SensorStrength': ('Tooltips/FittingWindow/SensorStrength', 'Tooltips/FittingWindow/SensorStrength_description'),
 'SignatureRadius': ('Tooltips/FittingWindow/SignatureRadius', 'Tooltips/FittingWindow/SignatureRadius_description'),
 'StripFitting': ('Tooltips/FittingWindow/StripFitting', None),
 'TurretHardPointBubbles': ('Tooltips/FittingWindow/TurretHardPointBubbles', 'Tooltips/FittingWindow/TurretHardPointBubbles_description'),
 'TurretIcon': ('Tooltips/FittingWindow/TurretIcon', None),
 'EmptyHighSlot': ('Tooltips/FittingWindow/EmptyHighSlot', None),
 'EmptyMidSlot': ('Tooltips/FittingWindow/EmptyMidSlot', None),
 'EmptyLowSlot': ('Tooltips/FittingWindow/EmptyLowSlot', None),
 'ResistanceHeaderEM': ('Tooltips/FittingWindow/ResistanceHeaderEM', 'Tooltips/FittingWindow/ResistanceHeaderEM_description'),
 'ResistanceHeaderThermal': ('Tooltips/FittingWindow/ResistanceHeaderThermal', 'Tooltips/FittingWindow/ResistanceHeaderThermal_description'),
 'ResistanceHeaderExplosive': ('Tooltips/FittingWindow/ResistanceHeaderExplosive', 'Tooltips/FittingWindow/ResistanceHeaderExplosive_description'),
 'ResistanceHeaderKinetic': ('Tooltips/FittingWindow/ResistanceHeaderKinetic', 'Tooltips/FittingWindow/ResistanceHeaderKinetic_description'),
 'DamagePerSecondTurrets': ('Tooltips/FittingWindow/DamagePerSecondTurrets', 'Tooltips/FittingWindow/DamagePerSecondTurrets_description'),
 'DamagePerSecondDrones': ('Tooltips/FittingWindow/DamagePerSecondDrones', 'Tooltips/FittingWindow/DamagePerSecondDrones_description'),
 'DamagePerSecondMissiles': ('Tooltips/FittingWindow/DamagePerSecondMissiles', 'Tooltips/FittingWindow/DamagePerSecondMissiles_description'),
 'AlpaStrike': ('Tooltips/FittingWindow/AlphaStrike', 'Tooltips/FittingWindow/AlphaStrike_description'),
 'AlignTime': ('Tooltips/FittingWindow/AlignTime', 'Tooltips/FittingWindow/AlignTime_description'),
 'FuelUsage': ('Tooltips/FittingWindow/FuelUsage', 'Tooltips/FittingWindow/FuelUsage_description'),
 'DroneDps': ('Tooltips/FittingWindow/DamagePerSecondDrones', 'Tooltips/FittingWindow/DamagePerSecondDrones_description'),
 'DroneBandwidth': ('Tooltips/FittingWindow/DroneBandwidth', 'Tooltips/FittingWindow/DroneBandwidth_description'),
 'DroneControlRange': ('Tooltips/FittingWindow/DroneControlRange', 'Tooltips/FittingWindow/DroneControlRange_description'),
 'FitShip': ('', 'Tooltips/FittingWindow/FitShip_description'),
 'BuildFitShip': ('', 'Tooltips/FittingWindow/BuildFitShip_description'),
 TAB_CONFIGNAME_SKINS: ('Tooltips/FittingWindow/SkinTab', 'Tooltips/FittingWindow/SkinTab_description'),
 TAB_CONFIGNAME_BROWSER: ('Tooltips/FittingWindow/BrowserTab', 'Tooltips/FittingWindow/BrowserTab_description'),
 TAB_CONFIGNAME_INVENTORY: ('Tooltips/FittingWindow/InvTab', 'Tooltips/FittingWindow/InvTab_description'),
 TAB_CONFIGNAME_STATS: ('Tooltips/FittingWindow/AttributesTab', 'Tooltips/FittingWindow/AttributesTab_description'),
 '%s_btn' % BROWSE_FITTINGS: ('', 'Tooltips/FittingWindow/ShipFitTab_description'),
 '%s_btn' % BROWSE_HARDWARE: ('', 'Tooltips/FittingWindow/HardwareTab_description'),
 '%s_btn' % BROWSE_MODULES: ('', 'Tooltips/FittingWindow/ModulesTab_description'),
 '%s_btn' % BROWSE_CHARGES: ('', 'Tooltips/FittingWindow/ChargesTab_description')}

def SetFittingTooltipInfo(targetObject, tooltipName, includeDesc = True, extraHeader = None):
    labelPaths = GetTooltipPathFromTooltipName(tooltipName)
    if not labelPaths:
        LogError('no valid labelpath for tooltipName=', tooltipName)
        return
    headerLabelPath, descriptionLabelPath = labelPaths
    if includeDesc and descriptionLabelPath:
        descriptionText = localization.GetByLabel(descriptionLabelPath)
    else:
        descriptionText = ''
    if headerLabelPath:
        headerText = localization.GetByLabel(headerLabelPath)
        if extraHeader:
            headerText = '%s<br>%s' % (headerText, extraHeader)
        return SetTooltipHeaderAndDescription(targetObject, headerText, descriptionText)
    if descriptionText:
        return SetTooltipDescription(targetObject, descriptionText)


def GetTooltipPathFromTooltipName(tooltipName):
    labelPaths = tooltipLabelPathDict.get(tooltipName, None)
    return labelPaths
