#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\skills\skillConst.py
import eveicon
from eve.common.lib import appConst
import inventorycommon.const as invconst
from localization import GetByLabel
skill_max_level = 5
skill_group_ids = (invconst.groupSpaceshipCommand,
 invconst.groupNavigation,
 invconst.groupEngineering,
 invconst.groupSubsystems,
 invconst.groupArmor,
 invconst.groupShields,
 invconst.groupTargeting,
 invconst.groupGunnery,
 invconst.groupMissiles,
 invconst.groupDrones,
 invconst.groupElectronicSystems,
 invconst.groupScanning,
 invconst.groupRigging,
 invconst.groupSocial,
 invconst.groupLeadership,
 invconst.groupCorporationManagement,
 invconst.groupTrade,
 invconst.groupNeuralEnhancement,
 invconst.groupProduction,
 invconst.groupScience,
 invconst.groupResourceProcessing,
 invconst.groupPlanetManagement,
 invconst.groupStructureManagement,
 invconst.groupSKINSequencing)
ICON_BY_GROUPID = {invconst.groupArmor: 'res:/UI/Texture/Classes/Skills/skillGroups/armor.png',
 invconst.groupCorporationManagement: 'res:/UI/Texture/Classes/Skills/skillGroups/corpMgmt.png',
 invconst.groupDrones: 'res:/UI/Texture/Classes/Skills/skillGroups/drones.png',
 invconst.groupElectronicSystems: 'res:/UI/Texture/Classes/Skills/skillGroups/electronicSystems.png',
 invconst.groupEngineering: 'res:/UI/Texture/Classes/Skills/skillGroups/engineering.png',
 invconst.groupGunnery: 'res:/UI/Texture/Classes/Skills/skillGroups/gunnery.png',
 invconst.groupLeadership: 'res:/UI/Texture/Classes/Skills/skillGroups/fleetSupport.png',
 invconst.groupMissiles: 'res:/UI/Texture/Classes/Skills/skillGroups/missiles.png',
 invconst.groupNavigation: 'res:/UI/Texture/Classes/Skills/skillGroups/navigation.png',
 invconst.groupNeuralEnhancement: 'res:/UI/Texture/Classes/Skills/skillGroups/neuralEnhancement.png',
 invconst.groupPlanetManagement: 'res:/UI/Texture/Classes/Skills/skillGroups/planetMgmt.png',
 invconst.groupProduction: 'res:/UI/Texture/Classes/Skills/skillGroups/production.png',
 invconst.groupSKINSequencing: 'res:/UI/Texture/Classes/Skills/skillGroups/skinSequencing.png',
 invconst.groupResourceProcessing: 'res:/UI/Texture/Classes/Skills/skillGroups/resourceProcessing.png',
 invconst.groupRigging: 'res:/UI/Texture/Classes/Skills/skillGroups/rigging.png',
 invconst.groupScanning: 'res:/UI/Texture/Classes/Skills/skillGroups/scanning.png',
 invconst.groupScience: 'res:/UI/Texture/Classes/Skills/skillGroups/science.png',
 invconst.groupShields: 'res:/UI/Texture/Classes/Skills/skillGroups/shields.png',
 invconst.groupSocial: 'res:/UI/Texture/Classes/Skills/skillGroups/social.png',
 invconst.groupSpaceshipCommand: 'res:/UI/Texture/Classes/Skills/skillGroups/spaceshipCmd.png',
 invconst.groupStructureManagement: 'res:/UI/Texture/Classes/Skills/skillGroups/structureMgmt.png',
 invconst.groupSubsystems: 'res:/UI/Texture/Classes/Skills/skillGroups/subsystems.png',
 invconst.groupTargeting: 'res:/UI/Texture/Classes/Skills/skillGroups/targeting.png',
 invconst.groupTrade: 'res:/UI/Texture/Classes/Skills/skillGroups/trade.png'}
