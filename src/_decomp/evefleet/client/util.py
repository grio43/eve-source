#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evefleet\client\util.py
import localization
from carbonui import TextColor
from evefleet import FLEET_FORMATION_SETTING, FLEET_FORMATION_SPACING_SETTING, FLEET_FORMATION_SPACING_SKILL_LEVEL_MAPPING, FLEET_FORMATION_SPACING, FLEET_FORMATION_SIZE_SETTING, FLEET_FORMATION_SIZE, FLEET_FORMATION_SIZE_SKILL_LEVEL_MAPPING, POINT, LOCALIZED_FORMATIONS_SHORT
import evefleet.fleetSetupConst as fsConst

def GetFormationSelected(skillLevel):
    selectedFormationValue = settings.char.ui.Get(FLEET_FORMATION_SETTING, POINT)
    if selectedFormationValue > skillLevel:
        selectedFormationValue = skillLevel
        settings.char.ui.Set(FLEET_FORMATION_SETTING, selectedFormationValue)
    return selectedFormationValue


def GetFormationSpacingSelected(skillLevel):
    selectedFormationSpacingValue = settings.char.ui.Get(FLEET_FORMATION_SPACING_SETTING, FLEET_FORMATION_SPACING[0])
    selectedFormationSpacingSkillLevelRequired = FLEET_FORMATION_SPACING_SKILL_LEVEL_MAPPING.get(selectedFormationSpacingValue, None)
    if selectedFormationSpacingSkillLevelRequired is None or selectedFormationSpacingSkillLevelRequired > skillLevel:
        selectedFormationSpacingValue = FLEET_FORMATION_SPACING[skillLevel]
        settings.char.ui.Set(FLEET_FORMATION_SPACING_SETTING, selectedFormationSpacingValue)
    return selectedFormationSpacingValue


def GetFormationSizeSelected(skillLevel):
    selectedFormationSizeValue = settings.char.ui.Get(FLEET_FORMATION_SIZE_SETTING, FLEET_FORMATION_SIZE[0])
    selectedFormationSizeSkillLevelRequired = FLEET_FORMATION_SIZE_SKILL_LEVEL_MAPPING.get(selectedFormationSizeValue, None)
    if selectedFormationSizeSkillLevelRequired is None or selectedFormationSizeSkillLevelRequired > skillLevel:
        selectedFormationSizeValue = FLEET_FORMATION_SIZE[skillLevel]
        settings.char.ui.Set(FLEET_FORMATION_SIZE_SETTING, selectedFormationSizeValue)
    return selectedFormationSizeValue


def GetSelectedFormationName():
    selectedFormation = settings.char.ui.Get(FLEET_FORMATION_SETTING, POINT)
    return localization.GetByLabel(LOCALIZED_FORMATIONS_SHORT[selectedFormation])


def GetFleetSetupOptionHint(fleetSetup):
    hintList = []
    hintList.append('<b>%s</b>' % fleetSetup[fsConst.FS_NAME])
    motd = fleetSetup.get(fsConst.FS_MOTD, '')
    if motd:
        if len(motd) > 100:
            motd = motd[:100] + '...'
        motd = '<font color="%s">%s</font>' % (TextColor.SECONDARY.hex_argb, motd)
        hintList.append(localization.GetByLabel('UI/Fleet/FleetWindow/Motd', motd=motd))
    isFreeMove = fleetSetup.get(fsConst.FS_IS_FREE_MOVE, None)
    if isFreeMove is None:
        pass
    elif isFreeMove:
        hintList.append(localization.GetByLabel('UI/Fleet/FleetWindow/FreeMoveOn'))
    else:
        hintList.append(localization.GetByLabel('UI/Fleet/FleetWindow/FreeMoveOff'))
    maxFleetSize = fleetSetup.get(fsConst.FS_MAX_SIZE, None)
    if maxFleetSize:
        hintList.append(localization.GetByLabel('UI/Fleet/FleetWindow/MaxFleetSize', fleetSize=maxFleetSize))
    defaultSquad = fleetSetup.get(fsConst.FS_DEFAULT_SQUAD, None)
    if defaultSquad:
        hintList.append(localization.GetByLabel('UI/Fleet/FleetWindow/DefaultSquadSet'))
    wingsInfo = fleetSetup.get(fsConst.FS_WINGS_INFO, {})
    numWings = len(wingsInfo)
    numSquads = 0
    for w in wingsInfo.itervalues():
        numSquads += len(w.get(fsConst.FS_SQUAD_NAMES, []))

    if numWings:
        hintList.append(localization.GetByLabel('UI/Fleet/FleetWindow/NumWings', numWings=numWings))
    if numSquads:
        hintList.append(localization.GetByLabel('UI/Fleet/FleetWindow/NumSquads', numSquads=numSquads))
    return '<br>'.join(hintList)
