#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\charsheet\__init__.py
from eve.client.script.ui.plex.textures import PLEX_WINDOW_ICON
from eve.common.lib import appConst
from localization import GetByLabel
import uihighlighting.uniqueNameConst as pConst
PANEL_EXPERTSYSTEMS = 'expertsystems'
PANEL_SHIPSKINS = 'skins'
PANEL_SHIPEMBLEMS = 'emblems'
PANEL_PERSONALIZATION = 'personalization'
PANEL_PLEX = 'pilotlicense'
PANEL_EMPLOYMENT = 'employment'
PANEL_JUMPCLONES = 'jumpclones'
PANEL_KILLRIGHTS = 'killrights'
PANEL_SECURITYSTATUS = 'securitystatus'
PANEL_BIO = 'bio'
PANEL_IMPLANTSBOOTERS = 'myimplants_boosters'
PANEL_ATTRIBUTES = 'myattributes'
PANEL_COMBATLOG = 'mykills'
PANEL_DECORATIONS = 'mydecorations'
PANEL_STANDINGS = 'mystandings'
PANEL_HOME_STATION = 'home_station'
PANEL_CHARACTER = 'character'
PANEL_HISTORY = 'history'
PANEL_INTERACTIONS = 'interactions'
PANEL_SKILLS_HISTORY = 'myskills_skillhistory'
PANEL_INFO = {PANEL_EXPERTSYSTEMS: ('Tooltips/CharacterSheet/ExpertSystems',
                       'res:/ui/Texture/WindowIcons/augmentations.png',
                       'Tooltips/CharacterSheet/ExpertSystems_description',
                       pConst.UNIQUE_NAME_EXPERT_SYSTEMS_TAB),
 PANEL_DECORATIONS: ('Tooltips/CharacterSheet/Decorations', 'res:/ui/Texture/WindowIcons/decorations.png', 'Tooltips/CharacterSheet/Decorations_description', None),
 PANEL_ATTRIBUTES: ('Tooltips/CharacterSheet/Attributes', 'res:/ui/Texture/WindowIcons/attributes.png', 'Tooltips/CharacterSheet/Attributes_description', None),
 PANEL_IMPLANTSBOOTERS: ('Tooltips/CharacterSheet/Augmentations',
                         'res:/ui/Texture/WindowIcons/augmentations.png',
                         'Tooltips/CharacterSheet/Augmentations_description',
                         pConst.UNIQUE_NAME_AUGMENTATIONS_TAB),
 PANEL_JUMPCLONES: ('Tooltips/CharacterSheet/JumpClones',
                    'res:/ui/Texture/WindowIcons/jumpclones.png',
                    'Tooltips/CharacterSheet/JumpClones_description',
                    pConst.UNIQUE_NAME_JUMP_CLONES_TAB),
 PANEL_BIO: ('Tooltips/CharacterSheet/Bio', 'res:/ui/Texture/WindowIcons/biography.png', 'Tooltips/CharacterSheet/Bio_description', None),
 PANEL_EMPLOYMENT: ('Tooltips/CharacterSheet/EmploymentHistory', 'res:/ui/Texture/WindowIcons/employmenthistory.png', 'Tooltips/CharacterSheet/EmploymentHistory_description', None),
 PANEL_STANDINGS: ('Tooltips/CharacterSheet/Standings',
                   'res:/ui/Texture/WindowIcons/personalstandings.png',
                   'Tooltips/CharacterSheet/Standings_description',
                   pConst.UNIQUE_NAME_CHAR_STANDINGS_TAB),
 PANEL_SECURITYSTATUS: ('Tooltips/CharacterSheet/SecurityStatus',
                        'res:/ui/Texture/WindowIcons/securitystatus.png',
                        'Tooltips/CharacterSheet/SecurityStatus_description',
                        pConst.UNIQUE_NAME_SECURITY_STATUS_TAB),
 PANEL_KILLRIGHTS: ('Tooltips/CharacterSheet/KillRights',
                    'res:/ui/Texture/WindowIcons/killrights.png',
                    'Tooltips/CharacterSheet/KillRights_description',
                    pConst.UNIQUE_NAME_SHOW_KILL_RIGHTS_TAB),
 PANEL_COMBATLOG: ('Tooltips/CharacterSheet/CombatLog',
                   'res:/ui/Texture/WindowIcons/combatlog.png',
                   'Tooltips/CharacterSheet/CombatLog_description',
                   pConst.UNIQUE_NAME_COMBAT_LOG_TAB),
 PANEL_PLEX: ('Tooltips/CharacterSheet/PilotLicense',
              PLEX_WINDOW_ICON,
              'Tooltips/CharacterSheet/PilotLicense_description',
              None),
 PANEL_PERSONALIZATION: ('Tooltips/CharacterSheet/Personalisation', None, 'Tooltips/CharacterSheet/Personalisation_description', None),
 PANEL_SHIPEMBLEMS: ('Tooltips/CharacterSheet/ShipEmblems',
                     None,
                     'Tooltips/CharacterSheet/ShipEmblems_description',
                     pConst.UNIQUE_NAME_EMBLEMS_TAB),
 PANEL_SHIPSKINS: ('Tooltips/CharacterSheet/Skins',
                   'res:/ui/Texture/WindowIcons/skins.png',
                   'Tooltips/CharacterSheet/Skins_description',
                   pConst.UNIQUE_NAME_SKINS_TAB),
 PANEL_CHARACTER: ('Tooltips/CharacterSheet/Character', 'res:/ui/Texture/WindowIcons/character.png', None, None),
 PANEL_INTERACTIONS: ('Tooltips/CharacterSheet/Interactions', 'res:/ui/Texture/WindowIcons/interactions.png', None, None),
 PANEL_HISTORY: ('Tooltips/CharacterSheet/History', 'res:/ui/Texture/WindowIcons/history.png', None, None),
 PANEL_SKILLS_HISTORY: ('Tooltips/CharacterSheet/Skills', 'res:/ui/Texture/WindowIcons/skills.png', 'Tooltips/CharacterSheet/History_description', None),
 PANEL_HOME_STATION: ('Tooltips/CharacterSheet/HomeStation',
                      None,
                      'Tooltips/CharacterSheet/HomeStationDescription',
                      pConst.UNIQUE_NAME_CHARSHEET_HOME_TAB)}

def GetPanelName(panelID):
    return GetByLabel(PANEL_INFO.get(panelID)[0])


def GetPanelIcon(panelID):
    return PANEL_INFO.get(panelID)[1]


def GetPanelDescription(panelID):
    label = PANEL_INFO.get(panelID)[2]
    if label:
        return GetByLabel(label)
    else:
        return None


def GetPanelUniqueName(panelID):
    return PANEL_INFO.get(panelID)[3]
