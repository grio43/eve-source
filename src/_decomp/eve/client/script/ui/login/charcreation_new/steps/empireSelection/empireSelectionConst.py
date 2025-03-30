#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation_new\steps\empireSelection\empireSelectionConst.py
from carbonui.util.color import Color
from eve.common.lib import appConst
SHIP_VIDEO_BY_FACTIONID = {appConst.factionMinmatarRepublic: 'res:/UI/Texture/Classes/CharacterSelection/EmpireSelection/ship_minmatar.webm',
 appConst.factionGallenteFederation: 'res:/UI/Texture/Classes/CharacterSelection/EmpireSelection/ship_gallente.webm',
 appConst.factionAmarrEmpire: 'res:/UI/Texture/Classes/CharacterSelection/EmpireSelection/ship_amarr.webm',
 appConst.factionCaldariState: 'res:/UI/Texture/Classes/CharacterSelection/EmpireSelection/ship_caldari.webm'}
BLURB_BY_FACTIONID = {appConst.factionGallenteFederation: 'UI/CharacterCreation/EmpireSelection/SelectionBlurbGallente',
 appConst.factionCaldariState: 'UI/CharacterCreation/EmpireSelection/SelectionBlurbCaldari',
 appConst.factionMinmatarRepublic: 'UI/CharacterCreation/EmpireSelection/SelectionBlurbMinmatar',
 appConst.factionAmarrEmpire: 'UI/CharacterCreation/EmpireSelection/SelectionBlurbAmarr'}
COLOR_BY_FACTIONID = {appConst.factionMinmatarRepublic: Color.HextoRGBA('#8D615E'),
 appConst.factionGallenteFederation: Color.HextoRGBA('#4C8B8B'),
 appConst.factionAmarrEmpire: Color.HextoRGBA('#98876A'),
 appConst.factionCaldariState: Color.HextoRGBA('#465A65')}
EMPIRE_FACTIONIDS = (appConst.factionGallenteFederation,
 appConst.factionCaldariState,
 appConst.factionMinmatarRepublic,
 appConst.factionAmarrEmpire)
ICON_MILITARY = 'res:/UI/Texture/Classes/CharacterSelection/EmpireSelection/iconSchoolMilitary.png'
ICON_ECONOMY = 'res:/UI/Texture/Classes/CharacterSelection/EmpireSelection/iconSchoolEconomy.png'
ICON_SCIENCE = 'res:/UI/Texture/Classes/CharacterSelection/EmpireSelection/iconSchoolScience.png'
ICONS_BY_SCHOOLID = {appConst.schoolImperialAcademy: ICON_MILITARY,
 appConst.schoolHedionUniversity: ICON_ECONOMY,
 appConst.schoolRoyalAmarrInstitute: ICON_SCIENCE,
 appConst.schoolRepublicMilitarySchool: ICON_MILITARY,
 appConst.schoolRepublicUniversity: ICON_ECONOMY,
 appConst.schoolPatorTechSchool: ICON_SCIENCE,
 appConst.schoolStateWarAcademy: ICON_MILITARY,
 appConst.schoolScienceAndTradeInstitute: ICON_ECONOMY,
 appConst.schoolSchoolOfAppliedKnowledge: ICON_SCIENCE,
 appConst.schoolFederalNavyAcademy: ICON_MILITARY,
 appConst.schoolUniversityOfCaille: ICON_ECONOMY,
 appConst.schoolCenterForAdvancedStudies: ICON_SCIENCE}
MINIMIZE_ANIMATION_DURATION = 0.6
FACTIONSELECT_ANIMATION_DURATION = 0.6
ENTRY_ANIMATION_DURATION = 5.0
