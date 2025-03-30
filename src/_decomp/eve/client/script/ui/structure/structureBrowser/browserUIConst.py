#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\structureBrowser\browserUIConst.py
import inventorycommon.const as invConst
OWNER_ANY = 0
OWNER_NPC = 1
OWNER_CORP = 2
OWNER_ALLIANCE = 3
SPECIAL_GROUP_NAVIGATIION_STRUCTURES = -2
UI_SETTING_STRUCTUREBROWSER_SERVICEFILTERS_DISABLED = 'structurebrowser_DisableServiceFilter'
UI_SETTING_STRUCTUREBROWSER_SERVICESETTING = 'structurebrowser_%s'
UI_SETTING_STRUCTUREBROWSER_FILTERS = 'structurebrowser_filters_%s'
UI_SETTING_SKYHOOKBROWSER_FILTERS = 'skyhookbrowser_filters_%s'
ALL_STRUCTURES = -1
STRUCTURES_BY_GROUPS = {const.groupStructureCitadel: ((invConst.typeCitadelAstrahus, [invConst.typeCitadelAstrahus]), (invConst.typeCitadelFortizar, [invConst.typeCitadelFortizar,
                                 invConst.typeCitadelMoreauFortizar,
                                 invConst.typeCitadelDraccousFortizar,
                                 invConst.typeCitadelHorizonFortizar,
                                 invConst.typeCitadelMarginisFortizar,
                                 invConst.typeCitadelPrometheusFortizar]), (invConst.typeCitadelKeepstar, [invConst.typeCitadelKeepstar, invConst.typeCitadelPalatineKeepstar])),
 const.groupStructureIndustrialArray: ((invConst.typeEngineeringComplexRaitaru, [invConst.typeEngineeringComplexRaitaru]), (invConst.typeEngineeringComplexAzbel, [invConst.typeEngineeringComplexAzbel]), (invConst.typeEngineeringComplexSotiyo, [invConst.typeEngineeringComplexSotiyo])),
 const.groupStructureDrillingPlatform: ((invConst.typeRefineryTatara, [invConst.typeRefineryTatara]), (invConst.typeRefineryAthanor, [invConst.typeRefineryAthanor])),
 SPECIAL_GROUP_NAVIGATIION_STRUCTURES: ((invConst.typeUpwellSmallStargate, [invConst.typeUpwellSmallStargate]),
                                        (invConst.typeUpwellCynosuralBeacon, [invConst.typeUpwellCynosuralBeacon]),
                                        (invConst.typeUpwellCynosuralSystemJammer, [invConst.typeUpwellCynosuralSystemJammer]),
                                        (invConst.typeUpwellAutoMoonMiner, [invConst.typeUpwellAutoMoonMiner]))}
SPECIAL_GROUPNAME_PATHS_BY_GROUPID = {SPECIAL_GROUP_NAVIGATIION_STRUCTURES: 'UI/StructureBrowser/NavigationStructures'}
ALL_PROFILES = -1
ALL_SERVICES = -1
IGNORE_RANGE = -1