DESCRIPTION_BY_GROUPID = {invconst.groupArmor: GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/skillGroups/descriptionArmor'),
 invconst.groupCorporationManagement: GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/skillGroups/descriptionCorporationManagement'),
 invconst.groupDrones: GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/skillGroups/descriptionDrones'),
 invconst.groupElectronicSystems: GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/skillGroups/descriptionElectronicSystems'),
 invconst.groupEngineering: GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/skillGroups/descriptionEngineering'),
 invconst.groupGunnery: GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/skillGroups/descriptionGunnery'),
 invconst.groupLeadership: GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/skillGroups/descriptionLeadership'),
 invconst.groupMissiles: GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/skillGroups/descriptionMissiles'),
 invconst.groupNavigation: GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/skillGroups/descriptionNavigation'),
 invconst.groupNeuralEnhancement: GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/skillGroups/descriptionNeuralEnhancement'),
 invconst.groupPlanetManagement: GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/skillGroups/descriptionPlanetManagement'),
 invconst.groupProduction: GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/skillGroups/descriptionProduction'),
 invconst.groupSKINSequencing: GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/skillGroups/descriptionSKINSequencing'),
 invconst.groupResourceProcessing: GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/skillGroups/descriptionResourceProcessing'),
 invconst.groupRigging: GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/skillGroups/descriptionRigging'),
 invconst.groupScanning: GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/skillGroups/descriptionScanning'),
 invconst.groupScience: GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/skillGroups/descriptionScience'),
 invconst.groupShields: GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/skillGroups/descriptionShields'),
 invconst.groupSocial: GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/skillGroups/descriptionSocial'),
 invconst.groupSpaceshipCommand: GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/skillGroups/descriptionSpaceshipCommand'),
 invconst.groupStructureManagement: GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/skillGroups/descriptionStructureManagement'),
 invconst.groupSubsystems: GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/skillGroups/descriptionSubsystems'),
 invconst.groupTargeting: GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/skillGroups/descriptionTargeting'),
 invconst.groupTrade: GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/skillGroups/descriptionTrade')}
FILTER_SHOWALL = 'alltrainable'
FILTER_TRAINABLENOW = 'mytrainable'
FILTER_HAVEPREREQUISITS = 'haveprerequisits'
FILTER_INJECTED = 'trained'
FILTER_CERTIFICATES = 'certificates'
ATTRIBUTES_BY_GROUPID = {invconst.groupArmor: (appConst.attributeIntelligence, appConst.attributeMemory),
 invconst.groupCorporationManagement: (appConst.attributeMemory, appConst.attributeCharisma),
 invconst.groupDrones: (appConst.attributeMemory, appConst.attributePerception),
 invconst.groupElectronicSystems: (appConst.attributeIntelligence, appConst.attributeMemory),
 invconst.groupEngineering: (appConst.attributeIntelligence, appConst.attributeMemory),
 invconst.groupGunnery: (appConst.attributePerception, appConst.attributeWillpower),
 invconst.groupLeadership: (appConst.attributeCharisma, appConst.attributeWillpower),
 invconst.groupMissiles: (appConst.attributePerception, appConst.attributeWillpower),
 invconst.groupNavigation: (appConst.attributeIntelligence, appConst.attributePerception),
 invconst.groupNeuralEnhancement: (appConst.attributeIntelligence, appConst.attributeMemory),
 invconst.groupPlanetManagement: (appConst.attributeIntelligence, appConst.attributeMemory),
 invconst.groupProduction: (appConst.attributeMemory, appConst.attributeIntelligence),
 invconst.groupResourceProcessing: (appConst.attributeMemory, appConst.attributeIntelligence),
 invconst.groupRigging: (appConst.attributeIntelligence, appConst.attributeMemory),
 invconst.groupScanning: (appConst.attributeIntelligence, appConst.attributeMemory),
 invconst.groupScience: (appConst.attributeIntelligence, appConst.attributeMemory),
 invconst.groupShields: (appConst.attributeIntelligence, appConst.attributeMemory),
 invconst.groupSocial: (appConst.attributeCharisma, appConst.attributeIntelligence),
 invconst.groupSpaceshipCommand: (appConst.attributePerception, appConst.attributeWillpower),
 invconst.groupStructureManagement: (appConst.attributeMemory, appConst.attributeWillpower),
 invconst.groupSubsystems: (appConst.attributeIntelligence, appConst.attributeMemory),
 invconst.groupTargeting: (appConst.attributeIntelligence, appConst.attributeMemory),
 invconst.groupTrade: (appConst.attributeCharisma, appConst.attributeMemory),
 invconst.groupSKINSequencing: (appConst.attributeCharisma, appConst.attributePerception)}
